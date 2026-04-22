from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from autobloggy.artifacts import extract_frontmatter, format_markdown_with_frontmatter


def copy_repo(src: Path, dest: Path) -> Path:
    target = dest / "repo"
    shutil.copytree(
        src,
        target,
        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", "posts/*/runs"),
    )
    return target


def run_cli(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo / "src")
    return subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", *args],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )


def run_cli_failure(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo / "src")
    return subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", *args],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def parse_kv(stdout: str) -> dict[str, str]:
    pairs = {}
    for line in stdout.strip().splitlines():
        if "\t" in line:
            key, value = line.split("\t", 1)
            pairs[key] = value
    return pairs


def resolve_generated_strategy(strategy_path: Path) -> None:
    text = strategy_path.read_text(encoding="utf-8")
    replacements = {
        "[REQUIRED: name the primary reader and the job they are trying to do.]": "Platform and product engineering leads who need operational guidance they can apply this quarter.",
        "[REQUIRED: confirm or replace this with the user's preferred voice.]": "",
        "[REQUIRED: edit these guardrails until they match the user's expectations for the piece.]": "",
        "[REQUIRED: add or remove points until this captures the non-negotiable substance of the post.]": "",
        "[REQUIRED: record any tones, claims, examples, or framing that should be avoided.]": "",
        "- [REQUIRED: What specific reader or buyer context should shape the framing?]": "- The framing should help technical leaders decide whether this workflow is worth adopting for their team.",
        "- [REQUIRED: Which examples, edge cases, or practical details are mandatory for this audience?]": "- The post must include one concrete example, one tradeoff, and one boundary where the approach should not be used.",
        "- [REQUIRED: What should the post sound like, and what should it never sound like?]": "- It should sound like a practiced operator and never like marketing copy or generic AI advice.",
        "- [REQUIRED: What practical takeaway should the reader leave with?]": "- The reader should leave with a clear decision rule and a concrete next step.",
        "- [ ] Audience is specific enough to guide structure and examples.": "- [x] Audience is specific enough to guide structure and examples.",
        "- [ ] Target voice reflects the user's actual preference, not the default.": "- [x] Target voice reflects the user's actual preference, not the default.",
        "- [ ] Style guardrails are concrete enough to guide generation.": "- [x] Style guardrails are concrete enough to guide generation.",
        "- [ ] Must-cover points capture the non-negotiable substance of the post.": "- [x] Must-cover points capture the non-negotiable substance of the post.",
        "- [ ] Must-avoid rules are explicit.": "- [x] Must-avoid rules are explicit.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    strategy_path.write_text(text, encoding="utf-8")


def resolve_generated_outline(outline_path: Path) -> None:
    text = outline_path.read_text(encoding="utf-8")
    frontmatter, _ = extract_frontmatter(text)
    body = "\n".join(
        [
            "# Outline",
            "",
            "## Why this topic is confusing in practice",
            "- Lead with the concrete reader confusion.",
            "",
            "## The distinction that matters most",
            "- Explain the key distinction clearly.",
            "",
            "## What the reader should do with it",
            "- End with the practical takeaway.",
            "",
        ]
    )
    outline_path.write_text(format_markdown_with_frontmatter(frontmatter, body), encoding="utf-8")
