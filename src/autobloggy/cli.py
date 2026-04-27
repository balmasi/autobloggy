from __future__ import annotations

import argparse
from pathlib import Path

from .artifacts import patch_meta, post_paths
from .prepare import (
    outline_approval_issues,
    prepare_post_inputs,
    run_generate_draft,
    run_generate_outline,
    run_generate_strategy,
    run_new_post,
    scaffold_preset,
)
from .utils import now_iso, repo_root
from .verify import run_verify


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="autobloggy")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_post = subparsers.add_parser("new-post")
    new_post.add_argument("--slug")
    new_post.add_argument("--title")
    new_post.add_argument("--topic")
    new_post.add_argument("--source", action="append", default=[])
    new_post.add_argument("--preset")

    new_preset = subparsers.add_parser("new-preset")
    new_preset.add_argument("--name", required=True)

    prepare_inputs = subparsers.add_parser("prepare-inputs")
    prepare_inputs.add_argument("--slug", required=True)

    decide_discovery = subparsers.add_parser("decide-discovery")
    decide_discovery.add_argument("--slug", required=True)
    decide_discovery.add_argument("--decision", required=True, choices=("yes", "no"))

    generate_strategy = subparsers.add_parser("generate-strategy")
    generate_strategy.add_argument("--slug", required=True)

    generate_outline = subparsers.add_parser("generate-outline")
    generate_outline.add_argument("--slug", required=True)

    approve_outline = subparsers.add_parser("approve-outline")
    approve_outline.add_argument("--slug", required=True)

    generate_draft = subparsers.add_parser("generate-draft")
    generate_draft.add_argument("--slug", required=True)

    verify = subparsers.add_parser("verify")
    verify.add_argument("--slug", required=True)

    return parser.parse_args()


def print_kv(payload: dict[str, str]) -> None:
    for key, value in payload.items():
        print(f"{key}\t{value}")


def cmd_new_post(args: argparse.Namespace) -> int:
    repo_root()
    try:
        print_kv(
            run_new_post(
                slug=args.slug,
                title=args.title,
                topic=args.topic,
                source_paths=[Path(value) for value in args.source],
                preset_name=args.preset,
            )
        )
        return 0
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc


def cmd_new_preset(args: argparse.Namespace) -> int:
    repo_root()
    try:
        preset_root = scaffold_preset(args.name)
        print(f"preset\t{preset_root}")
        return 0
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc


def cmd_prepare_inputs(args: argparse.Namespace) -> int:
    repo_root()
    try:
        print_kv(prepare_post_inputs(args.slug, require_sources=True))
        return 0
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc


def cmd_decide_discovery(args: argparse.Namespace) -> int:
    repo_root()
    paths = post_paths(args.slug)
    if not paths.meta.exists():
        raise SystemExit(f"Post meta does not exist: {paths.meta}. Run `autobloggy new-post` first.")
    meta = patch_meta(args.slug, discovery_decision=args.decision, discovery_decided_at=now_iso())
    print(f"slug\t{meta.slug}")
    print(f"discovery_decision\t{meta.discovery_decision}")
    return 0


def cmd_generate_strategy(args: argparse.Namespace) -> int:
    repo_root()
    try:
        print_kv(run_generate_strategy(args.slug))
        return 0
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc


def cmd_generate_outline(args: argparse.Namespace) -> int:
    repo_root()
    try:
        print_kv(run_generate_outline(args.slug))
        return 0
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc


def cmd_approve_outline(args: argparse.Namespace) -> int:
    repo_root()
    paths = post_paths(args.slug)
    if not paths.outline.exists():
        raise SystemExit(f"Outline does not exist: {paths.outline}")
    issues = outline_approval_issues(paths.outline.read_text(encoding="utf-8"))
    if issues:
        raise SystemExit("Outline is incomplete:\n- " + "\n- ".join(issues))
    meta = patch_meta(args.slug, status="outline_approved", approved_at=now_iso())
    print(f"slug\t{meta.slug}")
    print(f"status\t{meta.status}")
    print(f"outline\t{paths.outline}")
    return 0


def cmd_generate_draft(args: argparse.Namespace) -> int:
    repo_root()
    try:
        print_kv(run_generate_draft(args.slug))
        return 0
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc


def cmd_verify(args: argparse.Namespace) -> int:
    repo_root()
    try:
        print_kv(run_verify(args.slug))
        return 0
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc


def main() -> int:
    args = parse_args()
    commands = {
        "new-post": cmd_new_post,
        "new-preset": cmd_new_preset,
        "prepare-inputs": cmd_prepare_inputs,
        "decide-discovery": cmd_decide_discovery,
        "generate-strategy": cmd_generate_strategy,
        "generate-outline": cmd_generate_outline,
        "approve-outline": cmd_approve_outline,
        "generate-draft": cmd_generate_draft,
        "verify": cmd_verify,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
