from __future__ import annotations

from pathlib import Path

from autobloggy.artifacts import read_json
from autobloggy.visual_verifiers import playwright_wrapper_path
from tests.helpers import copy_repo, parse_kv, resolve_generated_outline, resolve_generated_strategy, run_cli


VALID_VISUAL_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Visual</title>
  <style>
    :root {
      --font-body: "Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      --color-bg: #F7F7F5;
      --color-surface: #FFFFFF;
      --color-text: #1F2933;
      --color-muted: #52606D;
      --color-accent: #0F766E;
      --color-accent-soft: #D9F3EF;
      --color-border: #D9E2EC;
    }
    body {
      margin: 0;
      font-family: var(--font-body);
      background: #F7F7F5;
      color: #1F2933;
    }
    .card {
      margin: 24px;
      padding: 24px;
      border: 1px solid #D9E2EC;
      background: #FFFFFF;
    }
    .accent {
      color: #0F766E;
    }
  </style>
</head>
<body>
  <section class="card" aria-label="A visual showing the pipeline stages from raw inputs to final embed">
    <h1 class="accent">Pipeline</h1>
    <p>Prepare inputs, generate visuals, verify outputs, then embed approved visuals.</p>
    <p>Source: Internal workflow summary.</p>
  </section>
</body>
</html>
"""


INVALID_VISUAL_HTML = """<!doctype html>
<html>
<head>
  <style>
    body {
      font-family: "Papyrus", cursive;
      color: #FF00FF;
    }
  </style>
  <script src="https://evil.example/app.js"></script>
</head>
<body>
  <div>Unlabeled visual</div>
</body>
</html>
"""


def build_post_with_draft(repo: Path, slug: str) -> None:
    run_cli(repo, "new-post", "--slug", slug, "--topic", "Visual verifier workflow")
    strategy_path = repo / "posts" / slug / "strategy.md"
    resolve_generated_strategy(strategy_path)
    run_cli(repo, "approve-strategy", "--slug", slug)
    run_cli(repo, "decide-discovery", "--slug", slug, "--decision", "no")
    run_cli(repo, "generate-outline", "--slug", slug)
    resolve_generated_outline(repo / "posts" / slug / "outline.md")
    run_cli(repo, "approve-outline", "--slug", slug)
    run_cli(repo, "generate-draft", "--slug", slug)


def install_fake_playwright_wrapper(tmp_path: Path, monkeypatch) -> Path:
    wrapper = tmp_path / "fake-playwright-wrapper.py"
    wrapper.write_text(
        """#!/usr/bin/env python3
import base64
import sys
from pathlib import Path

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO6Z0V0AAAAASUVORK5CYII=")

args = sys.argv[1:]
if args[:2] == ["--session", args[1] if len(args) > 1 else ""]:
    args = args[2:]
elif args and args[0].startswith("--session="):
    args = args[1:]

if not args:
    sys.exit(0)

command = args[0]
if command == "screenshot":
    filename = None
    for index, arg in enumerate(args):
        if arg == "--filename" and index + 1 < len(args):
            filename = args[index + 1]
            break
    if not filename:
        raise SystemExit("missing --filename")
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(PNG)
sys.exit(0)
""",
        encoding="utf-8",
    )
    wrapper.chmod(0o755)
    monkeypatch.setenv("AUTOBLOGGY_PLAYWRIGHT_WRAPPER", str(wrapper))
    return wrapper


def stage_visual_request(repo: Path, slug: str, html: str) -> tuple[dict[str, object], Path]:
    draft_path = repo / "posts" / slug / "draft.qmd"
    draft_path.write_text(
        draft_path.read_text(encoding="utf-8")
        + "\n## Visual Section\n\n<!-- visual: show the pipeline stages -->\n",
        encoding="utf-8",
    )
    run_cli(repo, "prepare-visuals", "--slug", slug)
    payload = read_json(repo / "posts" / slug / "visuals" / "requests.json")
    request = payload["requests"][0]
    html_path = repo / "posts" / slug / request["html_path"]
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    return request, html_path


def test_playwright_wrapper_path_prefers_explicit_override(tmp_path: Path, monkeypatch) -> None:
    override = tmp_path / "custom-wrapper.sh"
    override.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    override.chmod(0o755)

    monkeypatch.setenv("AUTOBLOGGY_PLAYWRIGHT_WRAPPER", str(override))

    assert playwright_wrapper_path() == override


def test_playwright_wrapper_path_supports_playwright_cli_skill_name(tmp_path: Path, monkeypatch) -> None:
    codex_home = tmp_path / "codex-home"
    wrapper = codex_home / "skills" / "playwright-cli" / "scripts" / "playwright_cli.sh"
    wrapper.parent.mkdir(parents=True, exist_ok=True)
    wrapper.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    wrapper.chmod(0o755)

    monkeypatch.delenv("AUTOBLOGGY_PLAYWRIGHT_WRAPPER", raising=False)
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    assert playwright_wrapper_path() == wrapper


def test_verify_visuals_writes_check_results_and_verifier_bundle(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)
    install_fake_playwright_wrapper(tmp_path, monkeypatch)

    slug = "visual-verify"
    build_post_with_draft(repo, slug)
    request, html_path = stage_visual_request(repo, slug, VALID_VISUAL_HTML)

    generated = parse_kv(run_cli(repo, "verify-visuals", "--slug", slug, "--visual-id", request["visual_id"]).stdout)
    assert generated["verified_count"] == "1"
    assert generated["attempt"] == "001"

    attempt_root = html_path.parent
    check_results = read_json(attempt_root / "check-results.json")
    assert check_results["blocker_count"] == 0
    assert (attempt_root / "screenshot-360.png").exists()
    assert (attempt_root / "screenshot-820.png").exists()

    verifier_requests = read_json(attempt_root / "verifier_requests.json")
    verifier_names = [item["verifier"] for item in verifier_requests["requests"]]
    assert verifier_names == [
        "visual_relevance",
        "text_visual_alignment",
        "source_attribution",
        "layout_integrity",
        "brand_consistency",
        "composition_clarity",
    ]
    for item in verifier_requests["requests"]:
        assert (repo / item["prompt_path"]).exists()
        if item["verifier"] in {"brand_consistency", "composition_clarity", "layout_integrity"}:
            assert "screenshot-360.png" in item["instructions"]
            assert "screenshot-820.png" in item["instructions"]
        verdict_path = attempt_root / "verdicts" / f"{item['verifier']}.json"
        assert verdict_path.exists()


def test_verify_visuals_flags_deterministic_visual_check_failures(repo_root: Path, tmp_path: Path, monkeypatch) -> None:
    repo = copy_repo(repo_root, tmp_path)
    monkeypatch.chdir(repo)
    install_fake_playwright_wrapper(tmp_path, monkeypatch)

    slug = "visual-verify-fail"
    build_post_with_draft(repo, slug)
    request, html_path = stage_visual_request(repo, slug, INVALID_VISUAL_HTML)

    run_cli(repo, "verify-visuals", "--slug", slug, "--visual-id", request["visual_id"])
    check_results = read_json(html_path.parent / "check-results.json")
    failed = {item["id"] for item in check_results["results"] if not item["passed"]}

    assert "accessible_label" in failed
    assert "script_origin_allowlist" in failed
    assert "brand_colours_only" in failed
    assert "brand_fonts_only" in failed
