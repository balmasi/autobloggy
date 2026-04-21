from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from .models import PostPaths
from .utils import ensure_dir, repo_root


def post_paths(slug: str, root: Path | None = None) -> PostPaths:
    repo = repo_root(root)
    post_root = repo / "posts" / slug
    return PostPaths(
        slug=slug,
        root=post_root,
        user_provided_root=post_root / "inputs" / "user_provided",
        strategy=post_root / "strategy.md",
        outline=post_root / "outline.md",
        draft=post_root / "draft.qmd",
        runs=post_root / "runs",
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

def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def extract_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    return yaml.safe_load(raw) or {}, body.lstrip("\n")


def format_markdown_with_frontmatter(frontmatter: dict[str, Any], body: str) -> str:
    return f"---\n{yaml.safe_dump(frontmatter, sort_keys=False).strip()}\n---\n\n{body.strip()}\n"


def text_fingerprint(payload: dict[str, Any]) -> str:
    stable = {
        key: payload[key]
        for key in sorted(payload)
    }
    encoded = json.dumps(stable, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]
