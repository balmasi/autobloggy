from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from .artifacts import (
    extract_frontmatter,
    format_markdown_with_frontmatter,
    post_paths,
    read_claims,
    read_json,
    read_sources,
    read_text,
    write_claims,
    write_json,
    write_sources,
    write_text,
)
from .checks import run_checks
from .loop import (
    append_results,
    collect_claim_issue_count,
    create_attempt,
    create_run,
    load_state,
    save_state,
    stage_prompt_pack,
    summarize_attempt,
    write_diff,
    ensure_results_tsv,
)
from .models import SourceRecord, SourceSnippet
from .prepare import parse_seed, run_prepare
from .scoring import is_strict_improvement
from .tasks import choose_next_task
from .utils import ensure_dir, now_iso, repo_root
from .verifiers import write_verifier_bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="autobloggy")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--slug", required=True)
    prepare.add_argument("--seed", required=True)
    prepare.add_argument("--through", choices=["brief", "outline", "claims", "draft"], default="brief")

    approve = subparsers.add_parser("approve-brief")
    approve.add_argument("--slug", required=True)

    stage = subparsers.add_parser("stage-attempt")
    stage.add_argument("--slug", required=True)
    stage.add_argument("--run-id")

    check = subparsers.add_parser("check")
    check.add_argument("--slug", required=True)
    check.add_argument("--draft")
    check.add_argument("--claims")
    check.add_argument("--sources")
    check.add_argument("--output")

    verify = subparsers.add_parser("verify")
    verify.add_argument("--slug", required=True)
    verify.add_argument("--run-id", required=True)
    verify.add_argument("--attempt", required=True)

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--slug", required=True)
    evaluate.add_argument("--run-id", required=True)
    evaluate.add_argument("--attempt", required=True)

    refresh = subparsers.add_parser("refresh-sources")
    refresh.add_argument("--slug", required=True)
    refresh.add_argument("--source-id", required=True)
    refresh.add_argument("--title", required=True)
    refresh.add_argument("--locator", required=True)
    refresh.add_argument("--snippet", required=True)
    refresh.add_argument("--kind", choices=["url", "local_markdown", "local_pptx", "manual"], default="url")
    refresh.add_argument("--claim-id", action="append", default=[])

    return parser.parse_args()


def command_prepare(args: argparse.Namespace) -> int:
    repo_root()
    seed_path = Path(args.seed).resolve()
    parse_seed(seed_path)
    paths = post_paths(args.slug)
    if args.through in {"claims", "draft"}:
        if not paths.brief.exists():
            generated = run_prepare(args.slug, seed_path, "brief")
            for key, value in generated.items():
                print(f"{key}\t{value}")
            raise SystemExit(
                "Brief generated for review. Approve it with `autobloggy approve-brief --slug "
                f"{args.slug}` before generating claims or a draft."
            )
        frontmatter, _ = extract_frontmatter(read_text(paths.brief))
        if frontmatter.get("status") != "approved":
            raise SystemExit(
                "Brief is not approved. Review `posts/{slug}/brief.md` and run "
                "`autobloggy approve-brief --slug {slug}` before generating claims or a draft.".format(
                    slug=args.slug
                )
            )
    generated = run_prepare(args.slug, seed_path, args.through)
    for key, value in generated.items():
        print(f"{key}\t{value}")
    return 0


def command_approve_brief(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    if not paths.brief.exists():
        raise FileNotFoundError(f"Brief does not exist: {paths.brief}")
    frontmatter, body = extract_frontmatter(read_text(paths.brief))
    frontmatter["status"] = "approved"
    frontmatter["approved_at"] = now_iso()
    write_text(paths.brief, format_markdown_with_frontmatter(frontmatter, body))
    print(f"brief\t{paths.brief}")
    return 0


def command_stage_attempt(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    if not paths.draft.exists() or not paths.claims.exists() or not paths.sources.exists():
        raise FileNotFoundError("Post artifacts are incomplete. Run prepare first.")

    if args.run_id:
        run_root = paths.runs / args.run_id
        ensure_dir(run_root / "attempts")
        ensure_results_tsv(run_root / "results.tsv")
        run_id = args.run_id
    else:
        run_id, run_root = create_run(paths.root)

    attempt_id, attempt_root = create_attempt(run_root, paths.draft, paths.claims, run_id)
    ensure_dir(run_root)
    baseline = summarize_attempt(run_id, "baseline", run_root / "attempts" / attempt_id, paths.draft, paths.claims, paths.sources)
    check_summary = run_checks(paths.draft, paths.claims, paths.sources)
    claim_issue_count, claim_issue_ids = collect_claim_issue_count(paths.claims, paths.draft)
    task = choose_next_task(check_summary.model_dump(mode="json"), baseline, claim_issue_ids)
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
    print(f"claim_issue_count\t{claim_issue_count}")
    return 0


def command_check(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    draft_path = Path(args.draft) if args.draft else paths.draft
    claims_path = Path(args.claims) if args.claims else paths.claims
    sources_path = Path(args.sources) if args.sources else paths.sources
    summary = run_checks(draft_path, claims_path, sources_path)
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
    written = write_verifier_bundle(attempt_root, attempt_root / "draft.qmd", attempt_root / "claims.yaml")
    for key, value in written.items():
        print(f"{key}\t{value}")
    return 0


def command_evaluate(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    run_root = paths.runs / args.run_id
    attempt_root = run_root / "attempts" / args.attempt
    state = load_state(run_root, args.run_id)
    summary = summarize_attempt(args.run_id, args.attempt, attempt_root, attempt_root / "draft.qmd", attempt_root / "claims.yaml", paths.sources)
    write_json(attempt_root / "check-results.json", run_checks(attempt_root / "draft.qmd", attempt_root / "claims.yaml", paths.sources).model_dump(mode="json"))
    write_json(attempt_root / "evaluation-summary.json", summary.model_dump(mode="json"))
    write_diff(paths.draft, attempt_root / "draft.qmd", attempt_root / "draft.diff")

    current = state.accepted_summary
    decision = "keep" if summary and is_strict_improvement(summary, current) else "revert"
    rationale = "candidate improved acceptance tuple"
    if decision == "keep":
        shutil.copy2(attempt_root / "draft.qmd", paths.draft)
        shutil.copy2(attempt_root / "claims.yaml", paths.claims)
        state.accepted_summary = summary
        save_state(run_root, state)
    else:
        rationale = "candidate did not strictly improve acceptance tuple"

    task_payload = read_json(attempt_root / "next-task.json") if (attempt_root / "next-task.json").exists() else {"task": "unknown"}
    append_results(run_root / "results.tsv", args.attempt, task_payload["task"], decision, summary, rationale)
    print(f"decision\t{decision}")
    print(f"summary\t{attempt_root / 'evaluation-summary.json'}")
    return 0


def command_refresh_sources(args: argparse.Namespace) -> int:
    paths = post_paths(args.slug)
    source_doc = read_sources(paths.sources)
    claim_doc = read_claims(paths.claims)

    source_doc.sources = [source for source in source_doc.sources if source.id != args.source_id]
    source_doc.sources.append(
        SourceRecord(
            id=args.source_id,
            title=args.title,
            kind=args.kind,
            locator=args.locator,
            snippets=[SourceSnippet(id=f"{args.source_id}-001", text=args.snippet)],
        )
    )
    source_doc.sources.sort(key=lambda item: item.id)

    for claim in claim_doc.claims:
        if args.claim_id and claim.id not in args.claim_id:
            continue
        if args.source_id not in claim.source_ids:
            claim.source_ids.append(args.source_id)
        claim.last_verification.status = "needs_rerun"
        claim.last_verification.reason = f"source {args.source_id} added"

    write_sources(paths.sources, source_doc)
    write_claims(paths.claims, claim_doc)
    print(paths.sources)
    return 0


def main() -> int:
    args = parse_args()
    command_map = {
        "prepare": command_prepare,
        "approve-brief": command_approve_brief,
        "stage-attempt": command_stage_attempt,
        "check": command_check,
        "verify": command_verify,
        "evaluate": command_evaluate,
        "refresh-sources": command_refresh_sources,
    }
    return command_map[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
