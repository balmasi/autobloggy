from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

from tests.conftest import run_cli


def _seed_post_with_pdf_source(repo: Path, slug: str = "demo") -> tuple[Path, Path]:
    """Create a minimal post layout with a fake PDF source registered in the manifest.

    Returns (post_root, raw_pdf_path).
    """
    post_root = repo / "posts" / slug
    raw_root = post_root / "inputs" / "raw"
    prepared_root = post_root / "inputs" / "prepared"
    prepared_001 = prepared_root / "source-001"
    raw_root.mkdir(parents=True)
    prepared_001.mkdir(parents=True)

    raw_pdf = raw_root / "deck.pdf"
    raw_pdf.write_bytes(b"%PDF-1.4 fake")

    placeholder = prepared_001 / "source.md"
    placeholder.write_text("# Prepared Source: source-001\n\nplaceholder.\n", encoding="utf-8")

    manifest = {
        "sources": [
            {
                "id": "intake",
                "kind": "intake",
                "description": "Operator intake from the kickoff conversation.",
                "path": "inputs/prepared/intake/source.md",
                "origins": ["conversation"],
            },
            {
                "id": "source-001",
                "kind": "pdf",
                "description": "Placeholder source for deck.pdf.",
                "path": "inputs/prepared/source-001/source.md",
                "origins": ["inputs/raw/deck.pdf"],
            },
        ]
    }
    (prepared_root / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    return post_root, raw_pdf


def test_normalize_source_unknown_id_errors(fresh_repo: Path) -> None:
    _seed_post_with_pdf_source(fresh_repo)
    result = run_cli(fresh_repo, "normalize-source", "--slug", "demo", "--source-id", "ghost", check=False)
    assert result.returncode != 0
    assert "not in manifest" in (result.stderr + result.stdout)


def test_normalize_source_updates_manifest_on_success(
    fresh_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    post_root, _ = _seed_post_with_pdf_source(fresh_repo)

    def fake_run(cmd, *args, **kwargs):
        assert "--output" in cmd
        out_path = Path(cmd[cmd.index("--output") + 1])
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            "# Deck\n\n![A diagram](source_images/image_000001.png)\n",
            encoding="utf-8",
        )
        (out_path.parent / f"{out_path.stem}_images").mkdir(exist_ok=True)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr("autobloggy.prepare.subprocess.run", fake_run)

    from autobloggy.prepare import run_normalize_source

    result = run_normalize_source("demo", "source-001")
    assert result["source_id"] == "source-001"
    assert result["captioned"] == "false"

    manifest = yaml.safe_load((post_root / "inputs/prepared/manifest.yaml").read_text())
    entry = next(e for e in manifest["sources"] if e["id"] == "source-001")
    assert entry["normalized"] is True
    assert "deck.pdf" in entry["description"]

    body = (post_root / "inputs/prepared/source-001/source.md").read_text()
    assert "A diagram" in body
    assert "placeholder" not in body


def test_normalize_source_subprocess_failure_keeps_placeholder(
    fresh_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    post_root, _ = _seed_post_with_pdf_source(fresh_repo)

    def fake_run(cmd, *args, **kwargs):
        return subprocess.CompletedProcess(cmd, 2, "", "boom")

    monkeypatch.setattr("autobloggy.prepare.subprocess.run", fake_run)

    from autobloggy.prepare import run_normalize_source

    with pytest.raises(RuntimeError):
        run_normalize_source("demo", "source-001")

    manifest = yaml.safe_load((post_root / "inputs/prepared/manifest.yaml").read_text())
    entry = next(e for e in manifest["sources"] if e["id"] == "source-001")
    assert entry.get("normalized", False) is False
    body = (post_root / "inputs/prepared/source-001/source.md").read_text()
    assert "placeholder" in body


def test_normalize_source_rejects_non_docling_kind(fresh_repo: Path) -> None:
    post_root, _ = _seed_post_with_pdf_source(fresh_repo)
    manifest_path = post_root / "inputs/prepared/manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    for entry in manifest["sources"]:
        if entry["id"] == "source-001":
            entry["kind"] = "txt"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False))

    result = run_cli(fresh_repo, "normalize-source", "--slug", "demo", "--source-id", "source-001", check=False)
    assert result.returncode != 0
    assert "kind" in (result.stderr + result.stdout)


def test_normalize_source_cli_requires_args(fresh_repo: Path) -> None:
    result = run_cli(fresh_repo, "normalize-source", check=False)
    assert result.returncode != 0
    assert "--slug" in result.stderr or "--source-id" in result.stderr
