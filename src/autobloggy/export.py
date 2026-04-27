from __future__ import annotations

import shutil

from .artifacts import post_paths
from .utils import ensure_dir

SUPPORTED_FORMATS = ("html",)


def export_post(slug: str, output_format: str = "html") -> dict[str, str]:
    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unknown export format `{output_format}`. Supported: {', '.join(SUPPORTED_FORMATS)}."
        )
    paths = post_paths(slug)
    if not paths.draft.exists():
        raise FileNotFoundError(f"Draft does not exist: {paths.draft}")

    if paths.export_html_root.exists():
        shutil.rmtree(paths.export_html_root)
    ensure_dir(paths.export_html_root)
    destination = paths.export_html_root / "draft.html"
    shutil.copy2(paths.draft, destination)
    return {"format": "html", "output": str(destination)}
