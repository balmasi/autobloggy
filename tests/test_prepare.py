from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from pptx import Presentation

from autobloggy.artifacts import extract_frontmatter
from autobloggy.prepare import run_prepare
from tests.helpers import copy_repo, resolve_generated_strategy


def test_prepare_supports_markdown_input(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)
    slug = "prepare-markdown"
    generated = run_prepare(slug, repo / "tests/fixtures/example_input.md", "draft")

    assert "draft" in generated
    assert (repo / "posts" / slug / "draft.qmd").exists()


def test_prepare_supports_user_input_directory(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)
    slug = "prepare-input-dir"
    input_root = repo / "posts" / slug / "inputs" / "user_provided"
    input_root.mkdir(parents=True, exist_ok=True)
    input_path = input_root / "input.md"
    input_path.write_text(
        """---
title: Input Directory Example
---

# Input Directory Example

User-provided notes can live beside supporting files instead of cluttering the post root.
""",
        encoding="utf-8",
    )
    (input_root / "slides").mkdir()
    (input_root / "slides" / "overview.txt").write_text("Slide notes.", encoding="utf-8")

    generated = run_prepare(slug, input_root, "draft")

    assert "draft" in generated

    strategy_frontmatter, _ = extract_frontmatter((repo / "posts" / slug / "strategy.md").read_text(encoding="utf-8"))
    assert strategy_frontmatter["input_path"] == str(input_path)
    assert strategy_frontmatter["input_root"] == str(input_root)


def test_prepare_supports_pptx_input(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)
    pptx_path = tmp_path / "input.pptx"
    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[1])
    slide.shapes.title.text = "Checklist rollout"
    slide.placeholders[1].text = "Handoffs dropped from 30 minutes to 5 minutes."
    presentation.save(pptx_path)

    slug = "prepare-pptx"
    generated = run_prepare(slug, pptx_path, "draft")

    assert "draft" in generated
    assert (repo / "posts" / slug / "draft.qmd").exists()


def test_prepare_cleans_markdown_input_before_generating_artifacts(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)
    input_path = repo / "tests" / "fixtures" / "noisy_input.md"
    input_path.write_text(
        """---
title: Noisy Input
---

# Noisy Input

Claude Code works in a terminal and can edit code across files.

NotebookLM works from a bounded source set and helps with synthesis before implementation. https://example.com/notebooklm

## Questions to answer

- What should move from research into execution?
- Where should implementation start?
""",
        encoding="utf-8",
    )

    slug = "prepare-noisy-markdown"
    run_prepare(slug, input_path, "draft")

    strategy_text = (repo / "posts" / slug / "strategy.md").read_text(encoding="utf-8")
    outline_text = (repo / "posts" / slug / "outline.md").read_text(encoding="utf-8")
    draft_text = (repo / "posts" / slug / "draft.qmd").read_text(encoding="utf-8")

    assert "# Noisy Input\n\n# Noisy Input" not in draft_text
    assert draft_text.count("# Noisy Input") == 1
    assert "## Noisy Input" not in draft_text
    assert "Questions to answer" not in outline_text
    assert "- " in outline_text
    assert "https://example.com/notebooklm" not in draft_text
    assert "## Evidence Standards" not in strategy_text


def test_generate_strategy_includes_required_voice_sections(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)
    slug = "prepare-strategy-template"
    input_path = repo / "tests" / "fixtures" / "example_input.md"

    run_prepare(slug, input_path, "strategy")

    strategy_text = (repo / "posts" / slug / "strategy.md").read_text(encoding="utf-8")
    assert "## Target Voice" in strategy_text
    assert "## Style Guardrails" in strategy_text
    assert "## Approval Checklist" in strategy_text
    assert "## Evidence Standards" not in strategy_text
    assert "[REQUIRED:" in strategy_text
    assert "input_root:" in strategy_text


def test_cli_requires_strategy_approval_before_generating_draft(repo_root: Path, tmp_path: Path) -> None:
    repo = copy_repo(repo_root, tmp_path)
    slug = "review-gated"
    input_path = repo / "tests" / "fixtures" / "example_input.md"

    first_prepare = subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "prepare", "--slug", slug, "--input", str(input_path)],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=True,
    )
    assert "strategy\t" in first_prepare.stdout
    assert not (repo / "posts" / slug / "draft.qmd").exists()

    strategy_path = repo / "posts" / slug / "strategy.md"
    strategy_path.write_text(strategy_path.read_text(encoding="utf-8") + "\nCustom review note.\n", encoding="utf-8")

    rejected_approval = subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "approve-strategy", "--slug", slug],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected_approval.returncode != 0
    assert "Strategy is incomplete" in (rejected_approval.stdout + rejected_approval.stderr)

    resolve_generated_strategy(strategy_path)

    blocked_prepare = subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "prepare", "--slug", slug, "--input", str(input_path), "--through", "draft"],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    assert blocked_prepare.returncode != 0
    assert "approve-strategy" in (blocked_prepare.stdout + blocked_prepare.stderr)

    subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "approve-strategy", "--slug", slug],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=True,
    )
    assert "status: approved" in strategy_path.read_text(encoding="utf-8")

    outline_prepare = subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "prepare", "--slug", slug, "--input", str(input_path), "--through", "draft"],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    assert outline_prepare.returncode != 0
    assert "outline\t" in outline_prepare.stdout
    assert "approve-outline" in (outline_prepare.stdout + outline_prepare.stderr)
    assert not (repo / "posts" / slug / "draft.qmd").exists()

    blocked_outline = subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "prepare", "--slug", slug, "--input", str(input_path), "--through", "draft"],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    assert blocked_outline.returncode != 0
    assert "approve-outline" in (blocked_outline.stdout + blocked_outline.stderr)

    subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "approve-outline", "--slug", slug],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=True,
    )
    outline_path = repo / "posts" / slug / "outline.md"
    assert "status: approved" in outline_path.read_text(encoding="utf-8")

    final_prepare = subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "prepare", "--slug", slug, "--input", str(input_path), "--through", "draft"],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=True,
    )
    assert "draft\t" in final_prepare.stdout
    assert (repo / "posts" / slug / "draft.qmd").exists()
    assert "Custom review note." in strategy_path.read_text(encoding="utf-8")
