from __future__ import annotations

from pathlib import Path

from autobloggy.artifacts import read_claims, read_sources
from tests.helpers import copy_repo, resolve_generated_brief, run_cli


def test_refresh_sources_appends_source_and_invalidates_claim(repo_root: Path, tmp_path: Path) -> None:
    repo = copy_repo(repo_root, tmp_path)
    slug = "example-post"
    seed = repo / "tests" / "fixtures" / "example_seed.md"
    run_cli(repo, "prepare", "--slug", slug, "--seed", str(seed), "--through", "brief")
    resolve_generated_brief(repo / "posts" / slug / "brief.md")
    run_cli(repo, "approve-brief", "--slug", slug)
    run_cli(repo, "prepare", "--slug", slug, "--seed", str(seed), "--through", "draft")

    run_cli(
        repo,
        "refresh-sources",
        "--slug",
        slug,
        "--source-id",
        "src-new",
        "--title",
        "Primary Note",
        "--locator",
        "https://example.com/primary",
        "--snippet",
        "Primary note snippet.",
        "--claim-id",
        "clm-001",
    )

    sources = read_sources(repo / "posts" / slug / "sources.yaml")
    claims = read_claims(repo / "posts" / slug / "claims.yaml")

    assert any(source.id == "src-new" for source in sources.sources)
    claim = next(item for item in claims.claims if item.id == "clm-001")
    assert "src-new" in claim.source_ids
    assert claim.last_verification.status == "needs_rerun"
