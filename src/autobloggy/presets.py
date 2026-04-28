from pathlib import Path
from typing import Any

from .artifacts import read_yaml
from .models import BriefSectionDef, IntakeDepthConfig, PresetManifest, ResolvedPreset, ResolvedPresetResource
from .utils import repo_root


def load_repo_config(root: Path | None = None) -> dict[str, Any]:
    repo = repo_root(root)
    path = repo / "config.yaml"
    return read_yaml(path) if path.exists() else {}


def load_prepare_config(root: Path | None = None) -> dict[str, Any]:
    return load_repo_config(root).get("prepare") or {}


def load_intake_config(root: Path | None = None) -> dict[str, Any]:
    return load_repo_config(root).get("intake") or {}


def load_verify_config(root: Path | None = None) -> dict[str, Any]:
    return load_repo_config(root).get("verify") or {}


def default_preset_name(root: Path | None = None) -> str:
    return str(load_prepare_config(root).get("default_preset") or "default")


def default_intake_depth_name(root: Path | None = None) -> str:
    return str(load_intake_config(root).get("default_depth") or "fast")


def presets_root(root: Path | None = None) -> Path:
    repo = repo_root(root)
    configured = Path(str(load_prepare_config(repo).get("presets_dir") or "presets"))
    if configured.is_absolute():
        return configured
    return (repo / configured).resolve()


def repo_relative_path(path: Path, root: Path | None = None) -> str:
    repo = repo_root(root)
    return str(path.resolve().relative_to(repo))


def load_brief_sections(root: Path | None = None) -> dict[str, BriefSectionDef]:
    raw = load_repo_config(root).get("brief_sections") or {}
    return {k: BriefSectionDef.model_validate(v) for k, v in raw.items()}


def load_intake_depth(name: str, root: Path | None = None) -> IntakeDepthConfig:
    depths = load_intake_config(root).get("depths") or {}
    if name not in depths:
        available = ", ".join(sorted(depths)) or "(none configured)"
        raise ValueError(f"Unknown intake depth `{name}`. Available depths: {available}.")
    depth = IntakeDepthConfig.model_validate(depths[name] or {})
    if depth.discovery not in {"never", "ask", "required"}:
        raise ValueError(
            f"Intake depth `{name}` has invalid discovery policy `{depth.discovery}`. "
            "Use one of: never, ask, required."
        )
    return depth


def _manifest_path(name: str, root: Path | None = None) -> Path:
    return presets_root(root) / name / "preset.yaml"


def load_preset_manifest(name: str, root: Path | None = None) -> PresetManifest:
    path = _manifest_path(name, root)
    if not path.exists():
        raise FileNotFoundError(f"Preset `{name}` is missing {repo_relative_path(path, root)}.")
    return PresetManifest.model_validate(read_yaml(path))


def _preset_chain(name: str, root: Path | None = None) -> list[tuple[str, Path, PresetManifest]]:
    manifest = load_preset_manifest(name, root)
    chain: list[tuple[str, Path, PresetManifest]] = []
    if manifest.extends:
        chain.extend(_preset_chain(manifest.extends, root))
    chain.append((name, presets_root(root) / name, manifest))
    return chain


def _parse_selection(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise ValueError(f"Invalid --select `{value}`. Expected key=value.")
    dimension, key = value.split("=", 1)
    dimension = dimension.strip()
    key = key.strip()
    if not dimension or not key:
        raise ValueError(f"Invalid --select `{value}`. Expected key=value.")
    return dimension, key


def parse_cli_selections(values: list[str] | None) -> dict[str, str]:
    selections: dict[str, str] = {}
    for value in values or []:
        dimension, key = _parse_selection(value)
        selections[dimension] = key
    return selections


def resolve_preset(
    name: str,
    selection_overrides: dict[str, str] | None = None,
    root: Path | None = None,
) -> ResolvedPreset:
    chain = _preset_chain(name, root)
    defaults: dict[str, str] = {}
    definitions: dict[str, dict[str, tuple[str, Path]]] = {}

    for _preset_name, preset_root, manifest in chain:
        defaults.update(manifest.defaults)
        for dimension, values in manifest.definitions.items():
            dimension_defs = definitions.setdefault(dimension, {})
            for key, relative_path in values.items():
                dimension_defs[key] = (relative_path, preset_root)

    overrides = selection_overrides or {}
    unknown_dimensions = sorted(set(overrides) - set(definitions))
    if unknown_dimensions:
        available = ", ".join(sorted(definitions)) or "(none)"
        raise ValueError(
            "Unknown preset selection dimension(s): "
            + ", ".join(f"`{item}`" for item in unknown_dimensions)
            + f". Available dimensions: {available}."
        )

    selections = {**defaults, **overrides}
    resources: dict[str, ResolvedPresetResource] = {}
    for dimension, selected_key in selections.items():
        dimension_defs = definitions.get(dimension)
        if not dimension_defs:
            available = ", ".join(sorted(definitions)) or "(none)"
            raise ValueError(f"Preset `{name}` has no definitions for `{dimension}`. Available dimensions: {available}.")
        if selected_key not in dimension_defs:
            available_keys = ", ".join(sorted(dimension_defs)) or "(none)"
            raise ValueError(
                f"Unknown `{dimension}` selection `{selected_key}` for preset `{name}`. "
                f"Available values: {available_keys}."
            )
        relative_path, declaring_root = dimension_defs[selected_key]
        path = (declaring_root / relative_path).resolve()
        if not path.exists():
            raise FileNotFoundError(
                f"Preset `{name}` selection `{dimension}={selected_key}` points to missing resource "
                f"{repo_relative_path(path, root)}."
            )
        resources[dimension] = ResolvedPresetResource(dimension=dimension, key=selected_key, path=path)

    if "html_template" not in resources:
        raise ValueError(f"Preset `{name}` must resolve one `html_template` resource.")

    return ResolvedPreset(
        name=name,
        root=presets_root(root) / name,
        selections=selections,
        resources=resources,
    )


def required_selection_errors(depth: IntakeDepthConfig, cli_selections: dict[str, str]) -> list[str]:
    missing = [dimension for dimension in depth.require_selections if dimension not in cli_selections]
    if not missing:
        return []
    return [
        "Intake depth requires explicit --select values for: "
        + ", ".join(f"`{dimension}`" for dimension in missing)
        + "."
    ]
