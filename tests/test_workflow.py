from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import copy_repo, resolve_generated_strategy, run_cli


def parse_kv(stdout: str) -> dict[str, str]:
    pairs = {}
    for line in stdout.strip().splitlines():
        if "\t" in line:
            key, value = line.split("\t", 1)
            pairs[key] = value
    return pairs


def test_stage_attempt_verify_and_evaluate_smoke(repo_root: Path, tmp_path: Path) -> None:
    repo = copy_repo(repo_root, tmp_path)
    slug = "example-post"
    input_path = repo / "tests" / "fixtures" / "example_input.md"
    run_cli(repo, "prepare", "--slug", slug, "--input", str(input_path), "--through", "strategy")
    resolve_generated_strategy(repo / "posts" / slug / "strategy.md")
    run_cli(repo, "approve-strategy", "--slug", slug)
    run_cli(repo, "prepare", "--slug", slug, "--input", str(input_path), "--through", "draft")

    staged = parse_kv(run_cli(repo, "stage-attempt", "--slug", slug).stdout)
    run_id = staged["run_id"]
    attempt_id = staged["attempt_id"]
    attempt_root = repo / "posts" / slug / "runs" / run_id / "attempts" / attempt_id

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
