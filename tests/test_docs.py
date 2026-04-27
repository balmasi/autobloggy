from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_program_md_describes_new_pipeline(repo_root: Path) -> None:
    program = (repo_root / "program.md").read_text(encoding="utf-8")
    assert "Use skill `autobloggy-new-post`." in program
    assert "`autobloggy prepare-inputs --slug <slug>`" in program
    assert "`autobloggy generate-strategy --slug <slug>`" in program
    assert "`autobloggy decide-discovery --slug <slug> --decision yes|no`" in program
    assert "Use skill `autobloggy-discovery`" in program
    assert "Use skill `autobloggy-first-draft`" in program
    assert "Use skill `autobloggy-draft-loop`" in program
    assert "`autobloggy verify --slug <slug>`" in program
    assert "Use skill `slop-mop` as the final workflow step" in program
    assert "Outline headings must already be publishable, reader-facing section titles" in program


def test_skill_inventory(repo_root: Path) -> None:
    skills = repo_root / "skills"
    for name in (
        "autobloggy-new-post",
        "autobloggy-first-draft",
        "autobloggy-draft-loop",
        "autobloggy-verifier",
        "autobloggy-discovery",
        "slop-mop",
        "autobloggy-transcribe",
    ):
        assert (skills / name / "SKILL.md").exists(), f"missing {name}"
    assert (skills / "slop-mop" / "scripts" / "detect_slop.py").exists()
    assert (skills / "slop-mop" / "references" / "prose-patterns.md").exists()
    assert not (skills / "autobloggy-visual-verifier").exists()
    assert not (skills / "autobloggy-visuals").exists()


def test_presets_have_template_html(repo_root: Path) -> None:
    for name in ("default", "georgian"):
        path = repo_root / "presets" / name / "template.html"
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "<main data-content>" in text


def test_verifier_rubrics_exists(repo_root: Path) -> None:
    rubrics = repo_root / "prompts" / "verifier_rubrics.md"
    assert rubrics.exists()
    text = rubrics.read_text(encoding="utf-8")
    for rule in ("voice", "overstatement", "needs_visual", "layout_integrity", "presentable_headings"):
        assert rule in text


def test_slop_mop_detector_runs(repo_root: Path) -> None:
    script = repo_root / "skills" / "slop-mop" / "tests" / "run_tests.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "ok test_sloppy_markdown" in result.stdout
