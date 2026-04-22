from __future__ import annotations

from pathlib import Path

from autobloggy.artifacts import write_text
from autobloggy.checks import flesch_kincaid_grade_level, readability_penalty, run_checks


def test_em_dash_is_blocked(tmp_path: Path) -> None:
    draft = tmp_path / "draft.qmd"
    write_text(
        draft,
        "---\ntitle: Example\nformat: gfm\n---\n\n# Example\n\nThis opening paragraph has enough words — but it uses an em dash.\n\n## Conclusion\n\nWrap up.\n",
    )
    summary = run_checks(draft)
    em_dash = next(result for result in summary.results if result.id == "em_dash_scan")
    assert not em_dash.passed


def test_generic_outline_style_headings_are_blocked(tmp_path: Path) -> None:
    draft = tmp_path / "draft.qmd"
    write_text(
        draft,
        "---\ntitle: Example\nformat: gfm\n---\n\n# Example\n\nThis opening paragraph has enough words to satisfy the intro check for the test.\n\n## Context\n\nA real paragraph follows here with enough substance to count as body text.\n\n## Conclusion\n\nWrap up clearly.\n",
    )
    summary = run_checks(draft)
    presentable = next(result for result in summary.results if result.id == "presentable_headings")
    assert not presentable.passed


def test_user_facing_final_section_counts_as_conclusion(tmp_path: Path) -> None:
    draft = tmp_path / "draft.qmd"
    write_text(
        draft,
        "---\ntitle: Example\nformat: gfm\n---\n\n# Example\n\nThis opening paragraph has enough words to satisfy the intro check for the test.\n\n## First section\n\nThis section explains the first key point with enough words to look like a real paragraph.\n\n## Second section\n\nThis section explains the second key point with enough words to look like a real paragraph.\n\n## The stack makes sense once you sort the layer\n\nThis final section is clearly functioning as the close of the article, even though it does not use the literal word conclusion anywhere in the heading.\n",
    )
    summary = run_checks(draft)
    conclusion = next(result for result in summary.results if result.id == "conclusion_exists")
    assert conclusion.passed


def test_flesch_kincaid_grade_level_handles_short_text() -> None:
    score = flesch_kincaid_grade_level("Short sentences keep this readable. " * 5)
    assert score is not None


def test_readability_penalty_uses_grade_level_target(repo_root: Path, monkeypatch) -> None:
    monkeypatch.chdir(repo_root)
    monkeypatch.setattr("autobloggy.checks.flesch_kincaid_grade_level", lambda text: 10.8)
    assert readability_penalty("ignored") == 0

    monkeypatch.setattr("autobloggy.checks.flesch_kincaid_grade_level", lambda text: 12.4)
    assert readability_penalty("ignored") == 2
