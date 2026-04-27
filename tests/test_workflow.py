from __future__ import annotations

from pathlib import Path

import yaml

from tests.conftest import parse_kv, run_cli


def _seed_strategy(strategy_path: Path) -> None:
    text = strategy_path.read_text(encoding="utf-8")
    replacements = {
        "[REQUIRED: name the primary reader and the job they are trying to do.]": "Operators of AI eval pipelines.",
        "[REQUIRED: confirm or replace this with the user's preferred voice.]": "",
        "[REQUIRED: edit these guardrails until they match the user's expectations for the piece.]": "",
        "[REQUIRED: add or remove points until this captures the non-negotiable substance of the post.]": "",
        "[REQUIRED: record any tones, claims, examples, or framing that should be avoided.]": "",
        "- [REQUIRED: What specific reader or buyer context should shape the framing?]": "- Help eng leads decide whether to adopt this workflow.",
        "- [REQUIRED: Which examples, edge cases, or practical details are mandatory for this audience?]": "- Include one example, one tradeoff, one boundary.",
        "- [REQUIRED: What should the post sound like, and what should it never sound like?]": "- Practitioner voice, not marketing.",
        "- [REQUIRED: What practical takeaway should the reader leave with?]": "- A concrete decision rule.",
        "- [ ] Audience is specific enough to guide structure and examples.": "- [x] Audience is specific enough to guide structure and examples.",
        "- [ ] Target voice reflects the user's actual preference, not the default.": "- [x] Target voice reflects the user's actual preference, not the default.",
        "- [ ] Style guardrails are concrete enough to guide generation.": "- [x] Style guardrails are concrete enough to guide generation.",
        "- [ ] Must-cover points capture the non-negotiable substance of the post.": "- [x] Must-cover points capture the non-negotiable substance of the post.",
        "- [ ] Must-avoid rules are explicit.": "- [x] Must-avoid rules are explicit.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    strategy_path.write_text(text, encoding="utf-8")


def _replace_outline(outline_path: Path) -> None:
    outline_path.write_text(
        "# Outline\n\nTitle: Example post\n\n"
        "## Why this topic confuses operators\n- bullet\n\n"
        "## The distinction that matters most\n- bullet\n\n"
        "## What to do with it\n- bullet\n",
        encoding="utf-8",
    )


def test_full_pipeline_through_draft_scaffold(fresh_repo: Path) -> None:
    repo = fresh_repo
    slug = "example-post"

    out = parse_kv(run_cli(repo, "new-post", "--slug", slug, "--topic", "Example post").stdout)
    assert out["slug"] == slug
    meta_path = repo / "posts" / slug / "meta.yaml"
    assert meta_path.exists()
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
    assert meta["preset"] == "default"

    run_cli(repo, "generate-strategy", "--slug", slug)
    strategy_path = repo / "posts" / slug / "strategy.md"
    assert strategy_path.exists()
    _seed_strategy(strategy_path)

    blocked = run_cli(repo, "generate-outline", "--slug", slug, check=False)
    assert blocked.returncode != 0
    assert "decide-discovery" in (blocked.stdout + blocked.stderr)

    run_cli(repo, "decide-discovery", "--slug", slug, "--decision", "no")
    run_cli(repo, "generate-outline", "--slug", slug)
    outline_path = repo / "posts" / slug / "outline.md"
    _replace_outline(outline_path)

    blocked_draft = run_cli(repo, "generate-draft", "--slug", slug, check=False)
    assert blocked_draft.returncode != 0
    assert "approve-outline" in (blocked_draft.stdout + blocked_draft.stderr)

    run_cli(repo, "approve-outline", "--slug", slug)
    run_cli(repo, "generate-draft", "--slug", slug)
    draft_path = repo / "posts" / slug / "draft.html"
    assert draft_path.exists()
    assert "<main" in draft_path.read_text(encoding="utf-8")


def test_approve_outline_rejects_generic_headings(fresh_repo: Path) -> None:
    repo = fresh_repo
    slug = "generic-outline"
    run_cli(repo, "new-post", "--slug", slug, "--topic", "Generic outline test")
    run_cli(repo, "generate-strategy", "--slug", slug)
    _seed_strategy(repo / "posts" / slug / "strategy.md")
    run_cli(repo, "decide-discovery", "--slug", slug, "--decision", "no")
    run_cli(repo, "generate-outline", "--slug", slug)
    (repo / "posts" / slug / "outline.md").write_text(
        "# Outline\n\n## Hook\n- bullet\n\n## Body section 1\n- bullet\n",
        encoding="utf-8",
    )
    blocked = run_cli(repo, "approve-outline", "--slug", slug, check=False)
    assert blocked.returncode != 0
    assert "publishable, reader-facing section title" in (blocked.stdout + blocked.stderr)


def test_verify_inserts_programmatic_markers(fresh_repo: Path) -> None:
    repo = fresh_repo
    slug = "verify-smoke"
    run_cli(repo, "new-post", "--slug", slug, "--topic", "Verify smoke")
    run_cli(repo, "generate-strategy", "--slug", slug)
    _seed_strategy(repo / "posts" / slug / "strategy.md")
    run_cli(repo, "decide-discovery", "--slug", slug, "--decision", "no")
    run_cli(repo, "generate-outline", "--slug", slug)
    _replace_outline(repo / "posts" / slug / "outline.md")
    run_cli(repo, "approve-outline", "--slug", slug)
    run_cli(repo, "generate-draft", "--slug", slug)

    draft_path = repo / "posts" / slug / "draft.html"
    text = draft_path.read_text(encoding="utf-8")
    text = text.replace(
        "<main data-content>",
        '<main data-content><h1>Bad post</h1><p>This framework is revolutionary — really.</p>',
        1,
    )
    # also remove the auto-inserted h1 inside main from generate-draft
    text = text.replace("</main>", "</main>", 1)
    draft_path.write_text(text, encoding="utf-8")

    result = parse_kv(run_cli(repo, "verify", "--slug", slug, check=False).stdout)
    # marker_count printed even if Playwright not available
    assert "marker_count" in result
    rewritten = draft_path.read_text(encoding="utf-8")
    assert "fb[one_h1]" in rewritten
