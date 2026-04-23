from __future__ import annotations

from pathlib import Path

from autobloggy.export import (
    CHILD_RESIZE_SCRIPT,
    EMBED_BLOCK_PATTERN,
    PARENT_RESIZE_LISTENER,
    _stage_for_html,
    copy_visuals_with_resize_hook,
    find_embed_blocks,
    inject_iframe_copies,
    rewrite_iframe_src_for_export,
    swap_embeds_for_images,
)
from tests.helpers import copy_repo, run_cli_failure


EMBED_SAMPLE = (
    "# Post\n\nSome prose.\n\n"
    "```{=html}\n"
    '<div class="autobloggy-visual-embed" style="margin: 2rem 0;">\n'
    '  <iframe src="visuals/visual-01/attempts/001/visual.html" title="First visual" '
    'loading="lazy" sandbox="allow-scripts allow-same-origin" '
    'style="width: 100%; aspect-ratio: 16 / 9; border: 0;"></iframe>\n'
    "</div>\n"
    "```\n\n"
    "More prose.\n\n"
    "```{=html}\n"
    '<div class="autobloggy-visual-embed" style="margin: 2rem 0;">\n'
    '  <iframe src="visuals/visual-02/attempts/001/visual.html" title="Second" '
    'loading="lazy" sandbox="allow-scripts allow-same-origin" '
    'style="width: 100%; aspect-ratio: 16 / 9; border: 0;"></iframe>\n'
    "</div>\n"
    "```\n"
)


def test_find_embed_blocks_parses_iframe_src_and_title() -> None:
    blocks = find_embed_blocks(EMBED_SAMPLE)
    assert [block.src for block in blocks] == [
        "visuals/visual-01/attempts/001/visual.html",
        "visuals/visual-02/attempts/001/visual.html",
    ]
    assert [block.title for block in blocks] == ["First visual", "Second"]


def test_swap_embeds_for_images_replaces_blocks_with_markdown_images() -> None:
    png_by_src = {
        "visuals/visual-01/attempts/001/visual.html": "visual-01-first-visual.png",
        "visuals/visual-02/attempts/001/visual.html": "visual-02-second.png",
    }
    swapped = swap_embeds_for_images(EMBED_SAMPLE, png_by_src)
    assert "![First visual](visual-01-first-visual.png)" in swapped
    assert "![Second](visual-02-second.png)" in swapped
    assert "<iframe" not in swapped


def test_swap_embeds_for_images_leaves_unmapped_blocks_intact() -> None:
    swapped = swap_embeds_for_images(EMBED_SAMPLE, {})
    assert swapped == EMBED_SAMPLE


def test_rewrite_iframe_src_for_export_produces_relative_paths(tmp_path: Path) -> None:
    post_root = tmp_path / "posts" / "slug"
    export_root = post_root / "export" / "html"
    export_root.mkdir(parents=True)
    (post_root / "visuals" / "visual-01" / "attempts" / "001").mkdir(parents=True)
    visual_file = post_root / "visuals" / "visual-01" / "attempts" / "001" / "visual.html"
    visual_file.write_text("<html></html>", encoding="utf-8")

    rewritten = rewrite_iframe_src_for_export(EMBED_SAMPLE, post_root, export_root)
    assert 'src="../../visuals/visual-01/attempts/001/visual.html"' in rewritten
    # Pattern still matches post-rewrite — structure preserved.
    assert len(EMBED_BLOCK_PATTERN.findall(rewritten)) == 2


def test_copy_visuals_with_resize_hook_injects_postmessage(tmp_path: Path) -> None:
    post_root = tmp_path / "posts" / "slug"
    export_root = post_root / "export" / "html"
    export_root.mkdir(parents=True)
    visual_dir = post_root / "visuals" / "visual-01" / "attempts" / "001"
    visual_dir.mkdir(parents=True)
    visual_path = visual_dir / "visual.html"
    visual_path.write_text("<html><body><p>hi</p></body></html>", encoding="utf-8")

    blocks = find_embed_blocks(EMBED_SAMPLE)
    mapping = copy_visuals_with_resize_hook(post_root, export_root, [blocks[0]])
    copied_rel = mapping[blocks[0].src]
    copied_path = export_root / copied_rel
    assert copied_path.exists()
    contents = copied_path.read_text(encoding="utf-8")
    assert "autobloggy:resize" in contents
    assert CHILD_RESIZE_SCRIPT.split("\n", 1)[0] in contents


def test_inject_iframe_copies_emits_listener_compatible_iframe() -> None:
    mapping = {
        "visuals/visual-01/attempts/001/visual.html": "embedded-visuals/01-first-visual.html",
        "visuals/visual-02/attempts/001/visual.html": "embedded-visuals/02-second.html",
    }
    rewritten = inject_iframe_copies(EMBED_SAMPLE, mapping)
    assert 'class="autobloggy-visual-iframe"' in rewritten
    assert "embedded-visuals/01-first-visual.html" in rewritten
    assert "embedded-visuals/02-second.html" in rewritten
    assert "sandbox" not in rewritten  # dropped so postMessage is unrestricted
    # Parent listener references the same class the iframe carries.
    assert "autobloggy-visual-iframe" in PARENT_RESIZE_LISTENER


def test_stage_for_html_frontmatter_at_start_and_html_options() -> None:
    draft = "---\ntitle: My Post\nformat: gfm\n---\n\n# My Post\n\nBody text.\n"
    staged = _stage_for_html(draft)
    assert staged.startswith("---\n"), "frontmatter must be at byte 0"
    assert "format: gfm" not in staged
    assert "embed-resources: true" in staged
    assert "toc: true" in staged
    # Listener appears after the closing --- of the frontmatter
    fm_end = staged.index("\n---\n", 4) + 5
    assert PARENT_RESIZE_LISTENER in staged[fm_end:]


def test_stage_for_html_no_frontmatter() -> None:
    draft = "# Bare Post\n\nNo frontmatter.\n"
    staged = _stage_for_html(draft)
    assert staged.startswith("---\n")
    assert "embed-resources: true" in staged
    assert PARENT_RESIZE_LISTENER in staged


def test_export_unknown_format_rejected(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)

    result = run_cli_failure(repo, "export", "--slug", "nope", "--format", "bogus")
    assert result.returncode != 0
    assert "bogus" in (result.stdout + result.stderr)


def test_export_qmd_copies_draft_without_rendering(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    from autobloggy.artifacts import post_paths
    from autobloggy.export import export_post

    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)

    slug = "qmd-export"
    paths = post_paths(slug, root=repo)
    paths.root.mkdir(parents=True)
    paths.draft.write_text("# Hello\n\nBody.\n", encoding="utf-8")

    result = export_post(slug, "qmd")
    assert result["format"] == "qmd"
    output = Path(result["output"])
    assert output.exists()
    assert output.read_text(encoding="utf-8") == "# Hello\n\nBody.\n"
    assert output.parent == paths.root / "export" / "qmd"
