from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from pptx import Presentation

from autobloggy.prepare import run_prepare
from tests.helpers import copy_repo


def resolve_generated_brief(brief_path: Path) -> None:
    text = brief_path.read_text(encoding="utf-8")
    replacements = {
        "[REQUIRED: name the primary reader and the job they are trying to do.]": "Platform and product engineering leads who need operational guidance they can apply this quarter.",
        "[REQUIRED: confirm or replace this with the user's preferred voice.]": "",
        "[REQUIRED: edit these guardrails until they match the user's expectations for the piece.]": "",
        "[REQUIRED: add or remove points until this captures the non-negotiable substance of the post.]": "",
        "[REQUIRED: record any tones, claims, examples, or framing that should be avoided.]": "",
        "- [REQUIRED: What specific reader or buyer context should shape the framing?]": "- The framing should help technical leaders decide whether this workflow is worth adopting for their team.",
        "- [REQUIRED: Which claims or examples are mandatory because they matter to this audience?]": "- The post must include one concrete example, one tradeoff, and one boundary where the approach should not be used.",
        "- [REQUIRED: What should the post sound like, and what should it never sound like?]": "- It should sound like a practiced operator and never like marketing copy or generic AI advice.",
        "- [REQUIRED: What practical takeaway should the reader leave with?]": "- The reader should leave with a clear decision rule and a concrete next step.",
        "- [ ] Audience is specific enough to guide structure and examples.": "- [x] Audience is specific enough to guide structure and examples.",
        "- [ ] Target voice reflects the user's actual preference, not the default.": "- [x] Target voice reflects the user's actual preference, not the default.",
        "- [ ] Style guardrails are concrete enough to guide generation.": "- [x] Style guardrails are concrete enough to guide generation.",
        "- [ ] Must-cover points capture the non-negotiable substance of the post.": "- [x] Must-cover points capture the non-negotiable substance of the post.",
        "- [ ] Must-avoid and evidence rules are explicit.": "- [x] Must-avoid and evidence rules are explicit.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    brief_path.write_text(text, encoding="utf-8")


def test_prepare_supports_markdown_seed(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)
    slug = "prepare-markdown"
    generated = run_prepare(slug, repo / "tests/fixtures/example_seed.md", "draft")

    assert "draft" in generated
    assert (repo / "posts" / slug / "claims.yaml").exists()


def test_prepare_supports_pptx_seed(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)
    pptx_path = tmp_path / "seed.pptx"
    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[1])
    slide.shapes.title.text = "Checklist rollout"
    slide.placeholders[1].text = "Handoffs dropped from 30 minutes to 5 minutes."
    presentation.save(pptx_path)

    slug = "prepare-pptx"
    generated = run_prepare(slug, pptx_path, "claims")

    assert "claims" in generated
    assert (repo / "posts" / slug / "sources.yaml").exists()


def test_prepare_cleans_markdown_seed_before_generating_artifacts(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)
    seed_path = repo / "tests" / "fixtures" / "noisy_seed.md"
    seed_path.write_text(
        """---
title: Noisy Seed
---

# Noisy Seed

Claude Code works in a terminal and can edit code across files.

NotebookLM works from a bounded source set and helps with synthesis before implementation. https://example.com/notebooklm

## Questions to answer

- What should move from research into execution?
- Where should implementation start?
""",
        encoding="utf-8",
    )

    slug = "prepare-noisy-markdown"
    run_prepare(slug, seed_path, "draft")

    brief_text = (repo / "posts" / slug / "brief.md").read_text(encoding="utf-8")
    outline_text = (repo / "posts" / slug / "outline.md").read_text(encoding="utf-8")
    claims_text = (repo / "posts" / slug / "claims.yaml").read_text(encoding="utf-8")
    draft_text = (repo / "posts" / slug / "draft.qmd").read_text(encoding="utf-8")
    sources_text = (repo / "posts" / slug / "sources.yaml").read_text(encoding="utf-8")

    assert "# Noisy Seed\n\n# Noisy Seed" not in draft_text
    assert draft_text.count("# Noisy Seed") == 1
    assert "## Noisy Seed" not in draft_text
    assert "Questions to answer" not in outline_text
    assert "https://example.com/notebooklm" not in claims_text
    assert sources_text.count("locator: https://example.com/notebooklm") == 1


def test_generate_brief_includes_required_voice_sections(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)
    slug = "prepare-brief-template"
    seed_path = repo / "tests" / "fixtures" / "example_seed.md"

    run_prepare(slug, seed_path, "brief")

    brief_text = (repo / "posts" / slug / "brief.md").read_text(encoding="utf-8")
    assert "## Target Voice" in brief_text
    assert "## Style Guardrails" in brief_text
    assert "## Evidence Standards" in brief_text
    assert "## Approval Checklist" in brief_text
    assert "[REQUIRED:" in brief_text


def test_cli_requires_brief_approval_before_generating_draft(repo_root: Path, tmp_path: Path) -> None:
    repo = copy_repo(repo_root, tmp_path)
    slug = "review-gated"
    seed_path = repo / "tests" / "fixtures" / "example_seed.md"

    first_prepare = subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "prepare", "--slug", slug, "--seed", str(seed_path)],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=True,
    )
    assert "brief\t" in first_prepare.stdout
    assert not (repo / "posts" / slug / "draft.qmd").exists()

    brief_path = repo / "posts" / slug / "brief.md"
    brief_path.write_text(brief_path.read_text(encoding="utf-8") + "\nCustom review note.\n", encoding="utf-8")

    rejected_approval = subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "approve-brief", "--slug", slug],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected_approval.returncode != 0
    assert "Brief is incomplete" in (rejected_approval.stdout + rejected_approval.stderr)

    resolve_generated_brief(brief_path)

    blocked_prepare = subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "prepare", "--slug", slug, "--seed", str(seed_path), "--through", "draft"],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    assert blocked_prepare.returncode != 0
    assert "approve-brief" in (blocked_prepare.stdout + blocked_prepare.stderr)

    subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "approve-brief", "--slug", slug],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=True,
    )
    assert "status: approved" in brief_path.read_text(encoding="utf-8")

    final_prepare = subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", "prepare", "--slug", slug, "--seed", str(seed_path), "--through", "draft"],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        text=True,
        capture_output=True,
        check=True,
    )
    assert "draft\t" in final_prepare.stdout
    assert (repo / "posts" / slug / "draft.qmd").exists()
    assert "Custom review note." in brief_path.read_text(encoding="utf-8")
