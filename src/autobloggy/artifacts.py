from pathlib import Path
from typing import Any

import yaml

from .models import DiscoveryMeta, PostMeta, PostPaths
from .utils import ensure_dir, now_iso, repo_root


def post_paths(slug: str, root: Path | None = None) -> PostPaths:
    repo = repo_root(root)
    post_root = repo / "posts" / slug
    inputs_root = post_root / "inputs"
    prepared_root = inputs_root / "prepared"
    verify_root = post_root / ".verify"
    return PostPaths(
        slug=slug,
        root=post_root,
        meta=post_root / "meta.yaml",
        blog_brief=post_root / "blog_brief.md",
        inputs_root=inputs_root,
        inputs_raw_root=inputs_root / "raw",
        prepared_root=prepared_root,
        prepared_manifest=prepared_root / "manifest.yaml",
        prepared_intake_root=prepared_root / "intake",
        prepared_intake_source=prepared_root / "intake" / "source.md",
        prepared_discovery_root=prepared_root / "discovery",
        prepared_discovery_source=prepared_root / "discovery" / "source.md",
        draft=post_root / "draft.html",
        verify_root=verify_root,
        verify_pack=verify_root / "verify-pack.md",
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


def init_meta(
    slug: str,
    preset: str,
    intake_depth: str,
    selections: dict[str, str],
    discovery: DiscoveryMeta,
    root: Path | None = None,
) -> PostMeta:
    paths = post_paths(slug, root)
    if paths.meta.exists():
        return read_meta(slug, root)
    meta = PostMeta(
        slug=slug,
        preset=preset,
        intake_depth=intake_depth,
        status="briefing",
        created_at=now_iso(),
        selections=selections,
        discovery=discovery,
    )
    write_meta(meta, root)
    return meta
