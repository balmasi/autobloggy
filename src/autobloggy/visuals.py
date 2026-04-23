from __future__ import annotations

import html
import re
from pathlib import Path

from .artifacts import extract_frontmatter, post_paths, read_json, read_text, text_fingerprint, write_json, write_text
from .prepare import prepare_post_inputs
from .presets import default_preset_name, preset_paths, repo_relative_path
from .utils import ensure_dir, now_iso, repo_root, slugify
from .visual_checks import load_visual_checks_config


VISUAL_MARKER_PATTERN = re.compile(r"<!--\s*visual:\s*(.*?)\s*-->")


def section_heading_for_offset(body: str, offset: int) -> str:
    heading = ""
    for match in re.finditer(r"^##\s+(.+)$", body, flags=re.MULTILINE):
        if match.start() > offset:
            break
        heading = match.group(1).strip()
    return heading


def marker_line_number(body: str, offset: int) -> int:
    return body[:offset].count("\n") + 1


def visual_request_id(index: int, hint: str, section_heading: str) -> str:
    label = slugify(hint or section_heading or f"visual-{index + 1}")[:32]
    suffix = text_fingerprint(
        {
            "index": index,
            "hint": hint.strip(),
            "section_heading": section_heading,
        }
    )[:8]
    return f"visual-{index + 1:02d}-{label}-{suffix}"


def extract_markdown_section(text: str, heading: str, level: int = 2) -> str:
    marker = "#" * level
    match = re.search(
        rf"^{re.escape(marker)}\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^{re.escape(marker)}\s+|\Z)",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if not match:
        return ""
    body = match.group(1).strip()
    if not body:
        return ""
    return f"{marker} {heading}\n\n{body}"


def extract_visual_requests(draft_text: str) -> list[dict[str, object]]:
    _, body = extract_frontmatter(draft_text)
    body = body or draft_text
    requests: list[dict[str, object]] = []

    for index, match in enumerate(VISUAL_MARKER_PATTERN.finditer(body)):
        hint = match.group(1).strip()
        section_heading = section_heading_for_offset(body, match.start())
        visual_id = visual_request_id(index, hint, section_heading)
        requests.append(
            {
                "visual_id": visual_id,
                "marker_index": index,
                "hint": hint,
                "section_heading": section_heading,
                "line_number": marker_line_number(body, match.start()),
            }
        )
    return requests


def strategy_brand_guide(slug: str) -> str:
    paths = post_paths(slug)
    strategy_text = read_text(paths.strategy)
    frontmatter, _ = extract_frontmatter(strategy_text)
    recorded = str(frontmatter.get("preset_brand_guide") or "").strip()
    if recorded:
        return recorded
    preset_name = str(frontmatter.get("preset") or default_preset_name())
    return repo_relative_path(preset_paths(preset_name).brand_guide)


def strategy_visual_identity(slug: str) -> str:
    brand_guide_relative = strategy_brand_guide(slug)
    brand_guide_path = repo_root() / brand_guide_relative
    if not brand_guide_path.exists():
        raise FileNotFoundError(f"Brand guide does not exist: {brand_guide_path}")
    visual_identity = extract_markdown_section(read_text(brand_guide_path), "Visual Identity")
    if not visual_identity:
        raise ValueError(
            "Brand guide "
            f"`{brand_guide_relative}` is missing a `## Visual Identity` section. "
            f"Add one before running `autobloggy prepare-visuals --slug {slug}`."
        )
    return visual_identity


def visual_requirements() -> list[str]:
    config = load_visual_checks_config()
    allowed_hosts = ", ".join(config["allowed_script_src_hosts"])
    widths = ", ".join(f"{width}px" for width in config["verifier_viewport_widths"])
    return [
        "Produce a self-contained HTML document with `<html>`, `<body>`, and inline `<style>`.",
        (
            "Treat responsiveness as a COMPOSITION decision, not a scaling trick. Design mobile-first at 360 px, then enhance upward. "
            f"The layout will be screenshotted and verified at: {widths}. The narrow view must not be a shrunken desktop — it must re-compose. "
            "Before choosing a pattern, confirm it degrades gracefully: wide comparison tables must convert to stacked cards or a key:value list at 360 px; "
            "multi-column grids (3+ columns) must collapse to 1–2 columns; dense charts must simplify (fewer series, or horizontal scroll inside the visual, not the page); "
            "side-by-side diagrams must restack vertically. If the concept cannot survive this recomposition, pick a different visual pattern entirely. "
            "Use fluid units (%, fr, minmax, clamp) and CSS Grid/Flexbox with real breakpoints (`@media (min-width: 600px)` etc.). No fixed pixel widths on the root container. "
            "Include `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">` in `<head>`."
        ),
        "Prevent source-note / footer overlap: when `.frame` uses `aspect-ratio` plus CSS Grid rows, ALWAYS write `grid-template-rows` with `minmax(0, 1fr)` for the content slot — never bare `1fr`. Also add `overflow: hidden` to `.frame` and `overflow: hidden` to the content container (table, card grid, etc.). Bare `1fr` collapses to zero under a fixed aspect-ratio constraint, causing the footer to visually climb into the content area.",
        "Include at least one meaningful non-empty `alt` or `aria-label` for the visual's informational content.",
        f"Use external scripts only from this allowlist: {allowed_hosts}. Prefer no external scripts when possible.",
        "Use only the bundled brand colours and brand font stacks unless the brief explicitly permits preserving a source asset's original styling.",
        "Add a visible caption or source note when the visual makes a factual, sourced, or data-backed claim.",
    ]


def bundled_visual_verifiers() -> dict[str, list[dict[str, object]]]:
    root = repo_root()
    config = load_visual_checks_config()
    grouped: dict[str, list[dict[str, object]]] = {
        "must_have": [],
        "improvement": [],
    }
    for config_key, output_key, must_have in (
        ("must_have_verifiers", "must_have", True),
        ("improvement_verifiers", "improvement", False),
    ):
        for verifier in config[config_key]:
            prompt_path = f"prompts/visual_verifiers/{verifier}.md"
            grouped[output_key].append(
                {
                    "verifier": verifier,
                    "must_have": must_have,
                    "prompt_path": prompt_path,
                    "rubric": read_text(root / prompt_path).strip(),
                }
            )
    return grouped


def post_relative_visual_path(path: Path, slug: str) -> str:
    paths = post_paths(slug)
    return str(path.resolve().relative_to(paths.root.resolve()))


def prepare_visual_requests(slug: str) -> dict[str, str]:
    paths = post_paths(slug)
    if not paths.strategy.exists():
        raise FileNotFoundError(f"Strategy does not exist: {paths.strategy}")
    if not paths.draft.exists():
        raise FileNotFoundError(f"Draft does not exist: {paths.draft}")

    prepare_post_inputs(slug, require_sources=True)

    draft_text = read_text(paths.draft)
    requests = extract_visual_requests(draft_text)
    if not requests:
        raise ValueError(
            f"No visual markers found in posts/{slug}/draft.qmd. Add `<!-- visual: hint -->` comments before running `autobloggy prepare-visuals --slug {slug}`."
        )

    ensure_dir(paths.visuals_root)
    for request in requests:
        visual_root = ensure_dir(paths.visuals_root / str(request["visual_id"]))
        request["visual_root"] = post_relative_visual_path(visual_root, slug)
        request["brief_path"] = post_relative_visual_path(visual_root / "brief.md", slug)
        request["html_path"] = post_relative_visual_path(visual_root / "attempts" / "001" / "visual.html", slug)

    visual_identity = strategy_visual_identity(slug)
    payload = {
        "generated_at": now_iso(),
        "draft": repo_relative_path(paths.draft),
        "strategy": repo_relative_path(paths.strategy),
        "prepared_input": repo_relative_path(paths.prepared_input),
        "input_manifest": repo_relative_path(paths.input_manifest),
        "brand_guide": strategy_brand_guide(slug),
        "visual_identity": visual_identity,
        "visual_requirements": visual_requirements(),
        "visual_verifiers": bundled_visual_verifiers(),
        "requests": requests,
    }
    write_json(paths.visuals_requests, payload)
    return {
        "requests": str(paths.visuals_requests),
        "visual_count": str(len(requests)),
    }


def render_embed_block(html_path: str, title: str) -> str:
    safe_title = html.escape(title or "Visual")
    return "\n".join(
        [
            "```{=html}",
            '<div class="autobloggy-visual-embed" style="margin: 2rem 0;">',
            f'  <iframe src="{html_path}" title="{safe_title}" loading="lazy" sandbox="allow-scripts allow-same-origin" style="width: 100%; height: 600px; border: 0;"></iframe>',
            "</div>",
            "```",
        ]
    )


def embed_visuals(slug: str, selected_visual_ids: list[str] | None = None) -> dict[str, str]:
    paths = post_paths(slug)
    if not paths.visuals_requests.exists():
        raise FileNotFoundError(
            f"Visual requests do not exist: {paths.visuals_requests}. Run `autobloggy prepare-visuals --slug {slug}` first."
        )
    if not paths.draft.exists():
        raise FileNotFoundError(f"Draft does not exist: {paths.draft}")

    payload = read_json(paths.visuals_requests)
    requests = payload.get("requests") or []
    request_map = {str(request["visual_id"]): request for request in requests}
    if selected_visual_ids:
        unknown = sorted(set(selected_visual_ids) - set(request_map))
        if unknown:
            raise ValueError("Unknown visual ids: " + ", ".join(unknown))
        selected_ids = set(selected_visual_ids)
    else:
        selected_ids = set(request_map)

    selected_by_index: dict[int, dict[str, object]] = {}
    for visual_id in selected_ids:
        request = request_map[visual_id]
        html_path = paths.root / str(request["html_path"])
        if not html_path.exists():
            raise FileNotFoundError(
                f"Visual HTML does not exist for `{visual_id}`: {html_path}. Generate the visual before embedding it."
            )
        selected_by_index[int(request["marker_index"])] = request

    draft_text = read_text(paths.draft)
    cursor = -1
    embedded_ids: list[str] = []

    def replace_marker(match: re.Match[str]) -> str:
        nonlocal cursor
        cursor += 1
        request = selected_by_index.get(cursor)
        if request is None:
            return match.group(0)
        embedded_ids.append(str(request["visual_id"]))
        title = str(request.get("hint") or request.get("section_heading") or request["visual_id"])
        return "\n\n" + render_embed_block(str(request["html_path"]), title) + "\n\n"

    rewritten = VISUAL_MARKER_PATTERN.sub(replace_marker, draft_text)
    write_text(paths.draft, rewritten)
    return {
        "draft": str(paths.draft),
        "embedded_count": str(len(embedded_ids)),
    }
