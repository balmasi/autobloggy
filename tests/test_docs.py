from __future__ import annotations

from pathlib import Path


def test_program_md_explicitly_names_complex_skills(repo_root: Path) -> None:
    program = (repo_root / "program.md").read_text(encoding="utf-8")

    assert "Use skill `autobloggy-new-post`." in program
    assert "`autobloggy prepare-inputs --slug <slug>`" in program
    assert "Ask whether to run discovery before generating the outline." in program
    assert "Use skill `autobloggy-discovery` only when the human explicitly chose yes." in program
    assert "`autobloggy decide-discovery --slug <slug> --decision yes|no`" in program
    assert "Use skill `autobloggy-draft-loop`." in program
    assert "Use skill `autobloggy-visuals` only after `prepare-visuals` has written the request bundle." in program
    assert "`autobloggy prepare-visuals --slug <slug>`" in program
    assert "Use skill `autobloggy-visual-verifier` only after `verify-visuals` has written the verifier bundle." in program
    assert "`autobloggy verify-visuals --slug <slug>`" in program
    assert "`autobloggy embed-visuals --slug <slug>`" in program
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
    assert (repo_root / "skills" / "autobloggy-visuals" / "SKILL.md").exists()
    assert (repo_root / "skills" / "autobloggy-visual-verifier" / "SKILL.md").exists()
    assert not (repo_root / "skills" / "autobloggy-prepare").exists()
    assert not (repo_root / "skills" / "autobloggy-outline").exists()


def test_new_post_skill_avoids_kickoff_jargon(repo_root: Path) -> None:
    skill = (repo_root / "skills" / "autobloggy-new-post" / "SKILL.md").read_text(encoding="utf-8")

    assert "Do not lead with slug, preset, or file-path jargon." in skill
    assert "ask briefly whether to use the default preset or create a new preset" in skill.lower()
    assert "brief.md" in skill
    assert "inputs/user_provided/raw/" in skill


def test_visual_brand_guides_expose_a_shared_visual_identity_schema(repo_root: Path) -> None:
    expected_headings = [
        "## Visual Identity",
        "### Colour Tokens",
        "### Typography Tokens",
        "### Chart Palette",
        "### Component Patterns",
        "### Iconography And External Libraries",
        "### Aspect Ratios",
    ]

    for relative_path in (
        "presets/default/brand_guide.md",
        "presets/georgian/brand_guide.md",
    ):
        text = (repo_root / relative_path).read_text(encoding="utf-8")
        for heading in expected_headings:
            assert heading in text


def test_visuals_skill_requires_exact_brand_tokens(repo_root: Path) -> None:
    skill = (repo_root / "skills" / "autobloggy-visuals" / "SKILL.md").read_text(encoding="utf-8")

    assert "visual_identity" in skill
    assert "visual_requirements" in skill
    assert "visual_verifiers.must_have" in skill
    assert "Copy hex codes, font stacks, component names, icon guidance, and aspect ratios exactly" in skill
    assert "Define CSS custom properties from the listed tokens" in skill


def test_visual_verifier_skill_uses_screenshot_for_pixel_checks(repo_root: Path) -> None:
    skill = (repo_root / "skills" / "autobloggy-visual-verifier" / "SKILL.md").read_text(encoding="utf-8")

    assert "screenshot-360.png" in skill
    assert "screenshot-820.png" in skill
    assert "Spawn one verifier sub-agent per request" in skill
    assert "Playwright CLI wrapper" in skill
