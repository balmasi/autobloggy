from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture()
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def fresh_repo(repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(
        repo_root,
        target,
        ignore=shutil.ignore_patterns(
            ".git", ".venv", "__pycache__", ".pytest_cache",
            "posts", "memory", ".playwright-cli", "node_modules",
        ),
    )
    (target / "posts").mkdir(exist_ok=True)
    monkeypatch.chdir(target)
    return target


def run_cli(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo / "src")
    return subprocess.run(
        [sys.executable, "-m", "autobloggy.cli", *args],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=check,
    )


def parse_kv(stdout: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for line in stdout.strip().splitlines():
        if "\t" in line:
            key, value = line.split("\t", 1)
            pairs[key] = value
    return pairs
