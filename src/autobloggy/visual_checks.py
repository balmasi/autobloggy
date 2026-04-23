from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from .artifacts import read_text
from .models import CheckResult, CheckSummary
from .presets import load_repo_config
from .utils import now_iso


DEFAULT_VISUAL_MUST_HAVE_VERIFIERS = [
    "visual_relevance",
    "alt_text_quality",
    "text_visual_alignment",
    "source_attribution",
]

DEFAULT_VISUAL_IMPROVEMENT_VERIFIERS = [
    "brand_consistency",
    "composition_clarity",
]

DEFAULT_ALLOWED_SCRIPT_SRC_HOSTS = [
    "cdn.jsdelivr.net",
    "unpkg.com",
    "cdnjs.cloudflare.com",
]

GENERIC_FONT_FAMILIES = {
    "serif",
    "sans-serif",
    "monospace",
    "cursive",
    "fantasy",
    "system-ui",
    "ui-sans-serif",
    "ui-serif",
    "ui-monospace",
    "emoji",
    "math",
    "fangsong",
}

HEX_PATTERN = re.compile(r"#[0-9a-fA-F]{6}\b")


class VisualHTMLInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []
        self.script_srcs: list[str] = []
        self.has_alt = False
        self.has_aria_label = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_name = tag.lower()
        self.tags.append(tag_name)
        attr_map = {str(key).lower(): (value or "") for key, value in attrs}
        if attr_map.get("alt", "").strip():
            self.has_alt = True
        if attr_map.get("aria-label", "").strip():
            self.has_aria_label = True
        if tag_name == "script":
            src = attr_map.get("src", "").strip()
            if src:
                self.script_srcs.append(src)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def load_visual_checks_config(root: Path | None = None) -> dict[str, list[str]]:
    raw = load_repo_config(root).get("visual_checks") or {}
    widths_raw = raw.get("verifier_viewport_widths")
    if widths_raw:
        widths = [int(width) for width in widths_raw]
    else:
        widths = [360, 820]
    return {
        "must_have_verifiers": list(raw.get("must_have_verifiers") or DEFAULT_VISUAL_MUST_HAVE_VERIFIERS),
        "improvement_verifiers": list(raw.get("improvement_verifiers") or DEFAULT_VISUAL_IMPROVEMENT_VERIFIERS),
        "allowed_script_src_hosts": list(raw.get("allowed_script_src_hosts") or DEFAULT_ALLOWED_SCRIPT_SRC_HOSTS),
        "verifier_viewport_widths": widths,
    }


def normalize_hex(value: str) -> str:
    return value.strip().lower()


def extract_brand_hex_colours(visual_identity: str) -> set[str]:
    return {normalize_hex(match) for match in HEX_PATTERN.findall(visual_identity)}


def extract_brand_font_families(visual_identity: str) -> set[str]:
    families: set[str] = set()
    for candidate in re.findall(r"`([^`]+)`", visual_identity):
        lowered = candidate.lower()
        if candidate.startswith("--"):
            continue
        if "," not in candidate and not any(keyword in lowered for keyword in GENERIC_FONT_FAMILIES):
            continue
        for family in candidate.split(","):
            cleaned = family.strip().strip("\"'").strip()
            if not cleaned:
                continue
            if cleaned.lower() in GENERIC_FONT_FAMILIES:
                continue
            families.add(cleaned)
    return families


def extract_html_hex_colours(html_text: str) -> set[str]:
    return {normalize_hex(match) for match in HEX_PATTERN.findall(html_text)}


def extract_html_font_families(html_text: str) -> set[str]:
    families: set[str] = set()
    for candidate in re.findall(r"(?:font-family|--font-[a-z0-9-]+)\s*:\s*([^;}{]+)", html_text, flags=re.IGNORECASE):
        for family in candidate.split(","):
            cleaned = family.strip().strip("\"'").strip()
            if not cleaned or cleaned.startswith("var(") or cleaned.startswith("--"):
                continue
            if cleaned.lower() in GENERIC_FONT_FAMILIES:
                continue
            families.add(cleaned)
    return families


def unknown_script_origins(script_srcs: list[str], allowed_hosts: list[str]) -> list[str]:
    allowed = {host.lower() for host in allowed_hosts}
    unknown: list[str] = []
    for script_src in script_srcs:
        parsed = urlparse(script_src)
        if not parsed.scheme and not parsed.netloc:
            continue
        host = parsed.netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        if host in allowed:
            continue
        unknown.append(script_src)
    return unknown


def run_visual_checks(html_path: Path, visual_identity: str) -> CheckSummary:
    html_text = read_text(html_path)
    inspector = VisualHTMLInspector()
    parser_error = ""
    try:
        inspector.feed(html_text)
        inspector.close()
    except Exception as exc:  # pragma: no cover - HTMLParser rarely raises, but this keeps failures visible.
        parser_error = str(exc)

    tags = set(inspector.tags)
    config = load_visual_checks_config()
    allowed_colours = extract_brand_hex_colours(visual_identity)
    allowed_fonts = extract_brand_font_families(visual_identity)
    unknown_colours = sorted(extract_html_hex_colours(html_text) - allowed_colours)
    unknown_fonts = sorted(extract_html_font_families(html_text) - allowed_fonts)
    unknown_scripts = unknown_script_origins(inspector.script_srcs, config["allowed_script_src_hosts"])

    results = [
        CheckResult(
            id="html_shell",
            passed=not parser_error and {"html", "body"}.issubset(tags) and "<style" in html_text.lower(),
            details=(
                "Visual HTML must be a self-contained document with `<html>`, `<body>`, and inline `<style>`."
                if not parser_error
                else f"HTML parser failed: {parser_error}"
            ),
        ),
        CheckResult(
            id="accessible_label",
            passed=inspector.has_alt or inspector.has_aria_label,
            details="Visual HTML needs at least one non-empty `alt` or `aria-label`.",
        ),
        CheckResult(
            id="script_origin_allowlist",
            passed=not unknown_scripts,
            details="Unknown script origins: " + (", ".join(unknown_scripts) or "none") + ".",
        ),
        CheckResult(
            id="brand_colours_only",
            passed=not unknown_colours,
            details="Colours outside the active brand guide: " + (", ".join(unknown_colours) or "none") + ".",
        ),
        CheckResult(
            id="brand_fonts_only",
            passed=not unknown_fonts,
            details="Fonts outside the active brand guide: " + (", ".join(unknown_fonts) or "none") + ".",
        ),
    ]

    blocker_count = sum(1 for result in results if not result.passed and result.severity == "blocker")
    return CheckSummary(
        target=str(html_path),
        generated_at=now_iso(),
        results=results,
        blocker_count=blocker_count,
        readability_penalty=0,
        banned_pattern_count=0,
    )
