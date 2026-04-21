from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


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

