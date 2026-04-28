from __future__ import annotations

from pathlib import Path

import yaml

from autobloggy.verify import DEFAULT_VIEWPORT_WIDTHS, _viewport_widths
from tests.conftest import parse_kv, run_cli


def _completed_brief(title: str = "Example post") -> str:
    return f"""# Blog Brief: {title}

## Generation Context

- Preset: `default`
- Intake depth: `fast`
- Brand: `presets/default/brand_guide.md`
- Writing: `presets/default/writing_guide.md`
- Format: `presets/default/formats/blog.md`
- Audience: `presets/default/audience/general.md`
- HTML template: `presets/default/template.html`
- Quality criteria: `prompts/quality_criteria.md`
- Prepared source manifest: `inputs/prepared/manifest.yaml`

## Goal

Help operators understand where eval loops break before they trust the output.

## Target Reader

Engineering and product leaders building AI eval pipelines.

## Core Thesis

Eval loops fail when teams optimize the loop mechanics before defining the decision the eval should support.

## Angle

The post focuses on operational failure modes rather than generic eval best practices.

## Scope

Cover data, rubric, and review-loop failures. Do not cover model training.

## Evidence

Use the prepared intake source and any source files listed in the manifest.

## Full Outline

### The loop fails before the model does

- Explain the decision gap.

### Rubrics turn vague when ownership is unclear

- Show why reviewer incentives matter.

### A useful eval loop starts with a decision rule

- Give the reader an operating checklist.

## Required Points

- Define the decision the eval supports.
- Include a practical failure mode.

## Things To Avoid

- Do not claim evals are useless.
- Do not use hype language.

## Quality Bar

Use `prompts/quality_criteria.md`.

Post-specific checks:

- Every section should name a concrete operational consequence.
"""


def test_full_pipeline_through_draft_scaffold(fresh_repo: Path) -> None:
    repo = fresh_repo
    slug = "example-post"

    out = parse_kv(run_cli(repo, "prep", "--slug", slug, "--topic", "Example post").stdout)
    assert out["slug"] == slug
    post_root = repo / "posts" / slug
    assert (post_root / "blog_brief.md").exists()
    assert (post_root / "inputs" / "prepared" / "manifest.yaml").exists()
    assert not (post_root / "strategy.md").exists()
    assert not (post_root / "outline.md").exists()

    meta = yaml.safe_load((post_root / "meta.yaml").read_text(encoding="utf-8"))
    assert meta["preset"] == "default"
    assert meta["intake_depth"] == "fast"
    assert meta["selections"]["html_template"] == "general"

    blocked_approval = run_cli(repo, "approve-brief", "--slug", slug, check=False)
    assert blocked_approval.returncode != 0
    assert "still contains `[AUTO_FILL]`" in (blocked_approval.stdout + blocked_approval.stderr)

    (post_root / "blog_brief.md").write_text(_completed_brief("Example post"), encoding="utf-8")

    blocked_draft = run_cli(repo, "generate-draft", "--slug", slug, check=False)
    assert blocked_draft.returncode != 0
    assert "approve-brief" in (blocked_draft.stdout + blocked_draft.stderr)

    run_cli(repo, "approve-brief", "--slug", slug)
    run_cli(repo, "generate-draft", "--slug", slug)
    draft_path = post_root / "draft.html"
    draft = draft_path.read_text(encoding="utf-8")
    assert "<title>Example post</title>" in draft
    assert "<h1>Example post</h1>" in draft


def test_prep_copies_sources_and_writes_structural_manifest(fresh_repo: Path, tmp_path: Path) -> None:
    repo = fresh_repo
    source = tmp_path / "notes.txt"
    source.write_text("The source says churn rose while NPS also rose.", encoding="utf-8")

    run_cli(repo, "prep", "--slug", "source-post", "--topic", "NPS is lossy", "--source", str(source))
    post_root = repo / "posts" / "source-post"
    assert (post_root / "inputs" / "raw" / "notes.txt").exists()
    prepared = post_root / "inputs" / "prepared" / "source-001" / "source.md"
    assert "churn rose" in prepared.read_text(encoding="utf-8")

    manifest = yaml.safe_load((post_root / "inputs" / "prepared" / "manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["sources"][0]["id"] == "intake"
    assert manifest["sources"][1]["id"] == "source-001"
    assert manifest["sources"][1]["path"] == "inputs/prepared/source-001/source.md"
    assert manifest["sources"][1]["origins"] == ["inputs/raw/notes.txt"]


def test_approve_brief_rejects_missing_outline_headings(fresh_repo: Path) -> None:
    repo = fresh_repo
    slug = "bad-brief"
    run_cli(repo, "prep", "--slug", slug, "--topic", "Bad brief")
    text = (
        _completed_brief("Bad brief")
        .replace("### Rubrics turn vague when ownership is unclear", "#### Too deep")
        .replace("### A useful eval loop starts with a decision rule", "#### Also too deep")
    )
    (repo / "posts" / slug / "blog_brief.md").write_text(text, encoding="utf-8")

    blocked = run_cli(repo, "approve-brief", "--slug", slug, check=False)
    assert blocked.returncode != 0
    assert "at least two `###` section headings" in (blocked.stdout + blocked.stderr)


def test_georgian_preset_uses_child_resources_and_parent_fallback(fresh_repo: Path) -> None:
    repo = fresh_repo
    run_cli(
        repo,
        "prep",
        "--slug",
        "georgian-post",
        "--topic",
        "NPS is lossy",
        "--preset",
        "georgian",
        "--intake-depth",
        "guided",
        "--select",
        "audience=ai-founders",
        "--select",
        "format=blog",
    )
    brief = (repo / "posts" / "georgian-post" / "blog_brief.md").read_text(encoding="utf-8")
    assert "`presets/georgian/brand_guide.md`" in brief
    assert "`presets/georgian/audience/ai_founders.md`" in brief
    assert "`presets/default/formats/blog.md`" in brief


def test_guided_intake_depth_requires_explicit_selection(fresh_repo: Path) -> None:
    blocked = run_cli(
        fresh_repo,
        "prep",
        "--slug",
        "guided-post",
        "--topic",
        "NPS is lossy",
        "--intake-depth",
        "guided",
        check=False,
    )
    assert blocked.returncode != 0
    assert "requires explicit --select values" in (blocked.stdout + blocked.stderr)


def test_unknown_selection_reports_available_values(fresh_repo: Path) -> None:
    blocked = run_cli(
        fresh_repo,
        "prep",
        "--slug",
        "bad-select",
        "--topic",
        "NPS is lossy",
        "--select",
        "format=nope",
        check=False,
    )
    assert blocked.returncode != 0
    assert "Available values: blog, guide" in (blocked.stdout + blocked.stderr)


def test_missing_selected_resource_fails_clearly(fresh_repo: Path) -> None:
    preset_path = fresh_repo / "presets" / "default" / "preset.yaml"
    preset_path.write_text(
        preset_path.read_text(encoding="utf-8").replace("general: template.html", "general: missing-template.html"),
        encoding="utf-8",
    )
    blocked = run_cli(
        fresh_repo,
        "prep",
        "--slug",
        "missing-resource",
        "--topic",
        "Broken template",
        check=False,
    )
    assert blocked.returncode != 0
    assert "points to missing resource" in (blocked.stdout + blocked.stderr)
    assert "missing-template.html" in (blocked.stdout + blocked.stderr)


def test_verify_inserts_programmatic_markers(fresh_repo: Path) -> None:
    repo = fresh_repo
    slug = "verify-smoke"
    run_cli(repo, "prep", "--slug", slug, "--topic", "Verify smoke")
    post_root = repo / "posts" / slug
    (post_root / "blog_brief.md").write_text(_completed_brief("Verify smoke"), encoding="utf-8")
    run_cli(repo, "approve-brief", "--slug", slug)
    run_cli(repo, "generate-draft", "--slug", slug)

    draft_path = post_root / "draft.html"
    text = draft_path.read_text(encoding="utf-8")
    text = text.replace(
        "<main data-content>",
        '<main data-content><h1>Bad post</h1><p>This framework is revolutionary - really.</p>',
        1,
    )
    draft_path.write_text(text, encoding="utf-8")

    result = parse_kv(run_cli(repo, "verify", "--slug", slug, check=False).stdout)
    assert "marker_count" in result
    rewritten = draft_path.read_text(encoding="utf-8")
    assert "fb[one_h1]" in rewritten
    pack = (post_root / ".verify" / "verify-pack.md").read_text(encoding="utf-8")
    assert "## Marker instructions" in pack
    assert "## Quality criteria" in pack
    assert "Blog brief:" in pack


def test_verify_viewport_widths_come_from_config(fresh_repo: Path) -> None:
    config_path = fresh_repo / "config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["verify"]["viewport_widths"] = [360, 768]
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    assert _viewport_widths(fresh_repo) == (360, 768)


def test_verify_viewport_widths_fall_back_when_unset(fresh_repo: Path) -> None:
    config_path = fresh_repo / "config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["verify"].pop("viewport_widths")
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    assert _viewport_widths(fresh_repo) == DEFAULT_VIEWPORT_WIDTHS
