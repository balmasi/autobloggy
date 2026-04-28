import shutil
from pathlib import Path

from .artifacts import post_paths, read_meta, read_text, write_text
from .presets import load_verify_config, resolve_preset
from .utils import ensure_dir, now_iso, repo_root
from .verifiers import marker_summary, run_programmatic, strip_markers


DEFAULT_VIEWPORT_WIDTHS = (360, 768, 1280)


def _viewport_widths(root: Path | None = None) -> tuple[int, ...]:
    configured = load_verify_config(root).get("viewport_widths")
    if configured is None:
        return DEFAULT_VIEWPORT_WIDTHS
    if not isinstance(configured, list) or not configured:
        raise ValueError("verify.viewport_widths must be a non-empty list of positive integers.")

    widths: list[int] = []
    for value in configured:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("verify.viewport_widths must be a non-empty list of positive integers.")
        widths.append(value)
    return tuple(widths)


def _take_screenshots(draft_html: Path, out_dir: Path, viewport_widths: tuple[int, ...]) -> list[Path]:
    """Render draft.html via Playwright and write a full-page screenshot per width."""
    from playwright.sync_api import sync_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    url = draft_html.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for width in viewport_widths:
                context = browser.new_context(viewport={"width": width, "height": 900})
                page = context.new_page()
                page.goto(url, wait_until="load")
                page.wait_for_timeout(300)
                target = out_dir / f"screenshot-{width}.png"
                page.screenshot(path=str(target), full_page=True)
                written.append(target)
                context.close()
        finally:
            browser.close()
    return written


def _verify_pack(
    slug: str,
    iteration: int,
    draft_path: Path,
    screenshots: list[Path],
    quality_criteria_text: str,
    programmatic_marker_counts: dict[str, int],
    blog_brief_path: Path,
    brand_guide_path: Path,
) -> str:
    screenshot_lines = "\n".join(f"  - `{s}`" for s in screenshots) or "  - (none - Playwright not available)"
    programmatic_lines = (
        "\n".join(f"  - `{rule}`: {count}" for rule, count in sorted(programmatic_marker_counts.items()))
        or "  - (none)"
    )
    return (
        f"# Verification pack - {slug} - iteration {iteration}\n\n"
        "You are the autobloggy-verifier sub-agent. Your only job is to read the draft and the screenshots, "
        "then insert `<!-- fb[rule_id]: rationale -->` markers in `draft.html` for any issues you find. "
        "Do NOT edit any prose.\n\n"
        "## Files\n\n"
        f"- Draft: `{draft_path}`\n"
        f"- Blog brief: `{blog_brief_path}`\n"
        f"- Brand guide: `{brand_guide_path}`\n"
        f"- Screenshots:\n{screenshot_lines}\n\n"
        "## Marker instructions\n\n"
        "- Format: `<!-- fb[rule_id]: short rationale -->`\n"
        "- Inline span issue: place the comment immediately after the offending span inside the same parent.\n"
        "- Heading issue: place the comment inside the heading element, just before the closing tag.\n"
        "- Document-level finding without a natural anchor: place it at the top of `<main>`, before the first child.\n"
        "- Visual issue: place the comment next to the offending visual node (`<svg>`, `<canvas>`, `<img>`, `<figure>`).\n"
        "- Use one marker per offense. Do not stack duplicates on the same span.\n"
        "- Use `needs_visual` when a section needs an inline visual. Use `document` for whole-document findings without a natural anchor.\n\n"
        "## Programmatic rules\n\n"
        "These have already been inserted by Python before this pack was built. Do not re-mark the same offenses.\n\n"
        "| `rule_id` | What it flags |\n"
        "|-----------|---------------|\n"
        "| `one_h1` | More than one H1 inside `<main>`. |\n"
        "| `heading_order` | Heading level jumps by more than one. |\n"
        "| `code_fences_tagged` | `<pre><code>` blocks missing a `language-*` class. |\n"
        "| `image_caption_alt` | `<img>` missing meaningful `alt`, or `<figure>` missing `<figcaption>`. |\n\n"
        "## Quality criteria\n\n"
        f"{quality_criteria_text}\n\n"
        "## Programmatic markers already inserted\n\n"
        f"{programmatic_lines}\n\n"
        "Edit `draft.html` to insert your markers, then return.\n"
    )


def run_verify(slug: str) -> dict[str, str]:
    paths = post_paths(slug)
    if not paths.draft.exists():
        raise FileNotFoundError(f"Draft does not exist: {paths.draft}")

    meta = read_meta(slug)
    resolved_preset = resolve_preset(meta.preset, meta.selections, paths.root)

    if paths.verify_root.exists():
        shutil.rmtree(paths.verify_root)
    ensure_dir(paths.verify_root)

    draft_html = read_text(paths.draft)
    cleaned = strip_markers(draft_html)
    marked, _inserted = run_programmatic(cleaned)
    write_text(paths.draft, marked)

    counts = marker_summary(marked)

    screenshots: list[Path] = []
    screenshot_error: str | None = None
    try:
        screenshots = _take_screenshots(paths.draft, paths.verify_root, _viewport_widths(paths.root))
    except Exception as exc:
        screenshot_error = f"Screenshot capture failed: {exc}. Install playwright browsers via `uv run playwright install chromium`."

    quality_path = repo_root() / "prompts" / "quality_criteria.md"
    quality_text = read_text(quality_path) if quality_path.exists() else "_(quality_criteria.md missing)_"
    brand_guide = resolved_preset.resources.get("brand")
    brand_guide_path = brand_guide.path if brand_guide else repo_root()
    pack = _verify_pack(
        slug=slug,
        iteration=int(now_iso().replace("-", "").replace(":", "").replace("T", "")[:14] or 0),
        draft_path=paths.draft,
        screenshots=screenshots,
        quality_criteria_text=quality_text,
        programmatic_marker_counts=counts,
        blog_brief_path=paths.blog_brief,
        brand_guide_path=brand_guide_path,
    )
    if screenshot_error:
        pack += f"\n> Note: {screenshot_error}\n"
    write_text(paths.verify_pack, pack)

    total = sum(counts.values())
    payload = {
        "draft": str(paths.draft),
        "verify_pack": str(paths.verify_pack),
        "marker_count": str(total),
    }
    for rule, count in sorted(counts.items()):
        payload[f"marker:{rule}"] = str(count)
    return payload
