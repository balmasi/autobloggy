from __future__ import annotations

import csv
import difflib
import shutil
from pathlib import Path

from .artifacts import read_json, read_text, write_json, write_text
from .checks import run_checks
from .models import EvaluationSummary, RunState, VerifierVerdict
from .utils import ensure_dir, now_iso
from .verifiers import VERIFIER_SPECS


RESULTS_HEADER = [
    "timestamp",
    "attempt_id",
    "task",
    "decision",
    "blocker_count",
    "must_have_verifier_fail_count",
    "improvement_fail_count",
    "readability_penalty",
    "banned_pattern_count",
    "rationale",
]


def ensure_results_tsv(path: Path) -> None:
    if path.exists():
        return
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(RESULTS_HEADER)

def collect_verdict_summary(attempt_dir: Path) -> tuple[int, int, list[str]]:
    verdict_dir = attempt_dir / "verdicts"
    verdict_map: dict[str, VerifierVerdict] = {}
    if verdict_dir.exists():
        for verdict_path in sorted(verdict_dir.glob("*.json")):
            verdict = VerifierVerdict.model_validate(read_json(verdict_path))
            verdict_map[verdict.verifier] = verdict
    must_have_failures = 0
    improvement_failures = 0
    missing: list[str] = []

    for verifier, must_have, _ in VERIFIER_SPECS:
        verdict = verdict_map.get(verifier)
        if verdict is None or verdict.status != "pass":
            if must_have:
                must_have_failures += 1
            else:
                improvement_failures += 1
            missing.append(verifier)
    return must_have_failures, improvement_failures, missing


def summarize_attempt(run_id: str, attempt_id: str, attempt_dir: Path, draft_path: Path) -> EvaluationSummary:
    check_summary = run_checks(draft_path)
    must_have_failures, improvement_failures, missing = collect_verdict_summary(attempt_dir)
    passes_baseline = check_summary.blocker_count == 0 and must_have_failures == 0
    acceptance_tuple = (
        check_summary.blocker_count,
        must_have_failures,
        improvement_failures,
        check_summary.readability_penalty,
        check_summary.banned_pattern_count,
    )
    return EvaluationSummary(
        run_id=run_id,
        attempt_id=attempt_id,
        target=str(draft_path),
        blocker_count=check_summary.blocker_count,
        must_have_verifier_fail_count=must_have_failures,
        improvement_fail_count=improvement_failures,
        readability_penalty=check_summary.readability_penalty,
        banned_pattern_count=check_summary.banned_pattern_count,
        passes_baseline=passes_baseline,
        acceptance_tuple=acceptance_tuple,
        missing_verdicts=missing,
    )


def state_path(run_root: Path) -> Path:
    return run_root / "state.json"


def load_state(run_root: Path, run_id: str) -> RunState:
    path = state_path(run_root)
    if not path.exists():
        return RunState(run_id=run_id)
    return RunState.model_validate(read_json(path))


def save_state(run_root: Path, state: RunState) -> None:
    write_json(state_path(run_root), state.model_dump(mode="json"))


def create_run(post_root: Path) -> tuple[str, Path]:
    run_id = now_iso().replace(":", "-")
    run_root = ensure_dir(post_root / "runs" / run_id)
    ensure_dir(run_root / "attempts")
    ensure_results_tsv(run_root / "results.tsv")
    return run_id, run_root


def create_attempt(run_root: Path, draft_path: Path, run_id: str) -> tuple[str, Path]:
    state = load_state(run_root, run_id)
    attempt_number = state.latest_attempt + 1
    attempt_id = f"attempt-{attempt_number:03d}"
    attempt_root = ensure_dir(run_root / "attempts" / attempt_id)
    shutil.copy2(draft_path, attempt_root / "draft.qmd")
    state.latest_attempt = attempt_number
    save_state(run_root, state)
    return attempt_id, attempt_root


def write_diff(current_path: Path, candidate_path: Path, diff_path: Path) -> None:
    current = read_text(current_path).splitlines(keepends=True)
    candidate = read_text(candidate_path).splitlines(keepends=True)
    diff = "".join(
        difflib.unified_diff(
            current,
            candidate,
            fromfile=str(current_path),
            tofile=str(candidate_path),
        )
    )
    write_text(diff_path, diff)


def append_results(results_path: Path, attempt_id: str, task: str, decision: str, summary: EvaluationSummary, rationale: str) -> None:
    ensure_results_tsv(results_path)
    with results_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(
            [
                now_iso(),
                attempt_id,
                task,
                decision,
                summary.blocker_count,
                summary.must_have_verifier_fail_count,
                summary.improvement_fail_count,
                summary.readability_penalty,
                summary.banned_pattern_count,
                rationale,
            ]
        )


def stage_prompt_pack(attempt_dir: Path, slug: str, task: dict) -> Path:
    content = "\n".join(
        [
            f"# Attempt Prompt: {slug}",
            "",
            "Editable files:",
            "- draft.qmd",
            "",
            f"Priority lane: {task['priority']}",
            f"Task: {task['task']}",
            f"Reason: {task['reason']}",
            "",
            "Keep changes narrow. Do not edit outline.md, strategy.md, program.md, or config.yaml.",
        ]
    )
    path = attempt_dir / "prompt-pack.md"
    write_text(path, content)
    return path
