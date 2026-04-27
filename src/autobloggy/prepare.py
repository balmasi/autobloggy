from __future__ import annotations

import re
import shutil
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
from .models import InputManifest, InputTextSource
from .presets import default_preset_name, preset_paths, presets_root, repo_relative_path
from .utils import ensure_dir, now_iso, sentences, slugify


TEXT_INPUT_SUFFIXES = {".md", ".markdown", ".txt"}
NON_PUBLISHABLE_OUTLINE_HEADINGS = {
    "hook",
    "opening",
    "context",
    "thesis",
    "problem",
    "what changed",
    "what it means",
    "decision table",
    "implications",
    "closing",
    "conclusion",
    "drafting notes",
    "notes for drafting",
}


# ---------- inputs ----------

def render_user_input_readme() -> str:
    return (
        "# User Inputs\n\n"
        "Use this folder only for human-owned material.\n\n"
        "- Put the plain-language post brief in `brief.md`.\n"
        "- Put original source files and folders under `raw/`.\n"
        "- Do not put generated files under `user_provided/`.\n"
        "- `../prepared/` contains the canonical LLM-facing bundle. It can be rebuilt.\n"
    )


def render_brief_template() -> str:
    return (
        "<!--\n"
        "Add the plain-language brief here when you are not giving it conversationally.\n"
        "Include the topic, audience, must-cover points, and must-avoid framing.\n"
        "-->\n"
    )


def render_brief_markdown(title: str | None, topic: str) -> str:
    heading = title or next((line.strip().rstrip(".") for line in topic.splitlines() if line.strip()), "Post brief")
    return f"# {heading}\n\n{topic.strip()}\n"


def scaffold_input_layout(slug: str) -> None:
    paths = post_paths(slug)
    ensure_dir(paths.user_provided_root)
    ensure_dir(paths.user_raw_root)
    ensure_dir(paths.prepared_root)
    ensure_dir(paths.discovery_root)
    if not paths.user_readme.exists():
        write_text(paths.user_readme, render_user_input_readme())
    if not paths.user_brief.exists():
        write_text(paths.user_brief, render_brief_template())


def brief_has_substance(brief_path: Path) -> bool:
    if not brief_path.exists():
        return False
    text = read_text(brief_path)
    cleaned = re.sub(r"<!--[\s\S]*?-->", "", text).strip()
    return bool(cleaned)


def raw_source_files(slug: str) -> list[Path]:
    paths = post_paths(slug)
    if not paths.user_raw_root.exists():
        return []
    return sorted(p for p in paths.user_raw_root.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_INPUT_SUFFIXES)


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


def post_relative_path(path: Path, post_root: Path) -> str:
    return str(path.resolve().relative_to(post_root.resolve()))


def derived_title(slug: str, brief_text: str | None, raw_files: list[Path]) -> str:
    if brief_text:
        for line in brief_text.splitlines():
            stripped = line.strip().lstrip("#").strip()
            if stripped and not stripped.startswith("<!--"):
                return stripped.rstrip(".")
    if raw_files:
        first = raw_files[0]
        return first.stem.replace("-", " ").replace("_", " ").strip().title() or first.stem
    return slug.replace("-", " ").title()


def render_prepared_input_markdown(title: str, brief_text: str | None, raw_files: list[Path], post_root: Path) -> str:
    lines = [f"# {title}", ""]
    if brief_text and brief_text.strip():
        lines.extend(["## Brief", "", brief_text.strip(), ""])
    if raw_files:
        lines.extend(["## Source files", ""])
        for path in raw_files:
            rel = post_relative_path(path, post_root)
            lines.append(f"### `{rel}`")
            lines.append("")
            try:
                lines.append(read_text(path).strip())
            except Exception:
                lines.append(f"_could not read {rel}_")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def prepare_post_inputs(slug: str, require_sources: bool = True) -> dict[str, str]:
    paths = post_paths(slug)
    scaffold_input_layout(slug)
    brief_text = read_text(paths.user_brief) if brief_has_substance(paths.user_brief) else None
    raw_files = raw_source_files(slug)

    if require_sources and brief_text is None and not raw_files:
        raise ValueError(
            f"No post brief or raw source files found for `{slug}`. "
            f"Add content to {paths.user_brief} or place files under {paths.user_raw_root}, "
            f"then run `autobloggy prepare-inputs --slug {slug}`."
        )

    title = derived_title(slug, brief_text, raw_files)
    prepared = render_prepared_input_markdown(title, brief_text, raw_files, paths.root)
    write_text(paths.prepared_input, prepared)

    sources = [
        InputTextSource(
            path=post_relative_path(p, paths.root),
            kind="markdown",
            title=p.stem,
        )
        for p in raw_files
    ]
    manifest = InputManifest(
        generated_at=now_iso(),
        brief=post_relative_path(paths.user_brief, paths.root) if brief_text else None,
        raw_text_sources=sources,
        canonical_input=post_relative_path(paths.prepared_input, paths.root),
    )
    write_yaml(paths.input_manifest, manifest.model_dump(mode="json"))
    return {
        "brief": str(paths.user_brief),
        "manifest": str(paths.input_manifest),
        "input": str(paths.prepared_input),
    }


# ---------- strategy ----------

def summarize_text(text: str, max_sentences: int = 3) -> str:
    return " ".join(sentences(text)[:max_sentences]).strip()


def default_must_cover(input_content_text: str, title: str) -> list[str]:
    headings = re.findall(r"^##\s+(.+)$", input_content_text, flags=re.MULTILINE)
    if headings:
        return [h.strip().rstrip(".") for h in headings[:5]]
    return [
        f"The real problem or decision behind {title}",
        "How the workflow, system, or argument works in practice",
        "The key tradeoffs, limits, and failure modes",
    ]


def render_strategy_template(template_text: str, context: dict[str, str]) -> str:
    rendered = template_text
    for key, value in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    unresolved = sorted(set(re.findall(r"\{\{([a-z0-9_]+)\}\}", rendered)))
    if unresolved:
        raise ValueError("Strategy template has unresolved tokens: " + ", ".join(unresolved))
    return rendered.strip() + "\n"


def run_generate_strategy(slug: str) -> dict[str, str]:
    paths = post_paths(slug)
    if not paths.prepared_input.exists():
        prepare_post_inputs(slug, require_sources=True)
    meta = read_meta(slug)
    preset = preset_paths(meta.preset)
    input_text = read_text(paths.prepared_input)
    title_match = re.search(r"^#\s+(.+)$", input_text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else slug.replace("-", " ").title()
    must_cover = default_must_cover(input_text, title)
    body = render_strategy_template(
        read_text(preset.strategy_template),
        {
            "topic_summary": summarize_text(input_text) or f"{title} is the working topic for this post.",
            "title": title,
            "preset_name": preset.name,
            "strategy_template_path": repo_relative_path(preset.strategy_template),
            "writing_guide_path": repo_relative_path(preset.writing_guide),
            "brand_guide_path": repo_relative_path(preset.brand_guide),
            "must_cover_bullets": "\n".join(f"- {item}" for item in must_cover),
        },
    )
    write_text(paths.strategy, body)
    return {"strategy": str(paths.strategy)}


# ---------- outline ----------

OUTLINE_STUB = (
    "# Outline\n\n"
    "Title: {title}\n\n"
    "_Replace the section headings below with publishable, reader-facing titles before approving._\n\n"
    "## Section one\n- bullet\n\n## Section two\n- bullet\n\n## Section three\n- bullet\n"
)


def outline_approval_issues(outline_text: str) -> list[str]:
    issues: list[str] = []
    headings = re.findall(r"^##\s+(.+)$", outline_text, flags=re.MULTILINE)
    if not headings:
        issues.append("Outline has no sections. Add at least one ## heading before approving.")
        return issues
    for heading in headings:
        normalized = heading.strip()
        lowered = normalized.casefold()
        if lowered in NON_PUBLISHABLE_OUTLINE_HEADINGS or lowered.startswith("body section ") or lowered.startswith("section "):
            issues.append(
                f"Replace generic outline heading `{normalized}` with a publishable, reader-facing section title."
            )
    return issues


def run_generate_outline(slug: str) -> dict[str, str]:
    paths = post_paths(slug)
    if not paths.strategy.exists():
        raise FileNotFoundError(f"Strategy does not exist: {paths.strategy}")
    meta = read_meta(slug)
    if meta.discovery_decision not in {"yes", "no"}:
        raise ValueError(
            "Discovery decision is missing. Ask the user for an explicit yes/no decision and run "
            f"`autobloggy decide-discovery --slug {slug} --decision yes|no` before generating the outline."
        )
    if meta.discovery_decision == "yes" and not paths.discovery_summary.exists():
        raise ValueError(
            f"Discovery was approved but not completed. Write discovery output to posts/{slug}/inputs/discovery/discovery.md before generating the outline."
        )
    strategy_text = read_text(paths.strategy)
    title_match = re.search(r"##\s+Core Question\s*\n\n([^\n]+)", strategy_text)
    title = title_match.group(1).strip() if title_match else slug.replace("-", " ").title()
    write_text(paths.outline, OUTLINE_STUB.format(title=title))
    return {"outline": str(paths.outline)}


# ---------- draft ----------

def run_generate_draft(slug: str) -> dict[str, str]:
    paths = post_paths(slug)
    if not paths.strategy.exists():
        raise FileNotFoundError(f"Strategy does not exist: {paths.strategy}")
    if not paths.outline.exists():
        raise FileNotFoundError(f"Outline does not exist: {paths.outline}")
    meta = read_meta(slug)
    if meta.status != "outline_approved":
        raise ValueError(
            f"Outline is not approved. Review posts/{slug}/outline.md and run `autobloggy approve-outline --slug {slug}` first."
        )
    issues = outline_approval_issues(read_text(paths.outline))
    if issues:
        raise ValueError("Outline is not draftable:\n- " + "\n- ".join(issues))

    preset = preset_paths(meta.preset)
    template = read_text(preset.template_html)

    title_match = re.search(r"^Title:\s*(.+)$", read_text(paths.outline), flags=re.MULTILINE)
    title = (title_match.group(1).strip() if title_match else slug.replace("-", " ").title())

    rendered = template
    rendered = re.sub(
        r"<title>[^<]*</title>",
        f"<title>{title}</title>",
        rendered,
        count=1,
    )
    rendered = re.sub(
        r'<main([^>]*)data-content([^>]*)>\s*</main>',
        f'<main\\1data-content\\2>\n    <h1>{title}</h1>\n  </main>',
        rendered,
        count=1,
    )
    write_text(paths.draft, rendered)
    return {"draft": str(paths.draft)}


# ---------- preset scaffolding ----------

def scaffold_preset(name: str, template_name: str = "default") -> Path:
    target_root = presets_root() / name
    if target_root.exists():
        raise ValueError(f"Preset `{name}` already exists at {repo_relative_path(target_root)}.")
    template = preset_paths(template_name)
    ensure_dir(target_root)
    for source_file in (
        template.strategy_template,
        template.writing_guide,
        template.brand_guide,
        template.template_html,
    ):
        shutil.copy2(source_file, target_root / source_file.name)
    return target_root


# ---------- new-post ----------

def run_new_post(
    slug: str | None,
    title: str | None,
    topic: str | None,
    source_paths: list[Path] | None = None,
    preset_name: str | None = None,
) -> dict[str, str]:
    source_paths = [path.resolve() for path in (source_paths or [])]
    if not slug and not title and not topic and not source_paths:
        raise ValueError("new-post requires a slug, a topic, a title, or at least one --source.")

    derived_slug = slug
    if not derived_slug:
        preview_title = title or next((path.stem for path in source_paths if path.name), None) or topic or "post"
        derived_slug = slugify(preview_title)

    paths = post_paths(derived_slug)
    if paths.strategy.exists() or paths.outline.exists() or paths.draft.exists():
        raise ValueError(f"Post `{derived_slug}` already has generated artifacts.")

    scaffold_input_layout(derived_slug)
    if topic is not None or title is not None:
        write_text(paths.user_brief, render_brief_markdown(title, topic or ""))

    for source_path in source_paths:
        copy_user_source(source_path, paths.user_raw_root)

    resolved_preset = preset_name or default_preset_name(paths.root)
    # Validate preset exists.
    preset_paths(resolved_preset)
    init_meta(derived_slug, resolved_preset)

    payload = {
        "slug": derived_slug,
        "preset": resolved_preset,
        "brief": str(paths.user_brief),
        "meta": str(paths.meta),
    }

    has_brief = brief_has_substance(paths.user_brief)
    has_raw = bool(raw_source_files(derived_slug))
    if not has_brief and not has_raw:
        payload["status"] = "scaffolded"
        payload["next_step"] = (
            f"Add a brief to {paths.user_brief} or place source files under {paths.user_raw_root}, "
            f"then run `autobloggy prepare-inputs --slug {derived_slug}`."
        )
        return payload

    prepared = prepare_post_inputs(derived_slug, require_sources=True)
    payload.update(prepared)
    payload["status"] = "scaffolded"
    return payload
