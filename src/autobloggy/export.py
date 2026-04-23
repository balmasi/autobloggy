from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .artifacts import extract_frontmatter, format_markdown_with_frontmatter, post_paths, read_text, write_text
from .utils import ensure_dir, slugify
from .visual_verifiers import capture_visual_screenshot, run_playwright_command

SUPPORTED_FORMATS = ("html", "qmd", "pdf", "docx")

EMBED_BLOCK_PATTERN = re.compile(
    r"```\{=html\}\s*\n"
    r"<div class=\"autobloggy-visual-embed\"[^>]*>\s*\n"
    r"\s*<iframe\s+[^>]*src=\"(?P<src>[^\"]+)\"[^>]*title=\"(?P<title>[^\"]*)\"[^>]*></iframe>\s*\n"
    r"\s*</div>\s*\n"
    r"```",
    re.MULTILINE,
)


@dataclass(frozen=True)
class EmbedBlock:
    src: str
    title: str
    start: int
    end: int


def find_embed_blocks(draft_text: str) -> list[EmbedBlock]:
    blocks: list[EmbedBlock] = []
    for match in EMBED_BLOCK_PATTERN.finditer(draft_text):
        blocks.append(
            EmbedBlock(
                src=match.group("src"),
                title=match.group("title"),
                start=match.start(),
                end=match.end(),
            )
        )
    return blocks


def swap_embeds_for_images(draft_text: str, png_by_src: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        src = match.group("src")
        title = match.group("title") or "Visual"
        png = png_by_src.get(src)
        if png is None:
            return match.group(0)
        alt = title.replace("]", "").replace("[", "")
        return f"![{alt}]({png})"

    return EMBED_BLOCK_PATTERN.sub(replace, draft_text)


def rasterize_embeds(slug: str, blocks: list[EmbedBlock], output_dir: Path) -> dict[str, str]:
    paths = post_paths(slug)
    ensure_dir(output_dir)
    png_by_src: dict[str, str] = {}
    for index, block in enumerate(blocks, start=1):
        source_html = (paths.root / block.src).resolve()
        if not source_html.exists():
            raise FileNotFoundError(f"Visual HTML referenced in draft does not exist: {source_html}")
        png_name = f"visual-{index:02d}-{slugify(block.title)[:40] or 'visual'}.png"
        png_path = output_dir / png_name
        session = slugify(f"export-{slug}-{index}")
        html_url = source_html.as_uri()
        try:
            run_playwright_command(["--session", session, "open", html_url])
            run_playwright_command(["--session", session, "resize", "1440", "900"])
            run_playwright_command([
                "--session",
                session,
                "run-code",
                "await page.waitForLoadState('load'); await page.waitForTimeout(400)",
            ])
            run_playwright_command([
                "--session",
                session,
                "screenshot",
                "--filename",
                str(png_path),
                "--full-page",
            ])
        finally:
            try:
                run_playwright_command(["--session", session, "close"])
            except Exception:
                pass
        png_by_src[block.src] = png_name
    return png_by_src


def run_quarto(input_path: Path, output_format: str, output_dir: Path) -> Path:
    if shutil.which("quarto") is None:
        raise FileNotFoundError(
            "`quarto` is not on PATH. Run `uv sync` (the `quarto-cli` dependency ships the binary) "
            "and invoke the CLI via `uv run autobloggy ...`, or export to `qmd` to skip rendering."
        )
    ensure_dir(output_dir)
    try:
        subprocess.run(
            [
                "quarto",
                "render",
                str(input_path),
                "--to",
                output_format,
                "--output-dir",
                str(output_dir),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = "\n".join(part for part in [exc.stdout.strip(), exc.stderr.strip()] if part)
        raise RuntimeError(f"quarto render failed:\n{detail}") from exc
    extension = {"html": ".html", "pdf": ".pdf", "docx": ".docx"}[output_format]
    rendered = output_dir / (input_path.stem + extension)
    return rendered


HTML_FORMAT_OPTIONS: dict = {
    "embed-resources": True,
    "toc": True,
    "toc-depth": 3,
    "anchor-sections": True,
    "smooth-scroll": True,
}


def _stage_for_html(draft_text: str) -> str:
    frontmatter, body = extract_frontmatter(draft_text)
    frontmatter["format"] = {"html": HTML_FORMAT_OPTIONS}
    body = PARENT_RESIZE_LISTENER + "\n\n" + body
    return format_markdown_with_frontmatter(frontmatter, body)


def export_post(slug: str, output_format: str) -> dict[str, str]:
    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unknown export format `{output_format}`. Supported: {', '.join(SUPPORTED_FORMATS)}."
        )
    paths = post_paths(slug)
    if not paths.draft.exists():
        raise FileNotFoundError(f"Draft does not exist: {paths.draft}")

    export_root = paths.root / "export" / output_format
    if export_root.exists():
        shutil.rmtree(export_root)
    ensure_dir(export_root)

    draft_text = read_text(paths.draft)

    if output_format == "qmd":
        destination = export_root / "draft.qmd"
        write_text(destination, draft_text)
        return {"format": "qmd", "output": str(destination)}

    if output_format == "html":
        staged = export_root / "draft.qmd"
        blocks = find_embed_blocks(draft_text)
        copied = copy_visuals_with_resize_hook(paths.root, export_root, blocks)
        rewritten = inject_iframe_copies(draft_text, copied)
        rewritten = _stage_for_html(rewritten)
        write_text(staged, rewritten)
        rendered = run_quarto(staged, "html", export_root)
        return {"format": "html", "output": str(rendered)}

    # pdf / docx: rasterize visuals, swap embed blocks for image references,
    # then hand to quarto.
    blocks = find_embed_blocks(draft_text)
    png_by_src = rasterize_embeds(slug, blocks, export_root) if blocks else {}
    staged = export_root / "draft.qmd"
    rewritten = swap_embeds_for_images(draft_text, png_by_src)
    write_text(staged, rewritten)
    rendered = run_quarto(staged, output_format, export_root)
    return {"format": output_format, "output": str(rendered), "rasterized_count": str(len(png_by_src))}


CHILD_RESIZE_SCRIPT = """
<script>
(function () {
  function post() {
    var h = Math.max(
      document.documentElement.scrollHeight,
      document.body ? document.body.scrollHeight : 0
    );
    parent.postMessage({ type: "autobloggy:resize", id: window.name, height: h }, "*");
  }
  window.addEventListener("load", function () {
    post();
    setTimeout(post, 200);
    setTimeout(post, 800);
  });
  window.addEventListener("resize", post);
  if (window.ResizeObserver) {
    new ResizeObserver(post).observe(document.documentElement);
  }
})();
</script>
""".strip()

PARENT_RESIZE_LISTENER = """```{=html}
<script>
window.addEventListener("message", function (e) {
  var d = e.data;
  if (!d || d.type !== "autobloggy:resize") return;
  var frames = document.querySelectorAll("iframe.autobloggy-visual-iframe");
  for (var i = 0; i < frames.length; i++) {
    if (frames[i].contentWindow === e.source) {
      frames[i].style.height = d.height + "px";
      return;
    }
  }
});
</script>
```"""


def _inject_before_body_close(html_text: str, snippet: str) -> str:
    lowered = html_text.lower()
    idx = lowered.rfind("</body>")
    if idx == -1:
        return html_text + "\n" + snippet + "\n"
    return html_text[:idx] + snippet + "\n" + html_text[idx:]


def copy_visuals_with_resize_hook(
    post_root: Path, export_root: Path, blocks: list[EmbedBlock]
) -> dict[str, str]:
    """Copy each referenced visual.html into the export dir with a postMessage
    resize hook injected. Returns {original_src: copied_relative_path}."""
    if not blocks:
        return {}
    copies_dir = export_root / "embedded-visuals"
    ensure_dir(copies_dir)
    mapping: dict[str, str] = {}
    for index, block in enumerate(blocks, start=1):
        source_html = (post_root / block.src).resolve()
        if not source_html.exists():
            raise FileNotFoundError(
                f"Visual HTML referenced in draft does not exist: {source_html}"
            )
        slug_part = slugify(block.title)[:40] or "visual"
        copy_name = f"{index:02d}-{slug_part}.html"
        copy_path = copies_dir / copy_name
        original = source_html.read_text(encoding="utf-8")
        copy_path.write_text(
            _inject_before_body_close(original, CHILD_RESIZE_SCRIPT),
            encoding="utf-8",
        )
        # Also copy sibling assets referenced relatively (images, etc.).
        for sibling in source_html.parent.iterdir():
            if sibling.is_file() and sibling.name != source_html.name:
                target = copies_dir / sibling.name
                if not target.exists():
                    shutil.copy2(sibling, target)
        mapping[block.src] = f"embedded-visuals/{copy_name}"
    return mapping


def inject_iframe_copies(draft_text: str, copied_by_src: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        src = match.group("src")
        title = match.group("title")
        copy_rel = copied_by_src.get(src, src)
        frame_id = "autobloggy-frame-" + slugify(copy_rel)
        return (
            "```{=html}\n"
            f'<div class="autobloggy-visual-embed" style="margin: 2rem 0;">\n'
            f'  <iframe class="autobloggy-visual-iframe" src="{copy_rel}" '
            f'name="{frame_id}" title="{title}" loading="lazy" '
            'style="width: 100%; height: 600px; border: 0; display: block;"></iframe>\n'
            "</div>\n"
            "```"
        )

    return EMBED_BLOCK_PATTERN.sub(replace, draft_text)


def rewrite_iframe_src_for_export(draft_text: str, post_root: Path, export_root: Path) -> str:
    """Rewrite post-relative iframe `src` attributes so they resolve from `export_root`."""

    def replace(match: re.Match[str]) -> str:
        src = match.group("src")
        title = match.group("title")
        absolute = (post_root / src).resolve()
        try:
            relative = absolute.relative_to(export_root.resolve(), walk_up=True)
        except (ValueError, TypeError):
            # Python <3.12 or unrelated paths — fall back to absolute file URI.
            relative = Path(absolute.as_uri())
        return (
            "```{=html}\n"
            f'<div class="autobloggy-visual-embed" style="margin: 2rem 0;">\n'
            f'  <iframe src="{relative}" title="{title}" loading="lazy" '
            'sandbox="allow-scripts allow-same-origin" '
            'onload="try{this.style.height=this.contentDocument.documentElement.scrollHeight+\'px\'}catch(e){}" '
            'style="width: 100%; height: 600px; border: 0;"></iframe>\n'
            "</div>\n"
            "```"
        )

    return EMBED_BLOCK_PATTERN.sub(replace, draft_text)
