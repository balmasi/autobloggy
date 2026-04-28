---
name: docling-convert
description: Convert PDF, DOCX, PPTX, HTML, and image documents to normalized Markdown with extracted images and optional VLM auto-captions. Use when a downstream LLM needs the full text + visual context of a source document. Triggers on document conversion, PDF parsing, slide deck extraction, image captioning, OCR, document-to-markdown.
---

# Docling Convert

Thin wrapper around [docling](https://github.com/docling-project/docling) for turning a source document into one Markdown file plus an adjacent folder of extracted images. Optionally runs a local VLM over each picture and injects the caption directly under the image, so a downstream LLM gets text and visual context in a single file.

This skill is project-agnostic. It does not know about any caller's directory layout — supply the input path and the output path; the skill handles the rest.

## When to use

- A user drops a PDF, slide deck, doc, or image and you need its content as text for an LLM.
- The document has diagrams, charts, screenshots, or other visuals that carry meaning.
- You want one file an LLM can read without opening the original.

## Output shape

```
<output>.md                  # markdown text, with image references and (optional) captions
<output>_images/             # extracted images, referenced from the markdown
```

Each captioned picture has its description inlined as alt text:

```markdown
![A two-column landscape diagram showing four pillars: LLM, Harness, Orchestrator, Platform.](my-doc_images/image_000001.png)
```

Without `--caption`, alt text falls back to `Image`.

Tables come out as Markdown tables. Headings and lists are preserved. Page breaks are not preserved by default.

## Quick start

```bash
uv run --with 'docling' python skills/docling-convert/scripts/convert.py INPUT --output OUTPUT.md
```

With auto-captioning of images (downloads a small local VLM on first run):

```bash
uv run --with 'docling' python skills/docling-convert/scripts/convert.py INPUT --output OUTPUT.md --caption
```

For scanned PDFs, complex multi-column layouts, tables, handwriting, formulas,
or remote/local VLM pipeline work, consult
[references/pipelines.md](references/pipelines.md) before converting. Keep the
main CLI path simple unless fidelity requires a heavier Docling pipeline.

## Flags

- `--output`, `-o` — output `.md` path. Required. Sidecar images go to `<stem>_images/` next to it.
- `--caption` — run a local VLM on every embedded image and inject a description.
- `--caption-model {smolvlm,granite}` — VLM preset. Default `smolvlm` (smaller, faster). `granite` is more accurate but heavier.
- `--caption-prompt "..."` — override the prompt sent to the VLM.
- `--no-images` — drop images entirely; produce text-only markdown.
- `--ocr` — force OCR on PDFs (slower; needed for scanned PDFs).
- `--max-pages N` — limit conversion to the first N pages.
- `--verbose` — log progress to stderr.

## Notes

- Captioning currently applies to PDF inputs. Non-PDF formats convert and extract images, but the VLM pass is a PDF-pipeline feature in docling.
- First captioning run downloads the VLM weights (a few hundred MB for SmolVLM, ~2 GB for Granite). Subsequent runs are cached.
- Models run on CPU by default. On Apple Silicon, MPS works if your torch build supports it.
- For air-gapped or remote-API captioning (Ollama, LM Studio, OpenAI-compatible endpoints), use docling's `PictureDescriptionVlmEngineOptions` directly in Python — see [docling's pictures_description_api example](https://github.com/docling-project/docling/blob/main/docs/examples/pictures_description_api.py). Not exposed in this skill's CLI yet.
- Docling's Python API expects `DocumentConverter(format_options=...)` keys like `InputFormat.PDF`, not string keys. See the pipeline reference for examples.

## Programmatic use

If you'd rather call docling directly, the script is small enough to read and adapt — `scripts/convert.py`. It exposes a `convert(input_path, output_path, caption=False, ...)` function that returns the path to the markdown.
