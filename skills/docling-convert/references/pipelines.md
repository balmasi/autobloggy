# Docling Pipeline Reference

Use this reference when the default `scripts/convert.py` path is not enough.
The goal is to choose a better Docling pipeline without making `SKILL.md`
large or turning the simple Markdown converter into a general Docling wrapper.

## Decision Matrix

| Need | Start with | Escalate to |
|---|---|---|
| Born-digital PDF, DOCX, PPTX, HTML | Default converter | `--ocr` only if text is missing |
| Scanned PDF or image-only pages | `--ocr` | VLM pipeline if OCR ordering is poor |
| Complex layout or multi-column reading order | Default converter | VLM pipeline |
| Tables are central to the source | Default converter | VLM pipeline; inspect table Markdown |
| Handwriting, formulas, dense figures | VLM pipeline | Remote or larger local VLM |
| Text-heavy PDF where VLM may hallucinate | Default converter | Hybrid VLM with `force_backend_text=True` |

## CLI Examples

Use Docling's CLI directly for pipeline experiments:

```bash
docling report.pdf --to md --output /tmp/docling-out
docling report.pdf --to json --output /tmp/docling-out
docling report.pdf --pipeline vlm --output /tmp/docling-out
docling report.pdf --pipeline vlm --vlm-model granite_docling --output /tmp/docling-out
docling report.pdf --ocr-engine tesserocr --output /tmp/docling-out
docling report.pdf --no-ocr --output /tmp/docling-out
docling report.pdf --no-tables --output /tmp/docling-out
```

For the Autobloggy normalized Markdown shape, prefer `scripts/convert.py`
after deciding which options are actually needed.

## Python API Gotcha

Docling 2.81+ expects `format_options` to map `InputFormat` enum values to
format options. Do not pass string keys or raw pipeline options.

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions(do_ocr=True, do_table_structure=True)
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
    }
)
result = converter.convert("report.pdf")
markdown = result.document.export_to_markdown()
```

## VLM Pipeline

Use VLM only when the document's layout or visual content justifies the cost.

```python
from docling.datamodel import vlm_model_specs
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.GRANITEDOCLING_TRANSFORMERS,
    generate_page_images=True,
)
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
            pipeline_options=pipeline_options,
        )
    }
)
result = converter.convert("report.pdf")
```

## Hybrid VLM

For text-heavy PDFs, keep deterministic backend text while asking the VLM to
handle visual regions:

```python
pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.GRANITEDOCLING_TRANSFORMERS,
    force_backend_text=True,
    generate_page_images=True,
)
```

## Remote VLM

Outbound HTTP is gated. Remote endpoints must opt in with
`enable_remote_services=True`.

```python
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat

vlm_options = ApiVlmOptions(
    url="http://localhost:8000/v1/chat/completions",
    params={"model": "ibm-granite/granite-docling-258M", "max_tokens": 4096},
    prompt="Convert this page to docling.",
    response_format=ResponseFormat.DOCTAGS,
    timeout=120,
)
pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_options,
    generate_page_images=True,
    enable_remote_services=True,
)
```

## Manual Checks

After conversion, inspect the Markdown before using it as source material:

- Page count roughly matches the source.
- Output is not near-empty.
- Obvious tables survived as tables.
- Image references point to files that exist.
- No repeated boilerplate lines dominate the output.
- No replacement characters (`\ufffd`) appear in extracted text.
