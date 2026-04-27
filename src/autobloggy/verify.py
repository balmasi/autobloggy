from __future__ import annotations

import shutil
from pathlib import Path

from .artifacts import post_paths, read_meta, read_text, write_text
from .presets import preset_paths, repo_relative_path
from .utils import ensure_dir, now_iso, repo_root
from .verifiers import marker_summary, run_programmatic, strip_markers


VIEWPORT_WIDTHS = (360, 768, 1280)


def _take_screenshots(draft_html: Path, out_dir: Path) -> list[Path]:
    """Render draft.html via Playwright and write a full-page screenshot per width."""
    from playwright.sync_api import sync_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    url = draft_html.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for width in VIEWPORT_WIDTHS:
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
    rubrics_text: str,
    programmatic_marker_counts: dict[str, int],
    strategy_path: Path,
    outline_path: Path,
    brand_guide_path: Path,
) -> str:
    screenshot_lines = "\n".join(f"  - `{s}`" for s in screenshots) or "  - (none — Playwright not available)"
    programmatic_lines = (
        "\n".join(f"  - `{rule}`: {count}" for rule, count in sorted(programmatic_marker_counts.items()))
        or "  - (none)"
    )
    return (
        f"# Verification pack — {slug} — iteration {iteration}\n\n"
        "You are the autobloggy-verifier sub-agent. Your only job is to read the draft and the screenshots, "
        "then insert `<!-- fb[rule_id]: rationale -->` markers in `draft.html` for any issues you find. "
        "Do NOT edit any prose.\n\n"
        "## Files\n\n"
        f"- Draft: `{draft_path}`\n"
        f"- Strategy: `{strategy_path}`\n"
        f"- Outline: `{outline_path}`\n"
        f"- Brand guide: `{brand_guide_path}`\n"
        f"- Screenshots:\n{screenshot_lines}\n\n"
        "## Rubrics\n\n"
        f"{rubrics_text}\n\n"
        "## Programmatic markers already inserted\n\n"
        f"{programmatic_lines}\n\n"
        "Edit `draft.html` to insert your markers, then return.\n"
    )


def run_verify(slug: str) -> dict[str, str]:
    paths = post_paths(slug)
    if not paths.draft.exists():
        raise FileNotFoundError(f"Draft does not exist: {paths.draft}")

    meta = read_meta(slug)
    preset = preset_paths(meta.preset)

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
        screenshots = _take_screenshots(paths.draft, paths.verify_root)
    except Exception as exc:
        screenshot_error = f"Screenshot capture failed: {exc}. Install playwright browsers via `uv run playwright install chromium`."

    rubrics_path = repo_root() / "prompts" / "verifier_rubrics.md"
    rubrics_text = read_text(rubrics_path) if rubrics_path.exists() else "_(verifier_rubrics.md missing)_"
    pack = _verify_pack(
        slug=slug,
        iteration=int(now_iso().replace("-", "").replace(":", "").replace("T", "")[:14] or 0),
        draft_path=paths.draft,
        screenshots=screenshots,
        rubrics_text=rubrics_text,
        programmatic_marker_counts=counts,
        strategy_path=paths.strategy,
        outline_path=paths.outline,
        brand_guide_path=preset.brand_guide,
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
