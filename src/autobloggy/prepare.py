import html
import re
import shutil
import subprocess
from pathlib import Path

from .artifacts import (
    init_meta,
    patch_meta,
    post_paths,
    read_meta,
    read_text,
    read_yaml,
    write_text,
    write_yaml,
)
from .models import DiscoveryMeta, SourceManifest, SourceManifestEntry
from .presets import (
    default_preset_name,
    default_intake_depth_name,
    load_brief_sections,
    load_intake_depth,
    parse_cli_selections,
    repo_relative_path,
    required_selection_errors,
    resolve_preset,
    presets_root,
)
from .utils import ensure_dir, now_iso, repo_root, slugify


TEXT_INPUT_SUFFIXES = {".md", ".markdown", ".txt"}
DOCLING_KINDS = {"pdf", "docx", "pptx", "html", "png", "jpg", "jpeg", "tiff", "bmp", "webp"}
DOCLING_SCRIPT = Path("skills/docling-convert/scripts/convert.py")
QUALITY_CRITERIA_PATH = "prompts/quality_criteria.md"


def post_relative_path(path: Path, post_root: Path) -> str:
    return str(path.resolve().relative_to(post_root.resolve()))


def scaffold_intake_layout(slug: str) -> None:
    paths = post_paths(slug)
    ensure_dir(paths.inputs_raw_root)
    ensure_dir(paths.prepared_root)
    ensure_dir(paths.prepared_intake_root)


def copy_user_source(source: Path, destination_root: Path) -> Path:
    source = source.resolve()
    destination_root = destination_root.resolve()
    try:
        source.relative_to(destination_root)
        return source
    except ValueError:
        pass
    ensure_dir(destination_root)
    target = destination_root / source.name
    if source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)
    elif source.is_file():
        shutil.copy2(source, target)
    else:
        raise FileNotFoundError(f"Source path does not exist: {source}")
    return target


def source_kind(path: Path) -> str:
    if path.is_dir():
        return "directory"
    suffix = path.suffix.lower().lstrip(".")
    return suffix or "file"


def render_intake_source(topic: str | None, copied_sources: list[Path], post_root: Path) -> str:
    lines = ["# Operator Intake", ""]
    if topic and topic.strip():
        lines.extend(["## Topic", "", topic.strip(), ""])
    if copied_sources:
        lines.extend(["## Raw Inputs Provided", ""])
        for path in copied_sources:
            lines.append(f"- `{post_relative_path(path, post_root)}`")
        lines.append("")
    if not topic and not copied_sources:
        lines.extend(["## Topic", "", "_No topic or source material was supplied during intake._", ""])
    return "\n".join(lines).rstrip() + "\n"


def render_prepared_source(source_id: str, raw_path: Path, prepared_source: Path, post_root: Path) -> str:
    rel_raw = post_relative_path(raw_path, post_root)
    lines = [
        f"# Prepared Source: {source_id}",
        "",
        f"Origin: `{rel_raw}`",
        "",
        "This source is a v1 normalization placeholder. It makes the raw input visible to the drafting process without moving generated content into `inputs/raw/`.",
        "",
    ]
    if raw_path.is_dir():
        files = sorted(p for p in raw_path.rglob("*") if p.is_file())
        lines.extend(["## Files", ""])
        for file_path in files:
            lines.append(f"- `{post_relative_path(file_path, post_root)}`")
        lines.append("")
    elif raw_path.suffix.lower() in TEXT_INPUT_SUFFIXES:
        lines.extend(["## Text", "", read_text(raw_path).strip(), ""])
    else:
        lines.extend(
            [
                "## Normalization status",
                "",
                f"`{raw_path.suffix.lower() or 'file'}` extraction is not implemented in this refactor.",
                "Use the original file as the source of record until a richer extractor exists.",
                "",
            ]
        )
    write_text(prepared_source, "\n".join(lines).rstrip() + "\n")
    return post_relative_path(prepared_source, post_root)


def write_prepared_sources(
    slug: str,
    topic: str | None,
    copied_sources: list[Path],
) -> SourceManifest:
    paths = post_paths(slug)
    intake_text = render_intake_source(topic, copied_sources, paths.root)
    write_text(paths.prepared_intake_source, intake_text)

    entries = [
        SourceManifestEntry(
            id="intake",
            kind="intake",
            description="Operator intake from the kickoff conversation.",
            path=post_relative_path(paths.prepared_intake_source, paths.root),
            origins=["conversation"],
        )
    ]

    for index, raw_path in enumerate(copied_sources, start=1):
        source_id = f"source-{index:03d}"
        prepared_source = paths.prepared_root / source_id / "source.md"
        rel_path = render_prepared_source(source_id, raw_path, prepared_source, paths.root)
        entries.append(
            SourceManifestEntry(
                id=source_id,
                kind=source_kind(raw_path),
                description=f"Placeholder source for {raw_path.name} (run `autobloggy normalize-source` to extract).",
                path=rel_path,
                origins=[post_relative_path(raw_path, paths.root)],
            )
        )

    manifest = SourceManifest(sources=entries)
    write_yaml(paths.prepared_manifest, manifest.model_dump(mode="json"))
    return manifest


def run_normalize_source(
    slug: str,
    source_id: str,
    *,
    caption: bool = False,
    caption_model: str = "smolvlm",
) -> dict[str, str]:
    paths = post_paths(slug)
    if not paths.prepared_manifest.exists():
        raise FileNotFoundError(f"Source manifest does not exist: {paths.prepared_manifest}")

    manifest = SourceManifest.model_validate(read_yaml(paths.prepared_manifest))
    entry = next((e for e in manifest.sources if e.id == source_id), None)
    if entry is None:
        known = ", ".join(e.id for e in manifest.sources) or "(none)"
        raise ValueError(f"Source `{source_id}` not in manifest. Known: {known}")

    if entry.kind not in DOCLING_KINDS:
        raise ValueError(
            f"Source `{source_id}` has kind `{entry.kind}`; docling normalization only supports {sorted(DOCLING_KINDS)}."
        )
    if len(entry.origins) != 1 or entry.origins[0] == "conversation":
        raise ValueError(
            f"Source `{source_id}` does not have a single file origin. "
            f"Run `docling-convert` manually for multi-origin or directory sources."
        )

    raw_path = (paths.root / entry.origins[0]).resolve()
    if not raw_path.is_file():
        raise FileNotFoundError(f"Raw input not found: {raw_path}")

    out_path = (paths.root / entry.path).resolve()
    script_path = (repo_root() / DOCLING_SCRIPT).resolve()
    if not script_path.is_file():
        raise FileNotFoundError(f"docling-convert script not found: {script_path}")

    cmd = [
        "uv", "run", "--with", "docling", "python", str(script_path),
        str(raw_path), "--output", str(out_path),
    ]
    if caption:
        cmd += ["--caption", "--caption-model", caption_model]

    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"docling-convert failed (exit {result.returncode}). "
            f"Placeholder source.md left in place."
        )

    entry.description = f"Docling-normalized source from {raw_path.name}."
    entry.normalized = True
    write_yaml(paths.prepared_manifest, manifest.model_dump(mode="json"))

    images_dir = out_path.parent / f"{out_path.stem}_images"
    return {
        "slug": slug,
        "source_id": source_id,
        "path": str(out_path),
        "images": str(images_dir) if images_dir.exists() else "",
        "captioned": "true" if caption else "false",
    }


def _marker_for(field: str, ask: set[str], prompt: str) -> str:
    if field in ask:
        return f"[ASK_USER]\n{prompt}\n[/ASK_USER]"
    return "[AUTO_FILL]"


def _resource_lines(resolved_preset) -> list[str]:
    label_order = {
        "brand": "Brand",
        "writing": "Writing",
        "format": "Format",
        "audience": "Audience",
        "html_template": "HTML template",
    }
    ordered = [dimension for dimension in label_order if dimension in resolved_preset.resources]
    ordered.extend(sorted(set(resolved_preset.resources) - set(ordered)))
    lines: list[str] = []
    for dimension in ordered:
        resource = resolved_preset.resources[dimension]
        label = label_order.get(dimension, dimension.replace("_", " ").title())
        lines.append(f"- {label}: `{repo_relative_path(resource.path)}`")
    return lines


def render_blog_brief_scaffold(
    slug: str,
    topic: str | None,
    preset_name: str,
    intake_depth_name: str,
    resolved_preset,
    intake_depth,
    brief_sections,
) -> str:
    ask = set(intake_depth.ask)
    omit = set(intake_depth.omit)
    title = topic.strip().splitlines()[0].strip().rstrip(".") if topic and topic.strip() else slug.replace("-", " ").title()
    if len(title) > 90:
        title = title[:87].rstrip() + "..."

    context = [
        "## Generation Context",
        "",
        f"- Preset: `{preset_name}`",
        f"- Intake depth: `{intake_depth_name}`",
        f"- Discovery policy: `{intake_depth.discovery}`",
        *_resource_lines(resolved_preset),
        "- Quality criteria: `prompts/quality_criteria.md`",
        "- Prepared source manifest: `inputs/prepared/manifest.yaml`",
    ]
    if intake_depth.discovery == "ask":
        context.append(
            "- Discovery decision: `[ASK_USER] Ask the operator whether to run discovery. "
            "Replace this with run after running discovery or declined if they decline. [/ASK_USER]`"
        )
    elif intake_depth.discovery in {"required", "never"}:
        context.append(f"- Discovery decision: `{intake_depth.discovery}`")
    context.append("")

    body: list[str] = []
    for key, section in brief_sections.items():
        if key in omit:
            continue
        body.append(f"## {section.label}")
        body.append("")
        if section.preamble:
            body.append(section.preamble)
            body.append("")
        body.append(_marker_for(key, ask, section.prompt))
        body.append("")

    lines = [f"# Blog Brief: {title}", "", *context, *body]
    return "\n".join(lines).rstrip() + "\n"


def run_prep(
    slug: str | None,
    topic: str | None,
    source_paths: list[Path] | None = None,
    preset_name: str | None = None,
    intake_depth_name: str | None = None,
    select_values: list[str] | None = None,
) -> dict[str, str]:
    source_paths = [path.resolve() for path in (source_paths or [])]
    if not topic and not source_paths:
        raise ValueError("prep requires --topic or at least one --source.")

    derived_slug = slug or slugify(topic or next((path.stem for path in source_paths if path.name), "post"))
    paths = post_paths(derived_slug)
    if paths.meta.exists() or paths.blog_brief.exists() or paths.draft.exists():
        raise ValueError(f"Post `{derived_slug}` already exists. Choose a different --slug or remove the existing post.")

    resolved_preset_name = preset_name or default_preset_name(paths.root)
    resolved_intake_depth_name = intake_depth_name or default_intake_depth_name(paths.root)
    intake_depth = load_intake_depth(resolved_intake_depth_name, paths.root)
    cli_selections = parse_cli_selections(select_values)
    selection_errors = required_selection_errors(intake_depth, cli_selections)
    if selection_errors:
        raise ValueError("\n".join(selection_errors))

    resolved_preset = resolve_preset(resolved_preset_name, cli_selections, paths.root)
    brief_sections = load_brief_sections(paths.root)

    scaffold_intake_layout(derived_slug)
    copied_sources = [copy_user_source(source_path, paths.inputs_raw_root) for source_path in source_paths]
    write_prepared_sources(derived_slug, topic, copied_sources)
    write_text(
        paths.blog_brief,
        render_blog_brief_scaffold(
            derived_slug,
            topic,
            resolved_preset_name,
            resolved_intake_depth_name,
            resolved_preset,
            intake_depth,
            brief_sections,
        ),
    )

    init_meta(
        derived_slug,
        resolved_preset_name,
        resolved_intake_depth_name,
        resolved_preset.selections,
        DiscoveryMeta(policy=intake_depth.discovery, ran=False),
        paths.root,
    )

    return {
        "slug": derived_slug,
        "preset": resolved_preset_name,
        "intake_depth": resolved_intake_depth_name,
        "blog_brief": str(paths.blog_brief),
        "manifest": str(paths.prepared_manifest),
        "meta": str(paths.meta),
        "status": "briefing",
    }


def _section_text(markdown: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)"
    match = re.search(pattern, markdown, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _context_values(markdown: str) -> dict[str, str]:
    context = _section_text(markdown, "Generation Context")
    values: dict[str, str] = {}
    for line in context.splitlines():
        match = re.match(r"-\s+([^:]+):\s+`([^`]+)`", line.strip())
        if match:
            values[match.group(1).strip().casefold()] = match.group(2).strip()
    return values


def _discovery_decision(markdown: str) -> str:
    return _context_values(markdown).get("discovery decision", "").strip().casefold()


def _resolve_brief_reference(value: str, post_root: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    if value.startswith("inputs/"):
        return (post_root / path).resolve()
    return (repo_root() / path).resolve()


def brief_approval_issues(slug: str) -> list[str]:
    paths = post_paths(slug)
    issues: list[str] = []
    if not paths.blog_brief.exists():
        return [f"Blog brief does not exist: {paths.blog_brief}"]

    text = read_text(paths.blog_brief)
    for marker in ("[ASK_USER]", "[/ASK_USER]", "[AUTO_FILL]"):
        if marker in text:
            issues.append(f"Blog brief still contains `{marker}`.")

    outline = _section_text(text, "Full Outline")
    if not outline:
        issues.append("Blog brief must include a `## Full Outline` section.")
    else:
        headings = re.findall(r"^###\s+.+$", outline, flags=re.MULTILINE)
        if len(headings) < 2:
            issues.append("Full Outline must include at least two `###` section headings.")

    if not _section_text(text, "Generation Context"):
        issues.append("Blog brief must include a `## Generation Context` section.")
        return issues

    meta = read_meta(slug)
    discovery_decision = _discovery_decision(text)

    if meta.discovery.policy == "required" and not paths.prepared_discovery_source.exists():
        issues.append(
            "Discovery policy is `required` — run the `autobloggy-discovery` skill before approving the brief."
        )
    elif (
        meta.discovery.policy == "ask"
        and not paths.prepared_discovery_source.exists()
        and discovery_decision != "declined"
    ):
        issues.append(
            "Discovery policy is `ask` — ask the operator whether to run discovery. "
            "If they want it, run the `autobloggy-discovery` skill before approving. "
            "If they decline, set `Discovery decision` in blog_brief.md to `declined`."
        )

    resolved_preset = resolve_preset(meta.preset, meta.selections, paths.root)
    expected_paths = {repo_relative_path(resource.path) for resource in resolved_preset.resources.values()}
    expected_paths.add(QUALITY_CRITERIA_PATH)
    expected_paths.add("inputs/prepared/manifest.yaml")

    context_values = _context_values(text)
    context_paths = set(context_values.values())
    for expected in sorted(expected_paths):
        if expected not in context_paths:
            issues.append(f"Generation Context must reference `{expected}`.")

    for value in sorted(context_paths):
        if "/" not in value and not value.endswith((".md", ".html", ".yaml")):
            continue
        resolved = _resolve_brief_reference(value, paths.root)
        if not resolved.exists():
            issues.append(f"Generation Context references missing file `{value}`.")

    return issues


def run_approve_brief(slug: str) -> dict[str, str]:
    issues = brief_approval_issues(slug)
    if issues:
        raise ValueError("Blog brief is incomplete:\n- " + "\n- ".join(issues))
    meta = patch_meta(slug, status="brief_approved", brief_approved_at=now_iso())
    paths = post_paths(slug)
    return {"slug": meta.slug, "status": meta.status, "blog_brief": str(paths.blog_brief)}


def extract_blog_title(blog_brief: str, slug: str) -> str:
    match = re.search(r"^#\s+Blog Brief:\s*(.+)$", blog_brief, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^#\s+(.+)$", blog_brief, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    return slug.replace("-", " ").title()


def run_generate_draft(slug: str) -> dict[str, str]:
    paths = post_paths(slug)
    if not paths.blog_brief.exists():
        raise FileNotFoundError(f"Blog brief does not exist: {paths.blog_brief}")
    meta = read_meta(slug)
    if meta.status != "brief_approved":
        raise ValueError(f"Blog brief is not approved. Review posts/{slug}/blog_brief.md and run `autobloggy approve-brief --slug {slug}` first.")

    resolved_preset = resolve_preset(meta.preset, meta.selections, paths.root)
    template_path = resolved_preset.resources["html_template"].path
    template = read_text(template_path)
    title = extract_blog_title(read_text(paths.blog_brief), slug)
    escaped_title = html.escape(title, quote=False)

    rendered = re.sub(r"<title>[^<]*</title>", f"<title>{escaped_title}</title>", template, count=1)
    rendered, replacements = re.subn(
        r'<main([^>]*)data-content([^>]*)>\s*</main>',
        f'<main\\1data-content\\2>\n    <h1>{escaped_title}</h1>\n  </main>',
        rendered,
        count=1,
    )
    if replacements != 1:
        raise ValueError(f"HTML template must contain an empty `<main data-content></main>`: {template_path}")
    write_text(paths.draft, rendered)
    return {"draft": str(paths.draft)}


def scaffold_preset(name: str, template_name: str = "default") -> Path:
    target_root = presets_root() / name
    if target_root.exists():
        raise ValueError(f"Preset `{name}` already exists at {repo_relative_path(target_root)}.")
    template_root = presets_root() / template_name
    if not template_root.exists():
        raise FileNotFoundError(f"Preset `{template_name}` does not exist.")
    shutil.copytree(template_root, target_root)
    return target_root
