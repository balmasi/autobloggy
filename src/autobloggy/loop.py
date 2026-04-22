from __future__ import annotations

import csv
import difflib
import shutil
from pathlib import Path

from .artifacts import extract_frontmatter, post_paths, read_json, read_text, write_json, write_text
from .checks import run_checks
from .models import EvaluationSummary, RunState, VerifierVerdict
from .presets import default_preset_name, preset_paths, repo_relative_path
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
    base_run_id = now_iso().replace(":", "-")
    run_id = base_run_id
    suffix = 1
    run_root = post_root / "runs" / run_id
    while run_root.exists():
        run_id = f"{base_run_id}-{suffix:02d}"
        run_root = post_root / "runs" / run_id
        suffix += 1
    run_root = ensure_dir(run_root)
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
    paths = post_paths(slug)
    strategy_frontmatter, _ = extract_frontmatter(read_text(paths.strategy))
    preset_name = str(strategy_frontmatter.get("preset") or default_preset_name())
    reference_files = [
        "program.md",
        repo_relative_path(paths.strategy),
    ]
    if paths.outline.exists():
        reference_files.append(repo_relative_path(paths.outline))

    preset_file_keys = (
        "preset_strategy_template",
        "preset_writing_guide",
        "preset_brand_guide",
    )
    preset_files = [str(strategy_frontmatter.get(key) or "").strip() for key in preset_file_keys]
    if not all(preset_files):
        preset = preset_paths(preset_name)
        preset_files = [
            repo_relative_path(preset.strategy_template),
            repo_relative_path(preset.writing_guide),
            repo_relative_path(preset.brand_guide),
        ]
    reference_files.extend(preset_files)

    batch = task.get("batch") or []
    batch_extras = [item for item in batch if item.get("id") != task["task"]]
    batch_lines: list[str] = []
    if task["priority"] == "deterministic_blockers" and batch_extras:
        batch_lines.append("")
        batch_lines.append("Also fix these deterministic blockers in the same edit:")
        batch_lines.extend(f"- {item['id']}: {item['reason']}" for item in batch_extras)

    content = "\n".join(
        [
            f"# Attempt Prompt: {slug}",
            "",
            f"Active preset: {preset_name}",
            "",
            "Read-only context:",
            *[f"- {path}" for path in reference_files],
            "",
            "Editable files:",
            "- draft.qmd",
            "",
            f"Priority lane: {task['priority']}",
            f"Task: {task['task']}",
            f"Reason: {task['reason']}",
            *batch_lines,
            "",
            "Fix every deterministic blocker listed above in a single edit. Keep semantic and stylistic changes narrow to the primary task.",
            "Read the context files first. Do not edit strategy.md, outline.md, program.md, config.yaml, or preset files.",
        ]
    )
    path = attempt_dir / "prompt-pack.md"
    write_text(path, content)
    return path
