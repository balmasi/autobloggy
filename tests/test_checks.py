from __future__ import annotations

from pathlib import Path

from autobloggy.artifacts import write_text
from autobloggy.checks import run_checks


def test_citations_must_resolve(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(repo_root)
    draft = tmp_path / "draft.qmd"
    draft.write_text(
        "---\ntitle: Example\nformat: gfm\n---\n\n# Example\n\nIntro paragraph with enough words to count as an intro [@missing].\n\n## Conclusion\n\nWrap up.\n",
        encoding="utf-8",
    )

    summary = run_checks(draft, repo_root / "posts/example-post/claims.yaml", repo_root / "posts/example-post/sources.yaml")
    citations = next(result for result in summary.results if result.id == "citations_resolve")
    assert not citations.passed


def test_em_dash_is_blocked(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(repo_root)
    draft = tmp_path / "draft.qmd"
    write_text(
        draft,
        "---\ntitle: Example\nformat: gfm\n---\n\n# Example\n\nThis opening paragraph has enough words — but it uses an em dash.\n\n## Conclusion\n\nWrap up.\n",
    )
    summary = run_checks(draft, repo_root / "posts/example-post/claims.yaml", repo_root / "posts/example-post/sources.yaml")
    em_dash = next(result for result in summary.results if result.id == "em_dash_scan")
    assert not em_dash.passed

