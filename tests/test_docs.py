from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_program_md_describes_prep_pipeline(repo_root: Path) -> None:
    program = (repo_root / "program.md").read_text(encoding="utf-8")
    assert "`autobloggy prep`" in program
    assert "`autobloggy approve-brief --slug <slug>`" in program
    assert "`autobloggy generate-draft --slug <slug>`" in program
    assert "Use skill `autobloggy-new-post`" in program
    assert "Use skill `autobloggy-first-draft`" in program
    assert "Use skill `autobloggy-draft-loop`" in program
    assert "`autobloggy verify --slug <slug>`" in program
    assert "Use skill `slop-mop` as the final workflow step" in program
    for removed in ("generate-strategy", "decide-discovery", "generate-outline", "approve-outline"):
        assert removed not in program


def test_skill_inventory(repo_root: Path) -> None:
    skills = repo_root / "skills"
    for name in (
        "autobloggy-new-post",
        "autobloggy-first-draft",
        "autobloggy-draft-loop",
        "autobloggy-verifier",
        "autobloggy-discovery",
        "slop-mop",
        "transcribe",
    ):
        assert (skills / name / "SKILL.md").exists(), f"missing {name}"
    assert (skills / "slop-mop" / "scripts" / "detect_slop.py").exists()
    assert (skills / "slop-mop" / "references" / "prose-patterns.md").exists()


def test_presets_have_manifest_and_template_html(repo_root: Path) -> None:
    for name in ("default", "georgian"):
        preset = repo_root / "presets" / name
        assert (preset / "preset.yaml").exists()
        text = (preset / "template.html").read_text(encoding="utf-8")
        assert "<main data-content>" in text


def test_quality_criteria_exists(repo_root: Path) -> None:
    criteria = repo_root / "prompts" / "quality_criteria.md"
    assert criteria.exists()
    text = criteria.read_text(encoding="utf-8")
    for rule in ("voice", "overstatement", "needs_visual", "layout_integrity", "presentable_headings"):
        assert rule in text
    assert not (repo_root / "prompts" / "verifier_rubrics.md").exists()


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
