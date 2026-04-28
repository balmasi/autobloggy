#!/usr/bin/env python3
"""Convert a document to Markdown with extracted images and optional VLM captions.

Usage:
    uv run --with 'docling' python convert.py INPUT --output OUTPUT.md [--caption]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable


IMAGE_LINE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<url>[^)]+)\)")

DEFAULT_PROMPT = (
    "Describe the image in 2-3 sentences. Be concise, accurate, and specific. "
    "Note any text, diagrams, charts, screenshots, or notable visual elements. "
    "Do not speculate beyond what is visible."
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="Path or URL to the source document.")
    p.add_argument("--output", "-o", required=True, help="Output markdown file path.")
    p.add_argument(
        "--caption",
        action="store_true",
        help="Run a local VLM over each image and inject a description.",
    )
    p.add_argument(
        "--caption-model",
        choices=("smolvlm", "granite"),
        default="smolvlm",
        help="Local VLM preset for captioning. Default: smolvlm.",
    )
    p.add_argument(
        "--caption-prompt",
        default=DEFAULT_PROMPT,
        help="Prompt sent to the VLM for each image.",
    )
    p.add_argument(
        "--no-images",
        action="store_true",
        help="Drop images entirely; produce text-only markdown.",
    )
    p.add_argument(
        "--ocr",
        action="store_true",
        help="Force OCR on PDFs (slower; needed for scanned PDFs).",
    )
    p.add_argument("--max-pages", type=int, help="Limit conversion to the first N pages.")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args(argv)


def convert(
    input_path: str,
    output_path: str | Path,
    *,
    caption: bool = False,
    caption_model: str = "smolvlm",
    caption_prompt: str = DEFAULT_PROMPT,
    include_images: bool = True,
    ocr: bool = False,
    max_pages: int | None = None,
    verbose: bool = False,
) -> Path:
    """Convert `input_path` to Markdown at `output_path`. Returns the output Path."""

    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling_core.types.doc import ImageRefMode
    from docling_core.types.doc.document import ContentLayer

    is_pptx = Path(str(input_path)).suffix.lower() == ".pptx"
    if caption and is_pptx:
        print("[docling-convert] --caption is PDF-only; ignoring for pptx", file=sys.stderr)
        caption = False
    notes_layers = {ContentLayer.BODY, ContentLayer.FURNITURE, ContentLayer.NOTES}

    pdf_opts = PdfPipelineOptions()
    pdf_opts.do_ocr = ocr
    pdf_opts.do_table_structure = True
    pdf_opts.images_scale = 2.0
    pdf_opts.generate_picture_images = include_images
    _configure_accelerator(pdf_opts, verbose=verbose)

    if caption and include_images:
        if caption_model == "smolvlm":
            from docling.datamodel.pipeline_options import smolvlm_picture_description as preset
        elif caption_model == "granite":
            from docling.datamodel.pipeline_options import granite_picture_description as preset
        else:
            raise ValueError(f"Unknown caption model: {caption_model}")
        pdf_opts.do_picture_description = True
        pdf_opts.picture_description_options = preset
        pdf_opts.picture_description_options.prompt = caption_prompt

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_opts)},
    )

    convert_kwargs: dict = {}
    if max_pages:
        convert_kwargs["max_num_pages"] = max_pages

    if verbose:
        print(f"[docling-convert] converting {input_path}", file=sys.stderr)

    result = converter.convert(input_path, **convert_kwargs)
    doc = result.document

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if include_images:
        artifacts_dir = out.parent / f"{out.stem}_images"
        doc.save_as_markdown(
            out,
            image_mode=ImageRefMode.REFERENCED,
            artifacts_dir=artifacts_dir,
            included_content_layers=notes_layers,
        )
        if is_pptx:
            md = _render_pptx_per_slide(doc, artifacts_dir, notes_layers)
        else:
            md = out.read_text()
            # docling writes absolute paths; rewrite to paths relative to the .md file
            for prefix in {str(artifacts_dir), str(artifacts_dir.resolve()), str(artifacts_dir.absolute())}:
                md = md.replace(prefix, artifacts_dir.name)
    else:
        md = doc.export_to_markdown(
            image_mode=ImageRefMode.PLACEHOLDER,
            included_content_layers=notes_layers,
        )
        out.write_text(md)
        artifacts_dir = None

    if caption and include_images:
        captions = [_picture_description(p) for p in doc.pictures]
        md, dropped_urls = _inject_captions(md, captions, drop_uncaptioned=True)
        _prune_orphans(out.parent, dropped_urls, verbose=verbose)

    if include_images:
        out.write_text(md)

    if verbose:
        print(f"[docling-convert] wrote {out}", file=sys.stderr)
        if artifacts_dir is not None:
            print(f"[docling-convert] images at {artifacts_dir}", file=sys.stderr)

    return out


def _configure_accelerator(pipeline_options, *, verbose: bool = False) -> None:
    """Pick the fastest available device: MPS on Apple Silicon, CUDA on NVIDIA, else CPU."""
    try:
        from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
    except ImportError:
        try:
            from docling.datamodel.pipeline_options import AcceleratorDevice, AcceleratorOptions
        except ImportError:
            return  # docling too old; fall back to library default

    device = AcceleratorDevice.CPU
    try:
        import torch
        if torch.backends.mps.is_available():
            device = AcceleratorDevice.MPS
        elif torch.cuda.is_available():
            device = AcceleratorDevice.CUDA
    except Exception:
        pass

    pipeline_options.accelerator_options = AcceleratorOptions(device=device)
    if verbose:
        print(f"[docling-convert] accelerator: {device.value}", file=sys.stderr)


def _render_pptx_per_slide(doc, artifacts_dir: Path, layers) -> str:
    """Render pptx as `## Slide N` sections with body, images, and speaker notes.

    Picture order in `doc.iterate_items()` matches the order docling writes
    `image_NNNNNN_*.png` files into `artifacts_dir`.
    """
    from docling_core.types.doc.document import ContentLayer

    image_files = sorted(artifacts_dir.glob("image_*"))
    pic_idx = 0
    parts: list[str] = []
    n_slides = len(doc.pages) if doc.pages else 0

    for slide_no in range(1, n_slides + 1):
        body: list[str] = []
        notes: list[str] = []
        for item, _ in doc.iterate_items(page_no=slide_no, included_content_layers=layers):
            label = getattr(item, "label", None)
            if str(label) == "DocItemLabel.PICTURE" or label == "picture":
                if pic_idx < len(image_files):
                    body.append(f"![]({artifacts_dir.name}/{image_files[pic_idx].name})")
                pic_idx += 1
                continue
            text = (getattr(item, "text", "") or "").strip()
            if not text:
                continue
            if getattr(item, "content_layer", None) == ContentLayer.NOTES:
                notes.append(text)
            else:
                body.append(text)
        parts.append(f"## Slide {slide_no}")
        if body:
            parts.append("\n\n".join(body))
        if notes:
            parts.append("### Speaker Notes\n\n" + "\n\n".join(notes))
    return "\n\n".join(parts).strip() + "\n"


def _picture_description(picture) -> str | None:
    meta = getattr(picture, "meta", None)
    if not meta:
        return None
    desc = getattr(meta, "description", None)
    if not desc:
        return None
    text = getattr(desc, "text", None)
    return text.strip() if text else None


def _inject_captions(
    md: str,
    captions: Iterable[str | None],
    *,
    drop_uncaptioned: bool = False,
) -> tuple[str, list[str]]:
    """Replace image alt text with VLM captions. Returns (new_md, dropped_image_urls)."""
    cap_iter = iter(captions)
    dropped: list[str] = []

    def repl(match: re.Match[str]) -> str:
        url = match.group("url")
        try:
            cap = next(cap_iter)
        except StopIteration:
            return match.group(0)
        if not cap:
            if drop_uncaptioned:
                dropped.append(url)
                return ""
            return match.group(0)
        # Markdown alt text can't contain unescaped ] or newlines.
        clean = cap.replace("\n", " ").replace("]", ")").strip()
        return f"![{clean}]({url})"

    new_md = IMAGE_LINE.sub(repl, md)
    if dropped:
        # Collapse blank-line runs left behind by removed image lines.
        new_md = re.sub(r"\n{3,}", "\n\n", new_md)
    return new_md, dropped


def _prune_orphans(md_dir: Path, urls: list[str], *, verbose: bool = False) -> None:
    for url in urls:
        if "://" in url:
            continue
        target = (md_dir / url).resolve()
        try:
            target.relative_to(md_dir.resolve())
        except ValueError:
            continue
        if target.is_file():
            target.unlink()
            if verbose:
                print(f"[docling-convert] pruned uncaptioned image {target.name}", file=sys.stderr)


def main() -> int:
    args = parse_args()
    convert(
        args.input,
        args.output,
        caption=args.caption,
        caption_model=args.caption_model,
        caption_prompt=args.caption_prompt,
        include_images=not args.no_images,
        ocr=args.ocr,
        max_pages=args.max_pages,
        verbose=args.verbose,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
