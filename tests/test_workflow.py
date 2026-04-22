from __future__ import annotations

import json
from pathlib import Path

from autobloggy.artifacts import read_json
from tests.helpers import copy_repo, parse_kv, resolve_generated_outline, resolve_generated_strategy, run_cli, run_cli_failure


def test_stage_attempt_verify_and_evaluate_smoke(repo_root: Path, tmp_path: Path) -> None:
    repo = copy_repo(repo_root, tmp_path)
    slug = "example-post"
    run_cli(repo, "new-post", "--slug", slug, "--topic", "Example post workflow")
    resolve_generated_strategy(repo / "posts" / slug / "strategy.md")
    run_cli(repo, "approve-strategy", "--slug", slug)
    run_cli(repo, "decide-discovery", "--slug", slug, "--decision", "no")
    run_cli(repo, "generate-outline", "--slug", slug)
    resolve_generated_outline(repo / "posts" / slug / "outline.md")
    run_cli(repo, "approve-outline", "--slug", slug)
    run_cli(repo, "generate-draft", "--slug", slug)

    staged = parse_kv(run_cli(repo, "stage-attempt", "--slug", slug).stdout)
    run_id = staged["run_id"]
    attempt_id = staged["attempt_id"]
    attempt_root = repo / "posts" / slug / "runs" / run_id / "attempts" / attempt_id
    prompt_pack = attempt_root / "prompt-pack.md"
    prompt_text = prompt_pack.read_text(encoding="utf-8")
    assert "Active preset: default" in prompt_text
    assert "- presets/default/writing_guide.md" in prompt_text
    assert "- presets/default/brand_guide.md" in prompt_text

    draft = attempt_root / "draft.qmd"
    draft.write_text(
        draft.read_text(encoding="utf-8").replace(
            "Close with the practical takeaway.\n",
            "Close with the practical takeaway.\n\nA concrete next step helps the reader act on the draft.\n",
        ),
        encoding="utf-8",
    )

    run_cli(repo, "verify", "--slug", slug, "--run-id", run_id, "--attempt", attempt_id)
    verdict_dir = attempt_root / "verdicts"
    for verdict_file in verdict_dir.glob("*.json"):
        payload = json.loads(verdict_file.read_text(encoding="utf-8"))
        payload["status"] = "pass"
        payload["rationale"] = "Test verdict."
        verdict_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    result = parse_kv(run_cli(repo, "evaluate", "--slug", slug, "--run-id", run_id, "--attempt", attempt_id).stdout)
    assert result["decision"] == "keep"
    results_tsv = repo / "posts" / slug / "runs" / run_id / "results.tsv"
    assert results_tsv.exists()
    assert "keep" in results_tsv.read_text(encoding="utf-8")


def test_stage_attempt_advances_to_next_failing_verifier_in_same_run(repo_root: Path, tmp_path: Path) -> None:
    repo = copy_repo(repo_root, tmp_path)
    slug = "verifier-routing"
    run_cli(repo, "new-post", "--slug", slug, "--topic", "Verifier routing")
    resolve_generated_strategy(repo / "posts" / slug / "strategy.md")
    run_cli(repo, "approve-strategy", "--slug", slug)
    run_cli(repo, "decide-discovery", "--slug", slug, "--decision", "no")
    run_cli(repo, "generate-outline", "--slug", slug)
    resolve_generated_outline(repo / "posts" / slug / "outline.md")
    run_cli(repo, "approve-outline", "--slug", slug)
    run_cli(repo, "generate-draft", "--slug", slug)

    staged = parse_kv(run_cli(repo, "stage-attempt", "--slug", slug).stdout)
    run_id = staged["run_id"]
    attempt_id = staged["attempt_id"]
    attempt_root = repo / "posts" / slug / "runs" / run_id / "attempts" / attempt_id

    run_cli(repo, "verify", "--slug", slug, "--run-id", run_id, "--attempt", attempt_id)
    verdict_dir = attempt_root / "verdicts"
    verdict_status = {
        "opening_clarity": "pass",
        "overstatement": "pass",
        "performance_metrics_disclosure": "pass",
        "portfolio_company_disclosure": "pass",
        "paragraph_focus": "fail",
        "voice": "fail",
        "research_citation": "fail",
        "specificity": "fail",
        "so_what": "fail",
        "filler_hype": "fail",
    }
    for verdict_file in verdict_dir.glob("*.json"):
        payload = json.loads(verdict_file.read_text(encoding="utf-8"))
        payload["status"] = verdict_status[payload["verifier"]]
        payload["rationale"] = f"Set by test to {payload['status']}."
        verdict_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    run_cli(repo, "evaluate", "--slug", slug, "--run-id", run_id, "--attempt", attempt_id)

    staged_again = parse_kv(run_cli(repo, "stage-attempt", "--slug", slug, "--run-id", run_id).stdout)
    next_attempt_root = repo / "posts" / slug / "runs" / run_id / "attempts" / staged_again["attempt_id"]
    next_task = read_json(next_attempt_root / "next-task.json")
    assert next_task["task"] == "paragraph_focus"


def test_stage_attempt_requires_explicit_new_run_when_runs_exist(repo_root: Path, tmp_path: Path) -> None:
    repo = copy_repo(repo_root, tmp_path)
    slug = "run-guard"
    run_cli(repo, "new-post", "--slug", slug, "--topic", "Guard accidental fresh runs")
    resolve_generated_strategy(repo / "posts" / slug / "strategy.md")
    run_cli(repo, "approve-strategy", "--slug", slug)
    run_cli(repo, "decide-discovery", "--slug", slug, "--decision", "no")
    run_cli(repo, "generate-outline", "--slug", slug)
    resolve_generated_outline(repo / "posts" / slug / "outline.md")
    run_cli(repo, "approve-outline", "--slug", slug)
    run_cli(repo, "generate-draft", "--slug", slug)

    staged = parse_kv(run_cli(repo, "stage-attempt", "--slug", slug).stdout)
    run_id = staged["run_id"]

    blocked = run_cli_failure(repo, "stage-attempt", "--slug", slug)
    assert blocked.returncode != 0
    combined = blocked.stdout + blocked.stderr
    assert f"--run-id {run_id}" in combined
    assert "--new-run" in combined

    restarted = parse_kv(run_cli(repo, "stage-attempt", "--slug", slug, "--new-run").stdout)
    assert restarted["run_id"] != run_id
