from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifacts import extract_frontmatter, read_text, read_yaml
from .models import PresetPaths
from .utils import repo_root


PRESET_FILE_NAMES = {
    "strategy_template": "strategy_template.md",
    "writing_guide": "writing_guide.md",
    "brand_guide": "brand_guide.md",
}


def load_repo_config(root: Path | None = None) -> dict[str, Any]:
    repo = repo_root(root)
    return read_yaml(repo / "config.yaml") or {}


def load_prepare_config(root: Path | None = None) -> dict[str, Any]:
    return load_repo_config(root).get("prepare") or {}


def default_preset_name(root: Path | None = None) -> str:
    prepare = load_prepare_config(root)
    return str(prepare.get("default_preset") or "default")


def presets_root(root: Path | None = None) -> Path:
    repo = repo_root(root)
    prepare = load_prepare_config(repo)
    configured = Path(str(prepare.get("presets_dir") or "presets"))
    if configured.is_absolute():
        return configured
    return (repo / configured).resolve()


def repo_relative_path(path: Path, root: Path | None = None) -> str:
    repo = repo_root(root)
    return str(path.resolve().relative_to(repo))


def preset_paths(name: str, root: Path | None = None) -> PresetPaths:
    preset_root = presets_root(root) / name
    preset = PresetPaths(
        name=name,
        root=preset_root,
        strategy_template=preset_root / PRESET_FILE_NAMES["strategy_template"],
        writing_guide=preset_root / PRESET_FILE_NAMES["writing_guide"],
        brand_guide=preset_root / PRESET_FILE_NAMES["brand_guide"],
    )
    missing = [path for path in (preset.strategy_template, preset.writing_guide, preset.brand_guide) if not path.exists()]
    if missing:
        missing_list = ", ".join(repo_relative_path(path, root) for path in missing)
        raise FileNotFoundError(f"Preset `{name}` is incomplete. Missing: {missing_list}.")
    return preset


def strategy_frontmatter_preset(strategy_path: Path) -> str | None:
    if not strategy_path.exists():
        return None
    frontmatter, _ = extract_frontmatter(read_text(strategy_path))
    preset = frontmatter.get("preset")
    if not preset:
        return None
    return str(preset).strip() or None
