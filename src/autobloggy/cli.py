from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from .artifacts import (
    extract_frontmatter,
    format_markdown_with_frontmatter,
    post_paths,
    read_json,
    read_text,
    write_json,
    write_text,
)
from .checks import run_checks
from .loop import (
    append_results,
    create_attempt,
    create_run,
    load_state,
    save_state,
    stage_prompt_pack,
    summarize_attempt,
    write_diff,
    ensure_results_tsv,
)
from .prepare import existing_strategy_path, outline_approval_issues, parse_input, resolve_input_path, run_prepare, strategy_approval_issues
from .scoring import is_strict_improvement
from .tasks import choose_next_task
from .utils import ensure_dir, now_iso, repo_root
from .verifiers import write_verifier_bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="autobloggy")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--slug", required=True)
    prepare.add_argument("--input", dest="input_path")
    prepare.add_argument("--seed", dest="legacy_seed_path")
    prepare.add_argument("--through", choices=["strategy", "brief", "outline", "draft"], default="strategy")

    approve = subparsers.add_parser("approve-strategy")
    approve.add_argument("--slug", required=True)

    approve_legacy = subparsers.add_parser("approve-brief")
    approve_legacy.add_argument("--slug", required=True)

    approve_outline = subparsers.add_parser("approve-outline")
    approve_outline.add_argument("--slug", required=True)

    stage = subparsers.add_parser("stage-attempt")
    stage.add_argument("--slug", required=True)
    stage.add_argument("--run-id")

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


def command_prepare(args: argparse.Namespace) -> int:
    repo_root()
    input_arg = args.input_path or args.legacy_seed_path
    if not input_arg:
        raise SystemExit("prepare requires `--input`.")
    input_path = resolve_input_path(Path(input_arg).resolve())
    parse_input(input_path)
    paths = post_paths(args.slug)
    strategy_path = existing_strategy_path(paths)
    through = "strategy" if args.through == "brief" else args.through
    if through == "draft":
        if not strategy_path.exists():
            generated = run_prepare(args.slug, input_path, "strategy")
            for key, value in generated.items():
                print(f"{key}\t{value}")
            raise SystemExit(
                "Strategy generated for review. Approve it with `autobloggy approve-strategy --slug "
                f"{args.slug}` before generating a draft."
            )
        frontmatter, _ = extract_frontmatter(read_text(strategy_path))
        if frontmatter.get("status") != "approved":
            raise SystemExit(
                "Strategy is not approved. Review `posts/{slug}/strategy.md` and run "
                "`autobloggy approve-strategy --slug {slug}` before generating a draft.".format(
                    slug=args.slug
                )
            )
        if not paths.outline.exists():
            generated = run_prepare(args.slug, input_path, "outline")
            for key, value in generated.items():
                print(f"{key}\t{value}")
            raise SystemExit(
                "Outline generated. Open posts/{slug}/outline.md and review the sections and\n"
                "talking points. Edit freely — the outline is yours to reshape before the first\n"
                "draft is written. When it looks right, run:\n\n"
                "    autobloggy approve-outline --slug {slug}".format(slug=args.slug)
            )
        outline_fm, _ = extract_frontmatter(read_text(paths.outline))
        if outline_fm.get("status") != "approved":
            raise SystemExit(
                "Outline is not yet approved. Review posts/{slug}/outline.md, make any edits,\n"
                "then run:\n\n"
                "    autobloggy approve-outline --slug {slug}\n\n"
                "to generate the first draft.".format(slug=args.slug)
            )
    generated = run_prepare(args.slug, input_path, through)
    for key, value in generated.items():
        print(f"{key}\t{value}")
    return 0


def command_approve_strategy(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    strategy_path = existing_strategy_path(paths)
    if not strategy_path.exists():
        raise FileNotFoundError(f"Strategy does not exist: {paths.strategy}")
    strategy_text = read_text(strategy_path)
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
        raise FileNotFoundError("Post artifacts are incomplete. Run prepare first.")

    if args.run_id:
        run_root = paths.runs / args.run_id
        ensure_dir(run_root / "attempts")
        ensure_results_tsv(run_root / "results.tsv")
        run_id = args.run_id
    else:
        run_id, run_root = create_run(paths.root)

    attempt_id, attempt_root = create_attempt(run_root, paths.draft, run_id)
    ensure_dir(run_root)
    baseline = summarize_attempt(run_id, "baseline", run_root / "attempts" / attempt_id, paths.draft)
    check_summary = run_checks(paths.draft)
    task = choose_next_task(check_summary.model_dump(mode="json"), baseline)
    prompt_path = stage_prompt_pack(attempt_root, args.slug, task)
    write_json(attempt_root / "next-task.json", task)
    write_json(attempt_root / "baseline-summary.json", baseline.model_dump(mode="json"))
    state = load_state(run_root, run_id)
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
    for key, value in written.items():
        print(f"{key}\t{value}")
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
        "prepare": command_prepare,
        "approve-strategy": command_approve_strategy,
        "approve-brief": command_approve_strategy,
        "approve-outline": command_approve_outline,
        "stage-attempt": command_stage_attempt,
        "check": command_check,
        "verify": command_verify,
        "evaluate": command_evaluate,
    }
    return command_map[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
