from __future__ import annotations

import hashlib
import http.server
import os
import shutil
import subprocess
import threading
from pathlib import Path

from .artifacts import extract_frontmatter, post_paths, read_json, read_text, write_json
from .models import VerifierRequest, VerifierVerdict
from .prepare import load_input_manifest
from .presets import repo_relative_path
from .utils import ensure_dir, repo_root, slugify
from .visual_checks import load_visual_checks_config, run_visual_checks
from .visuals import extract_markdown_section

PLAYWRIGHT_SCREENSHOT_VERIFIERS = {"brand_consistency", "composition_clarity", "layout_integrity"}


def normalize_visual_attempt_id(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        return "001"
    if candidate == "final":
        return candidate
    if candidate.isdigit():
        return f"{int(candidate):03d}"
    return candidate


def load_visual_request_payload(slug: str) -> dict[str, object]:
    paths = post_paths(slug)
    if not paths.visuals_requests.exists():
        raise FileNotFoundError(
            f"Visual requests do not exist: {paths.visuals_requests}. Run `autobloggy prepare-visuals --slug {slug}` first."
        )
    return read_json(paths.visuals_requests)


def select_visual_requests(slug: str, selected_visual_ids: list[str] | None = None) -> tuple[dict[str, object], list[dict[str, object]]]:
    payload = load_visual_request_payload(slug)
    requests = [dict(item) for item in (payload.get("requests") or [])]
    request_map = {str(request["visual_id"]): request for request in requests}
    if selected_visual_ids:
        unknown = sorted(set(selected_visual_ids) - set(request_map))
        if unknown:
            raise ValueError("Unknown visual ids: " + ", ".join(unknown))
        ordered = [request_map[visual_id] for visual_id in selected_visual_ids]
    else:
        ordered = requests
    return payload, ordered


def visual_attempt_root(slug: str, request: dict[str, object], attempt: str) -> Path:
    paths = post_paths(slug)
    visual_root = paths.root / str(request["visual_root"])
    return visual_root / "attempts" / attempt


def visual_html_path(slug: str, request: dict[str, object], attempt: str) -> Path:
    paths = post_paths(slug)
    if attempt == "001":
        return paths.root / str(request["html_path"])
    return visual_attempt_root(slug, request, attempt) / "visual.html"


def visual_brief_path(slug: str, request: dict[str, object]) -> Path:
    paths = post_paths(slug)
    return paths.root / str(request["brief_path"])


def section_excerpt(draft_text: str, section_heading: str) -> str:
    _, body = extract_frontmatter(draft_text)
    draft_body = body or draft_text
    if section_heading:
        excerpt = extract_markdown_section(draft_body, section_heading, level=2)
        if excerpt:
            return excerpt
    return draft_body[:1600].strip()


def visual_source_summary(slug: str) -> str:
    manifest = load_input_manifest(post_paths(slug).input_manifest)
    sources = [*manifest.raw_visual_sources, *manifest.extracted_visual_sources]
    if not sources:
        return "No visual source assets listed in the input manifest."
    lines = []
    for source in sources:
        locator = f", {source.source_locator}" if source.source_locator else ""
        lines.append(f"- {source.id}: {source.path} (from {source.source_file}{locator})")
    return "\n".join(lines[:12])


def screenshot_path_for_width(html_path: Path, width: int) -> Path:
    return html_path.parent / f"screenshot-{width}.png"


def screenshot_paths_for_attempt(html_path: Path) -> list[tuple[int, Path]]:
    widths = load_visual_checks_config()["verifier_viewport_widths"]
    return [(width, screenshot_path_for_width(html_path, width)) for width in widths]


def default_playwright_wrapper_paths() -> list[Path]:
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    root = repo_root()
    return [
        codex_home / "skills" / "playwright" / "scripts" / "playwright_cli.sh",
        codex_home / "skills" / "playwright-cli" / "scripts" / "playwright_cli.sh",
        root / ".agents" / "skills" / "playwright" / "scripts" / "playwright_cli.sh",
        root / ".agents" / "skills" / "playwright-cli" / "scripts" / "playwright_cli.sh",
        root / ".claude" / "skills" / "playwright" / "scripts" / "playwright_cli.sh",
        root / ".claude" / "skills" / "playwright-cli" / "scripts" / "playwright_cli.sh",
    ]


def playwright_wrapper_path() -> Path:
    configured = os.environ.get("AUTOBLOGGY_PLAYWRIGHT_WRAPPER", "").strip()
    if configured:
        return Path(configured)
    for candidate in default_playwright_wrapper_paths():
        if candidate.exists():
            return candidate
    return default_playwright_wrapper_paths()[0]


def requires_playwright_screenshot() -> bool:
    config = load_visual_checks_config()
    enabled = [*config["must_have_verifiers"], *config["improvement_verifiers"]]
    return any(verifier in PLAYWRIGHT_SCREENSHOT_VERIFIERS for verifier in enabled)


def run_playwright_command(args: list[str]) -> None:
    configured_wrapper = os.environ.get("AUTOBLOGGY_PLAYWRIGHT_WRAPPER", "").strip()
    if not configured_wrapper and shutil.which("npx") is None:
        raise FileNotFoundError(
            "`npx` is required to run the Playwright CLI wrapper. Install Node.js/npm, or set "
            "`AUTOBLOGGY_PLAYWRIGHT_WRAPPER` to a working wrapper script."
        )
    wrapper = playwright_wrapper_path()
    if not wrapper.exists():
        searched = "\n".join(f"- {path}" for path in default_playwright_wrapper_paths())
        raise FileNotFoundError(
            "Playwright wrapper not found at "
            f"{wrapper}. Install or expose the `playwright` or `playwright-cli` skill, or set "
            "`AUTOBLOGGY_PLAYWRIGHT_WRAPPER`.\nSearched:\n"
            f"{searched}"
        )
    try:
        subprocess.run(
            [str(wrapper), *args],
            cwd=repo_root(),
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = "\n".join(part for part in [exc.stdout.strip(), exc.stderr.strip()] if part)
        raise RuntimeError(
            "Playwright command failed: "
            + " ".join(args)
            + (f"\n{detail}" if detail else "")
            + "\nRun `playwright-cli install-browser` if the browser binaries are missing."
        ) from exc


def capture_visual_screenshot(slug: str, request: dict[str, object], attempt: str, html_path: Path) -> list[Path]:
    raw = f"visual-{slug}-{request['visual_id']}-{attempt}"
    session = "pw-" + hashlib.sha1(raw.encode()).hexdigest()[:16]
    widths = load_visual_checks_config()["verifier_viewport_widths"]
    command_prefix = ["--session", session]
    captured: list[Path] = []

    # Playwright CLI blocks file:// protocol. Serve the visual directory over HTTP so
    # the browser can load the HTML and any relative assets without protocol restrictions.
    serve_dir = str(html_path.parent)
    handler = http.server.SimpleHTTPRequestHandler
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    server.timeout = 2
    # Change the working directory for the handler so relative paths resolve correctly.
    original_dir = os.getcwd()
    os.chdir(serve_dir)
    port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    html_url = f"http://127.0.0.1:{port}/{html_path.name}"
    try:
        run_playwright_command([*command_prefix, "open", html_url])
        for width in widths:
            screenshot_path = screenshot_path_for_width(html_path, width)
            run_playwright_command([*command_prefix, "resize", str(width), "900"])
            run_playwright_command([*command_prefix, "run-code", "await page.waitForLoadState('load'); await page.waitForTimeout(400)"])
            run_playwright_command([*command_prefix, "screenshot", "--filename", str(screenshot_path), "--full-page"])
            captured.append(screenshot_path)
    finally:
        try:
            run_playwright_command([*command_prefix, "close"])
        except Exception:
            pass
        server.shutdown()
        os.chdir(original_dir)
    return captured


def build_visual_verifier_requests(
    slug: str,
    request: dict[str, object],
    payload: dict[str, object],
    attempt: str,
) -> list[VerifierRequest]:
    paths = post_paths(slug)
    html_path = visual_html_path(slug, request, attempt)
    brief_path = visual_brief_path(slug, request)
    draft_text = read_text(paths.draft)
    excerpt = section_excerpt(draft_text, str(request.get("section_heading") or ""))
    brief_excerpt = ""
    if brief_path.exists():
        brief_excerpt = read_text(brief_path).strip()[:1400]

    context_lines = [
        f"Visual id: {request['visual_id']}",
        f"Attempt: {attempt}",
        f"Hint: {request.get('hint') or '(none)'}",
        f"Section heading: {request.get('section_heading') or '(none)'}",
        "",
        "Adjacent draft section:",
        excerpt or "(section unavailable)",
        "",
        "Available source visuals:",
        visual_source_summary(slug),
    ]
    if brief_excerpt:
        context_lines.extend(["", "Brief excerpt:", brief_excerpt])

    screenshot_entries = screenshot_paths_for_attempt(html_path)
    existing_screenshots = [(width, path) for width, path in screenshot_entries if path.exists()]
    if existing_screenshots:
        screenshot_line = "Screenshots (evaluate ALL widths — a pass requires the composition to work at every width, not just shrink): " + "; ".join(
            f"{width}px → {repo_relative_path(path)}" for width, path in existing_screenshots
        )
    else:
        screenshot_line = "No screenshot files are bundled for this attempt."
    instructions = "\n".join(
        [
            f"Primary HTML file: {repo_relative_path(html_path)}",
            f"Brief file: {repo_relative_path(brief_path) if brief_path.exists() else '(missing)'}",
            f"Draft file: {payload['draft']}",
            f"Brand guide: {payload['brand_guide']}",
            "Use the rubric in the prompt file for this verifier.",
            screenshot_line,
            "Return only pass or fail with a short rationale.",
        ]
    )

    config = load_visual_checks_config()
    requests: list[VerifierRequest] = []
    for verifier in config["must_have_verifiers"]:
        requests.append(
            VerifierRequest(
                verifier=verifier,
                must_have=True,
                prompt_path=f"prompts/visual_verifiers/{verifier}.md",
                scope=f"visual:{request['visual_id']}:{attempt}",
                target_excerpt="\n".join(context_lines),
                instructions=instructions,
            )
        )
    for verifier in config["improvement_verifiers"]:
        requests.append(
            VerifierRequest(
                verifier=verifier,
                must_have=False,
                prompt_path=f"prompts/visual_verifiers/{verifier}.md",
                scope=f"visual:{request['visual_id']}:{attempt}",
                target_excerpt="\n".join(context_lines),
                instructions=instructions,
            )
        )
    return requests


def write_visual_verifier_bundle(slug: str, selected_visual_ids: list[str] | None = None, attempt: str = "001") -> dict[str, str]:
    attempt_id = normalize_visual_attempt_id(attempt)
    payload, requests = select_visual_requests(slug, selected_visual_ids)
    visual_identity = str(payload.get("visual_identity") or "")
    paths = post_paths(slug)

    verified_count = 0
    for request in requests:
        html_path = visual_html_path(slug, request, attempt_id)
        if not html_path.exists():
            raise FileNotFoundError(
                f"Visual HTML does not exist for `{request['visual_id']}` at attempt `{attempt_id}`: {html_path}."
            )
        attempt_root = ensure_dir(html_path.parent)
        if requires_playwright_screenshot():
            capture_visual_screenshot(slug, request, attempt_id, html_path)
        check_summary = run_visual_checks(html_path, visual_identity)
        write_json(attempt_root / "check-results.json", check_summary.model_dump(mode="json"))

        verifier_requests = build_visual_verifier_requests(slug, request, payload, attempt_id)
        write_json(
            attempt_root / "verifier_requests.json",
            {"requests": [item.model_dump(mode="json") for item in verifier_requests]},
        )

        verdict_dir = ensure_dir(attempt_root / "verdicts")
        for verifier_request in verifier_requests:
            verdict_path = verdict_dir / f"{verifier_request.verifier}.json"
            if not verdict_path.exists():
                verdict = VerifierVerdict(
                    verifier=verifier_request.verifier,
                    must_have=verifier_request.must_have,
                    scope=verifier_request.scope,
                )
                write_json(verdict_path, verdict.model_dump(mode="json"))
        verified_count += 1

    return {
        "visuals_root": str(paths.visuals_root),
        "attempt": attempt_id,
        "verified_count": str(verified_count),
    }
