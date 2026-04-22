from __future__ import annotations

from pathlib import Path


def test_program_md_explicitly_names_complex_skills(repo_root: Path) -> None:
    program = (repo_root / "program.md").read_text(encoding="utf-8")

    assert "Use skill `autobloggy-new-post`." in program
    assert "Ask whether to run discovery before generating the outline." in program
    assert "Use skill `autobloggy-discovery` only when the human explicitly chose yes." in program
    assert "`autobloggy decide-discovery --slug <slug> --decision yes|no`" in program
    assert "Use skill `autobloggy-draft-loop`." in program
    assert "`autobloggy stage-attempt --slug <slug> --run-id <run-id>`" in program
    assert "`--new-run` only when intentionally starting a fresh run" in program
    assert "Outline headings must already be publishable, reader-facing section titles" in program
    assert "Use skill `autobloggy-copy-edit` only when the active task is prose tightening." in program
    assert "Do not infer alternate workflow instructions from `CLAUDE.md`, `AGENTS.md`, or any skill." in program
    assert "write a complete outline directly into `posts/<slug>/outline.md`" in program


def test_bootstrap_docs_are_thin_indexes(repo_root: Path) -> None:
    agents = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    claude = (repo_root / "CLAUDE.md").read_text(encoding="utf-8")

    for text in (agents, claude):
        assert "read `program.md` first" in text.lower()
        assert "Workflow" not in text
        assert "Use the skill named by `program.md`" in text


def test_skill_inventory_matches_single_owner_design(repo_root: Path) -> None:
    assert (repo_root / "skills" / "autobloggy-new-post" / "SKILL.md").exists()
    assert (repo_root / "skills" / "autobloggy-draft-loop" / "SKILL.md").exists()
    assert not (repo_root / "skills" / "autobloggy-prepare").exists()
    assert not (repo_root / "skills" / "autobloggy-outline").exists()


def test_new_post_skill_avoids_kickoff_jargon(repo_root: Path) -> None:
    skill = (repo_root / "skills" / "autobloggy-new-post" / "SKILL.md").read_text(encoding="utf-8")

    assert "Do not lead with slug, preset, or file-path jargon." in skill
    assert "ask briefly whether to use the default preset or create a new preset" in skill.lower()
