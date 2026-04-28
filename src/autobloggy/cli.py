import argparse
from pathlib import Path

from .prepare import (
    run_approve_brief,
    run_generate_draft,
    run_normalize_source,
    run_prep,
    run_skip_discovery,
    scaffold_preset,
)
from .utils import repo_root
from .verify import run_verify


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="autobloggy",
        description="Turn a topic and source material into a publishable blog post.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prep = subparsers.add_parser(
        "prep",
        help="Prepare a new post: scaffold the folder, copy sources, and write blog_brief.md.",
    )
    prep.add_argument(
        "--slug",
        metavar="SLUG",
        help="URL-safe post identifier (e.g. why-evals-fail). Auto-derived from --topic if omitted.",
    )
    prep.add_argument(
        "--topic",
        metavar="TEXT",
        help="Plain-language topic or title for the post.",
    )
    prep.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="PATH",
        help="Path to a source file or directory to include. Repeatable.",
    )
    prep.add_argument(
        "--preset",
        metavar="NAME",
        help="Preset to use (must exist under presets/). Defaults to the value in config.yaml.",
    )
    prep.add_argument(
        "--intake-depth",
        metavar="NAME",
        help="Intake depth controlling how blog_brief.md is scaffolded "
             "(e.g. fast, guided, expert). Defined in config.yaml under intake.depths.",
    )
    prep.add_argument(
        "--select",
        action="append",
        default=[],
        metavar="DIMENSION=KEY",
        help="Override a preset resource selection (e.g. --select audience=developers). Repeatable.",
    )

    new_preset = subparsers.add_parser(
        "new-preset",
        help="Scaffold a new preset directory under presets/<name>/.",
    )
    new_preset.add_argument("--name", required=True, metavar="NAME", help="Name of the new preset.")

    normalize_source = subparsers.add_parser(
        "normalize-source",
        help="Replace a placeholder source with docling-extracted markdown and update the manifest.",
    )
    normalize_source.add_argument("--slug", required=True, metavar="SLUG", help="Post slug.")
    normalize_source.add_argument(
        "--source-id",
        required=True,
        metavar="ID",
        help="Source id in manifest.yaml (e.g. source-001).",
    )
    normalize_source.add_argument(
        "--caption",
        action="store_true",
        help="Run a local VLM over each image and store its description as alt text. Off by default.",
    )
    normalize_source.add_argument(
        "--caption-model",
        choices=("smolvlm", "granite"),
        default="smolvlm",
        help="Local VLM preset for captioning. Default: smolvlm.",
    )

    skip_discovery = subparsers.add_parser(
        "skip-discovery",
        help="Record that discovery was declined for this post, satisfying an ask/required discovery gate.",
    )
    skip_discovery.add_argument("--slug", required=True, metavar="SLUG", help="Post slug.")

    approve_brief = subparsers.add_parser(
        "approve-brief",
        help="Lock blog_brief.md and advance meta.yaml status to brief_approved.",
    )
    approve_brief.add_argument("--slug", required=True, metavar="SLUG", help="Post slug.")

    generate_draft = subparsers.add_parser(
        "generate-draft",
        help="Materialise draft.html from the preset template (fills title and H1 only).",
    )
    generate_draft.add_argument("--slug", required=True, metavar="SLUG", help="Post slug.")

    verify = subparsers.add_parser(
        "verify",
        help="Run programmatic checks and Playwright screenshots; write the verify pack to .verify/.",
    )
    verify.add_argument("--slug", required=True, metavar="SLUG", help="Post slug.")

    return parser.parse_args()


def print_kv(payload: dict[str, str]) -> None:
    for key, value in payload.items():
        print(f"{key}\t{value}")


def cmd_prep(args: argparse.Namespace) -> int:
    repo_root()
    try:
        print_kv(
            run_prep(
                slug=args.slug,
                topic=args.topic,
                source_paths=[Path(value) for value in args.source],
                preset_name=args.preset,
                intake_depth_name=args.intake_depth,
                select_values=args.select,
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


def cmd_normalize_source(args: argparse.Namespace) -> int:
    repo_root()
    try:
        print_kv(
            run_normalize_source(
                slug=args.slug,
                source_id=args.source_id,
                caption=args.caption,
                caption_model=args.caption_model,
            )
        )
        return 0
    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        raise SystemExit(str(exc)) from exc


def cmd_skip_discovery(args: argparse.Namespace) -> int:
    repo_root()
    try:
        print_kv(run_skip_discovery(args.slug))
        return 0
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc


def cmd_approve_brief(args: argparse.Namespace) -> int:
    repo_root()
    try:
        print_kv(run_approve_brief(args.slug))
        return 0
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc


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
        "prep": cmd_prep,
        "new-preset": cmd_new_preset,
        "normalize-source": cmd_normalize_source,
        "skip-discovery": cmd_skip_discovery,
        "approve-brief": cmd_approve_brief,
        "generate-draft": cmd_generate_draft,
        "verify": cmd_verify,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
