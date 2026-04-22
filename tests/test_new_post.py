from __future__ import annotations

from pathlib import Path

from autobloggy.artifacts import extract_frontmatter, format_markdown_with_frontmatter
from tests.helpers import copy_repo, parse_kv, resolve_generated_outline, resolve_generated_strategy, run_cli, run_cli_failure


def test_new_post_supports_topic_only(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)

    result = parse_kv(run_cli(repo, "new-post", "--topic", "Why AI eval loops fail").stdout)
    slug = result["slug"]

    input_path = repo / "posts" / slug / "inputs" / "user_provided" / "input.md"
    strategy_path = repo / "posts" / slug / "strategy.md"
    assert slug == "why-ai-eval-loops-fail"
    assert input_path.exists()
    assert strategy_path.exists()

    frontmatter, _ = extract_frontmatter(strategy_path.read_text(encoding="utf-8"))
    assert frontmatter["input_path"] == str(input_path)
    assert frontmatter["input_root"] == str(input_path.parent)
    assert frontmatter["preset"] == "default"


def test_new_post_uses_existing_post_input_folder_by_default(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)

    slug = "folder-first"
    input_root = repo / "posts" / slug / "inputs" / "user_provided"
    input_root.mkdir(parents=True, exist_ok=True)
    seeded = input_root / "notes.md"
    seeded.write_text(
        """---
title: Folder First
---

# Folder First

Operators want one place to drop source files before the writing flow starts.
""",
        encoding="utf-8",
    )

    result = parse_kv(run_cli(repo, "new-post", "--slug", slug).stdout)
    assert result["slug"] == slug
    assert (input_root / "input.md").exists()
    assert (repo / "posts" / slug / "strategy.md").exists()
    assert "`notes.md`" in (input_root / "input.md").read_text(encoding="utf-8")


def test_new_post_copies_source_files_into_user_provided(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)

    source_md = tmp_path / "source-notes.md"
    source_md.write_text(
        """---
title: Source Notes
---

# Source Notes

This note should be copied into the post input bundle.
""",
        encoding="utf-8",
    )
    source_txt = tmp_path / "overview.txt"
    source_txt.write_text("A second supporting file.", encoding="utf-8")

    slug = "copied-sources"
    run_cli(
        repo,
        "new-post",
        "--slug",
        slug,
        "--topic",
        "Copied sources should land in the default post input folder.",
        "--source",
        str(source_md),
        "--source",
        str(source_txt),
    )

    supporting_root = repo / "posts" / slug / "inputs" / "user_provided" / "supporting"
    assert (supporting_root / "source-notes.md").exists()
    assert (supporting_root / "overview.txt").exists()


def test_new_post_supports_explicit_preset(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)

    preset_root = repo / "presets" / "acme"
    preset_root.mkdir(parents=True, exist_ok=True)
    (preset_root / "strategy_template.md").write_text((repo / "presets" / "default" / "strategy_template.md").read_text(encoding="utf-8"), encoding="utf-8")
    (preset_root / "writing_guide.md").write_text("# ACME Writing Guide\n", encoding="utf-8")
    (preset_root / "brand_guide.md").write_text("# ACME Brand Guide\n", encoding="utf-8")

    slug = "explicit-preset"
    run_cli(repo, "new-post", "--slug", slug, "--topic", "Explicit preset", "--preset", "acme")

    strategy_text = (repo / "posts" / slug / "strategy.md").read_text(encoding="utf-8")
    frontmatter, _ = extract_frontmatter(strategy_text)
    assert frontmatter["preset"] == "acme"
    assert "presets/acme/writing_guide.md" in strategy_text


def test_new_preset_scaffolds_from_default(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)

    result = parse_kv(run_cli(repo, "new-preset", "--name", "acme").stdout)
    preset_root = repo / "presets" / "acme"

    assert result["preset"] == str(preset_root)
    assert (preset_root / "strategy_template.md").exists()
    assert (preset_root / "writing_guide.md").exists()
    assert (preset_root / "brand_guide.md").exists()
    assert (preset_root / "strategy_template.md").read_text(encoding="utf-8") == (
        repo / "presets" / "default" / "strategy_template.md"
    ).read_text(encoding="utf-8")


def test_generate_outline_and_generate_draft_require_approvals(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)

    slug = "review-gated"
    run_cli(repo, "new-post", "--slug", slug, "--topic", "Review-gated post")
    strategy_path = repo / "posts" / slug / "strategy.md"

    blocked_outline = run_cli_failure(repo, "generate-outline", "--slug", slug)
    assert blocked_outline.returncode != 0
    assert "approve-strategy" in (blocked_outline.stdout + blocked_outline.stderr)

    resolve_generated_strategy(strategy_path)
    run_cli(repo, "approve-strategy", "--slug", slug)

    blocked_without_decision = run_cli_failure(repo, "generate-outline", "--slug", slug)
    assert blocked_without_decision.returncode != 0
    assert "decide-discovery" in (blocked_without_decision.stdout + blocked_without_decision.stderr)

    recorded_decision = parse_kv(run_cli(repo, "decide-discovery", "--slug", slug, "--decision", "no").stdout)
    assert recorded_decision["discovery_decision"] == "no"

    generated_outline = parse_kv(run_cli(repo, "generate-outline", "--slug", slug).stdout)
    assert generated_outline["outline"] == str(repo / "posts" / slug / "outline.md")

    resolve_generated_outline(repo / "posts" / slug / "outline.md")

    blocked_draft = run_cli_failure(repo, "generate-draft", "--slug", slug)
    assert blocked_draft.returncode != 0
    assert "approve-outline" in (blocked_draft.stdout + blocked_draft.stderr)

    run_cli(repo, "approve-outline", "--slug", slug)
    generated_draft = parse_kv(run_cli(repo, "generate-draft", "--slug", slug).stdout)
    assert generated_draft["draft"] == str(repo / "posts" / slug / "draft.qmd")


def test_generate_outline_requires_discovery_output_when_decision_is_yes(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)

    slug = "discovery-gated"
    run_cli(repo, "new-post", "--slug", slug, "--topic", "Discovery-gated post")
    strategy_path = repo / "posts" / slug / "strategy.md"
    resolve_generated_strategy(strategy_path)
    run_cli(repo, "approve-strategy", "--slug", slug)
    run_cli(repo, "decide-discovery", "--slug", slug, "--decision", "yes")

    blocked_outline = run_cli_failure(repo, "generate-outline", "--slug", slug)
    assert blocked_outline.returncode != 0
    assert f"posts/{slug}/inputs/discovery/discovery.md" in (blocked_outline.stdout + blocked_outline.stderr)

    discovery_summary = repo / "posts" / slug / "inputs" / "discovery" / "discovery.md"
    discovery_summary.parent.mkdir(parents=True, exist_ok=True)
    discovery_summary.write_text("# Discovery\n\nThe operator chose to run discovery.\n", encoding="utf-8")

    generated_outline = parse_kv(run_cli(repo, "generate-outline", "--slug", slug).stdout)
    assert generated_outline["outline"] == str(repo / "posts" / slug / "outline.md")


def test_generate_draft_quotes_yaml_sensitive_titles(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)

    slug = "colon-title"
    run_cli(repo, "new-post", "--slug", slug, "--topic", "Claude terms: connectors, skills, plugins, and MCP")
    strategy_path = repo / "posts" / slug / "strategy.md"
    resolve_generated_strategy(strategy_path)
    run_cli(repo, "approve-strategy", "--slug", slug)
    run_cli(repo, "decide-discovery", "--slug", slug, "--decision", "no")
    run_cli(repo, "generate-outline", "--slug", slug)
    resolve_generated_outline(repo / "posts" / slug / "outline.md")
    run_cli(repo, "approve-outline", "--slug", slug)
    run_cli(repo, "generate-draft", "--slug", slug)

    draft_path = repo / "posts" / slug / "draft.qmd"
    frontmatter, _ = extract_frontmatter(draft_path.read_text(encoding="utf-8"))
    assert frontmatter["title"] == "Claude terms: connectors, skills, plugins, and MCP"

    staged = parse_kv(run_cli(repo, "stage-attempt", "--slug", slug).stdout)
    attempt_root = repo / "posts" / slug / "runs" / staged["run_id"] / "attempts" / staged["attempt_id"]
    assert attempt_root.exists()


def test_approve_outline_rejects_generic_outline_headings(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)

    slug = "generic-outline"
    run_cli(repo, "new-post", "--slug", slug, "--topic", "Generic outline headings")
    strategy_path = repo / "posts" / slug / "strategy.md"
    resolve_generated_strategy(strategy_path)
    run_cli(repo, "approve-strategy", "--slug", slug)
    run_cli(repo, "decide-discovery", "--slug", slug, "--decision", "no")
    run_cli(repo, "generate-outline", "--slug", slug)

    outline_path = repo / "posts" / slug / "outline.md"
    frontmatter, _ = extract_frontmatter(outline_path.read_text(encoding="utf-8"))
    outline_path.write_text(
        format_markdown_with_frontmatter(
            frontmatter,
            "# Outline\n\n## Hook\n- Lead point.\n\n## Body section 1\n- Explain the distinction.\n",
        ),
        encoding="utf-8",
    )

    blocked = run_cli_failure(repo, "approve-outline", "--slug", slug)
    assert blocked.returncode != 0
    assert "publishable, reader-facing section title" in (blocked.stdout + blocked.stderr)
