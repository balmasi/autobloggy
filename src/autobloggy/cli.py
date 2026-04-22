from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from .artifacts import extract_frontmatter, format_markdown_with_frontmatter, post_paths, read_json, read_text, write_json, write_text
from .checks import run_checks
from .loop import (
    append_results,
    create_attempt,
    create_run,
    ensure_results_tsv,
    load_state,
    save_state,
    stage_prompt_pack,
    summarize_attempt,
    write_diff,
)
from .prepare import (
    outline_approval_issues,
    run_generate_draft,
    run_generate_outline,
    run_new_post,
    scaffold_preset,
    strategy_approval_issues,
)
from .scoring import is_strict_improvement
from .tasks import choose_next_task
from .utils import ensure_dir, now_iso, repo_root
from .verifiers import write_verifier_bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="autobloggy")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_post = subparsers.add_parser("new-post")
    new_post.add_argument("--slug")
    new_post.add_argument("--title")
    new_post.add_argument("--topic")
    new_post.add_argument("--source", action="append", default=[], help="File or folder to copy into inputs/user_provided/supporting/.")
    new_post.add_argument("--preset", help="Preset name under presets/<name>. Defaults to config prepare.default_preset.")

    new_preset = subparsers.add_parser("new-preset")
    new_preset.add_argument("--name", required=True)

    generate_outline = subparsers.add_parser("generate-outline")
    generate_outline.add_argument("--slug", required=True)

    generate_draft = subparsers.add_parser("generate-draft")
    generate_draft.add_argument("--slug", required=True)

    decide_discovery = subparsers.add_parser("decide-discovery")
    decide_discovery.add_argument("--slug", required=True)
    decide_discovery.add_argument("--decision", required=True, choices=("yes", "no"))

    approve = subparsers.add_parser("approve-strategy")
    approve.add_argument("--slug", required=True)

    approve_outline = subparsers.add_parser("approve-outline")
    approve_outline.add_argument("--slug", required=True)

    stage = subparsers.add_parser("stage-attempt")
    stage.add_argument("--slug", required=True)
    stage.add_argument("--run-id")
    stage.add_argument("--new-run", action="store_true")

    check = subparsers.add_parser("check")
    check.add_argument("--slug", required=True)
    check.add_argument("--draft")
    check.add_argument("--output")

    verify = subparsers.add_parser("verify")
    verify.add_argument("--slug", required=True)
    verify.add_argument("--run-id", required=True)
    verify.add_argument("--attempt", required=True)

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--slug", required=True)
    evaluate.add_argument("--run-id", required=True)
    evaluate.add_argument("--attempt", required=True)

    return parser.parse_args()


def print_generated(payload: dict[str, str]) -> None:
    for key, value in payload.items():
        print(f"{key}\t{value}")


def command_new_post(args: argparse.Namespace) -> int:
    repo_root()
    try:
        generated = run_new_post(
            slug=args.slug,
            title=args.title,
            topic=args.topic,
            source_paths=[Path(value) for value in args.source],
            preset_name=args.preset,
        )
        print_generated(generated)
        return 0
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def command_new_preset(args: argparse.Namespace) -> int:
    repo_root()
    try:
        preset_root = scaffold_preset(args.name)
        print(f"preset\t{preset_root}")
        return 0
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def command_generate_outline(args: argparse.Namespace) -> int:
    repo_root()
    try:
        generated = run_generate_outline(args.slug)
        print_generated(generated)
        return 0
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def command_generate_draft(args: argparse.Namespace) -> int:
    repo_root()
    try:
        generated = run_generate_draft(args.slug)
        print_generated(generated)
        return 0
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def command_decide_discovery(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    if not paths.strategy.exists():
        raise FileNotFoundError(f"Strategy does not exist: {paths.strategy}")
    strategy_text = read_text(paths.strategy)
    frontmatter, body = extract_frontmatter(strategy_text)
    frontmatter["discovery_decision"] = args.decision
    frontmatter["discovery_decided_at"] = now_iso()
    write_text(paths.strategy, format_markdown_with_frontmatter(frontmatter, body))
    print(f"strategy\t{paths.strategy}")
    print(f"discovery_decision\t{args.decision}")
    return 0


def command_approve_strategy(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    if not paths.strategy.exists():
        raise FileNotFoundError(f"Strategy does not exist: {paths.strategy}")
    strategy_text = read_text(paths.strategy)
    issues = strategy_approval_issues(strategy_text)
    if issues:
        raise SystemExit("Strategy is incomplete:\n- " + "\n- ".join(issues))
    frontmatter, body = extract_frontmatter(strategy_text)
    frontmatter["status"] = "approved"
    frontmatter["approved_at"] = now_iso()
    write_text(paths.strategy, format_markdown_with_frontmatter(frontmatter, body))
    print(f"strategy\t{paths.strategy}")
    return 0


def command_approve_outline(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    if not paths.outline.exists():
        raise FileNotFoundError(f"Outline does not exist: {paths.outline}")
    outline_text = read_text(paths.outline)
    issues = outline_approval_issues(outline_text)
    if issues:
        raise SystemExit("Outline is incomplete:\n- " + "\n- ".join(issues))
    frontmatter, body = extract_frontmatter(outline_text)
    frontmatter["status"] = "approved"
    frontmatter["approved_at"] = now_iso()
    write_text(paths.outline, format_markdown_with_frontmatter(frontmatter, body))
    print(f"outline\t{paths.outline}")
    return 0


def command_stage_attempt(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    if not paths.draft.exists():
        raise FileNotFoundError("Post artifacts are incomplete. Run `autobloggy generate-draft --slug <slug>` first.")

    if args.run_id and args.new_run:
        raise SystemExit("Choose either `--run-id <run-id>` to continue an existing run or `--new-run` to start a fresh run, not both.")

    existing_run_ids = []
    if paths.runs.exists():
        existing_run_ids = sorted(path.name for path in paths.runs.iterdir() if path.is_dir())

    if args.run_id:
        run_root = paths.runs / args.run_id
        if not run_root.exists():
            detail = f" Existing runs: {', '.join(existing_run_ids)}." if existing_run_ids else ""
            raise SystemExit(f"Run `{args.run_id}` does not exist for post `{args.slug}`.{detail}")
        ensure_dir(run_root / "attempts")
        ensure_results_tsv(run_root / "results.tsv")
        run_id = args.run_id
    else:
        if existing_run_ids and not args.new_run:
            latest_run_id = existing_run_ids[-1]
            raise SystemExit(
                "Post already has staged run state. Continue the active run with "
                f"`autobloggy stage-attempt --slug {args.slug} --run-id {latest_run_id}` "
                "or pass `--new-run` to intentionally start a fresh run."
            )
        run_id, run_root = create_run(paths.root)

    state = load_state(run_root, run_id)
    attempt_id, attempt_root = create_attempt(run_root, paths.draft, run_id)
    ensure_dir(run_root)
    baseline = summarize_attempt(run_id, "baseline", run_root / "attempts" / attempt_id, paths.draft)
    check_summary = run_checks(paths.draft)
    task = choose_next_task(check_summary.model_dump(mode="json"), state.accepted_summary or baseline)
    prompt_path = stage_prompt_pack(attempt_root, args.slug, task)
    write_json(attempt_root / "next-task.json", task)
    write_json(attempt_root / "baseline-summary.json", baseline.model_dump(mode="json"))
    if state.accepted_summary is None:
        state.accepted_summary = baseline
        save_state(run_root, state)

    print(f"run_id\t{run_id}")
    print(f"attempt_id\t{attempt_id}")
    print(f"prompt_pack\t{prompt_path}")
    return 0


def command_check(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    draft_path = Path(args.draft) if args.draft else paths.draft
    summary = run_checks(draft_path)
    payload = summary.model_dump(mode="json")
    if args.output:
        write_json(Path(args.output), payload)
        print(args.output)
    else:
        print(payload)
    return 0


def command_verify(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    attempt_root = paths.runs / args.run_id / "attempts" / args.attempt
    if not attempt_root.exists():
        raise FileNotFoundError(f"Attempt does not exist: {attempt_root}")
    written = write_verifier_bundle(attempt_root, attempt_root / "draft.qmd")
    print_generated(written)
    return 0


def command_evaluate(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    run_root = paths.runs / args.run_id
    attempt_root = run_root / "attempts" / args.attempt
    state = load_state(run_root, args.run_id)
    summary = summarize_attempt(args.run_id, args.attempt, attempt_root, attempt_root / "draft.qmd")
    write_json(attempt_root / "check-results.json", run_checks(attempt_root / "draft.qmd").model_dump(mode="json"))
    write_json(attempt_root / "evaluation-summary.json", summary.model_dump(mode="json"))
    write_diff(paths.draft, attempt_root / "draft.qmd", attempt_root / "draft.diff")

    current = state.accepted_summary
    decision = "keep" if summary and is_strict_improvement(summary, current) else "revert"
    rationale = "candidate improved acceptance tuple"
    if decision == "keep":
        shutil.copy2(attempt_root / "draft.qmd", paths.draft)
        state.accepted_summary = summary
        save_state(run_root, state)
    else:
        rationale = "candidate did not strictly improve acceptance tuple"

    task_payload = read_json(attempt_root / "next-task.json") if (attempt_root / "next-task.json").exists() else {"task": "unknown"}
    append_results(run_root / "results.tsv", args.attempt, task_payload["task"], decision, summary, rationale)
    print(f"decision\t{decision}")
    print(f"summary\t{attempt_root / 'evaluation-summary.json'}")
    return 0


def main() -> int:
    args = parse_args()
    command_map = {
        "new-post": command_new_post,
        "new-preset": command_new_preset,
        "generate-outline": command_generate_outline,
        "generate-draft": command_generate_draft,
        "decide-discovery": command_decide_discovery,
        "approve-strategy": command_approve_strategy,
        "approve-outline": command_approve_outline,
        "stage-attempt": command_stage_attempt,
        "check": command_check,
        "verify": command_verify,
        "evaluate": command_evaluate,
    }
    return command_map[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
