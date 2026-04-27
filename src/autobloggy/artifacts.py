from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import PostMeta, PostPaths
from .utils import ensure_dir, now_iso, repo_root


def post_paths(slug: str, root: Path | None = None) -> PostPaths:
    repo = repo_root(root)
    post_root = repo / "posts" / slug
    inputs_root = post_root / "inputs"
    user_provided_root = inputs_root / "user_provided"
    prepared_root = inputs_root / "prepared"
    discovery_root = inputs_root / "discovery"
    verify_root = post_root / ".verify"
    return PostPaths(
        slug=slug,
        root=post_root,
        meta=post_root / "meta.yaml",
        inputs_root=inputs_root,
        user_provided_root=user_provided_root,
        user_readme=user_provided_root / "README.md",
        user_brief=user_provided_root / "brief.md",
        user_raw_root=user_provided_root / "raw",
        extracted_root=inputs_root / "extracted",
        prepared_root=prepared_root,
        prepared_input=prepared_root / "input.md",
        input_manifest=prepared_root / "input_manifest.yaml",
        discovery_root=discovery_root,
        discovery_summary=discovery_root / "discovery.md",
        strategy=post_root / "strategy.md",
        outline=post_root / "outline.md",
        draft=post_root / "draft.html",
        verify_root=verify_root,
        verify_pack=verify_root / "verify-pack.md",
        export_html_root=post_root / "export" / "html",
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def read_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def write_yaml(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=False)


def read_meta(slug: str, root: Path | None = None) -> PostMeta:
    paths = post_paths(slug, root)
    if not paths.meta.exists():
        raise FileNotFoundError(f"Post meta does not exist: {paths.meta}")
    return PostMeta.model_validate(read_yaml(paths.meta))


def write_meta(meta: PostMeta, root: Path | None = None) -> Path:
    paths = post_paths(meta.slug, root)
    write_yaml(paths.meta, meta.model_dump(mode="json", exclude_none=True))
    return paths.meta


def patch_meta(slug: str, root: Path | None = None, **fields: Any) -> PostMeta:
    meta = read_meta(slug, root)
    updated = meta.model_copy(update=fields)
    write_meta(updated, root)
    return updated


def init_meta(slug: str, preset: str, root: Path | None = None) -> PostMeta:
    paths = post_paths(slug, root)
    if paths.meta.exists():
        return read_meta(slug, root)
    meta = PostMeta(slug=slug, preset=preset, status="drafting", created_at=now_iso())
    write_meta(meta, root)
    return meta
