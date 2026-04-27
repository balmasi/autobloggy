#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html.parser
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


IGNORED_TAGS = {"code", "pre", "script", "style", "svg", "noscript"}


@dataclass
class Finding:
    line: int
    rule: str
    match: str
    excerpt: str


@dataclass
class Pattern:
    text: str
    is_regex: bool = False


class VisibleTextParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_stack: list[str] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in IGNORED_TAGS:
            self._ignored_stack.append(tag.lower())

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._ignored_stack and self._ignored_stack[-1] == tag:
            self._ignored_stack.pop()

    def handle_data(self, data: str) -> None:
        if not self._ignored_stack:
            self.parts.append(data)


def unquote_yaml_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return bytes(value[1:-1], "utf-8").decode("unicode_escape")
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def parse_pattern(value: str) -> Pattern:
    value = unquote_yaml_value(value)
    if value.startswith("re:"):
        return Pattern(value[3:], is_regex=True)
    return Pattern(value)


def load_patterns() -> dict[str, list[Pattern]]:
    path = Path(__file__).with_name("patterns.yaml")
    patterns: dict[str, list[Pattern]] = {}
    section: str | None = None
    active_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if not raw_line.startswith(" ") and line.endswith(":"):
            section = line[:-1]
            active_key = None
            if section != "patterns":
                raise ValueError(f"Unknown pattern section: {section}")
            continue
        if section != "patterns":
            raise ValueError(f"Pattern must be inside patterns section: {raw_line}")
        if line.startswith("- "):
            if active_key is None:
                raise ValueError(f"List pattern has no active key: {raw_line}")
            patterns[active_key].append(parse_pattern(line[2:]))
            continue
        if ":" not in line:
            raise ValueError(f"Invalid patterns.yaml line: {raw_line}")
        key, value = line.split(":", 1)
        active_key = key.strip()
        value = value.strip()
        patterns[active_key] = [parse_pattern(value)] if value else []
    return patterns


def visible_text(text: str, source: Path | None) -> str:
    if source and source.suffix.lower() in {".html", ".htm"}:
        parser = VisibleTextParser()
        parser.feed(text)
        return "\n".join(parser.parts)
    return text


def paragraphs(text: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    start_line: int | None = None
    current: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.strip():
            if start_line is None:
                start_line = line_number
            current.append(line.strip())
            continue
        if current and start_line is not None:
            blocks.append((start_line, " ".join(current)))
        start_line = None
        current = []
    if current and start_line is not None:
        blocks.append((start_line, " ".join(current)))
    return blocks


def regex_matches(text: str, pattern: str) -> list[str]:
    return [match.group(0) for match in re.finditer(pattern, text, flags=re.IGNORECASE | re.DOTALL)]


def literal_matches(text: str, pattern: str) -> list[str]:
    escaped = re.escape(pattern)
    return [match.group(0) for match in re.finditer(rf"(?<!\w){escaped}(?!\w)", text, flags=re.IGNORECASE)]


def pattern_matches(text: str, pattern: Pattern) -> list[str]:
    if pattern.is_regex:
        return regex_matches(text, pattern.text)
    return literal_matches(text, pattern.text)


def excerpt(text: str, matched: str) -> str:
    clean = " ".join(text.strip().split())
    if len(clean) <= 180:
        return clean
    lower = clean.lower()
    index = lower.find(matched.lower())
    if index < 0:
        return clean[:177] + "..."
    start = max(0, index - 70)
    end = min(len(clean), index + len(matched) + 90)
    prefix = "..." if start else ""
    suffix = "..." if end < len(clean) else ""
    return prefix + clean[start:end] + suffix


def detect(text: str) -> list[Finding]:
    patterns = load_patterns()
    findings: list[Finding] = []

    for line_number, paragraph in paragraphs(text):
        for rule_id, pattern_list in patterns.items():
            for pattern in pattern_list:
                for matched in pattern_matches(paragraph, pattern):
                    findings.append(Finding(line_number, rule_id, matched, excerpt(paragraph, matched)))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect high-signal AI-slop patterns in prose.")
    parser.add_argument("path", nargs="?", help="Text/Markdown/HTML file. Reads stdin when omitted.")
    parser.add_argument("--json", action="store_true", help="Emit JSON findings.")
    args = parser.parse_args()

    source = Path(args.path) if args.path else None
    raw = source.read_text(encoding="utf-8") if source else sys.stdin.read()
    text = visible_text(raw, source)
    findings = detect(text)

    if args.json:
        print(json.dumps([asdict(finding) for finding in findings], indent=2))
    else:
        if not findings:
            print("No scripted slop patterns found.")
        for finding in findings:
            location = "document" if finding.line == 0 else f"line {finding.line}"
            print(f"{location}: {finding.rule}: {finding.match}")
            print(f"  {finding.excerpt}")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
