from __future__ import annotations

import re
import shutil
from pathlib import Path

from pptx import Presentation

from .artifacts import extract_frontmatter, format_markdown_with_frontmatter, post_paths, read_text, write_text
from .presets import default_preset_name, preset_paths, presets_root, repo_relative_path, strategy_frontmatter_preset
from .utils import ensure_dir, now_iso, sentences, slugify


class InputContent:
    def __init__(self, title: str, text: str, headings: list[str], urls: list[str], kind: str):
        self.title = title
        self.text = text
        self.headings = headings
        self.urls = urls
        self.kind = kind


REQUIRED_STRATEGY_SECTIONS = (
    "Preset Context",
    "Core Question",
    "Audience",
    "Reader Outcome",
    "Target Voice",
    "Style Guardrails",
    "Must Cover",
    "Must Avoid",
    "Open Questions Before Approval",
    "Approval Checklist",
)

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

UNRESOLVED_STRATEGY_MARKERS = (
    "[REQUIRED:",
    "- [ ]",
)

SUPPORTED_INPUT_SUFFIXES = {".md", ".markdown", ".qmd", ".txt", ".pptx"}
PREFERRED_INPUT_FILENAMES = (
    "input.md",
    "input.markdown",
    "input.qmd",
    "input.txt",
    "input.pptx",
)


def markdown_headings(text: str) -> list[tuple[int, str]]:
    matches = re.finditer(r"^(#{1,6})\s+(.+)$", text, flags=re.MULTILINE)
    return [(len(match.group(1)), match.group(2).strip()) for match in matches]


def clean_markdown_input_text(text: str) -> str:
    lines = [line for line in text.splitlines() if not re.match(r"^\s*#{1,6}\s+", line)]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"https?://[^\s)]+", "", cleaned)
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def usable_markdown_headings(text: str, title: str) -> list[str]:
    excluded = {"questions", "questions to answer", "links", "notes", "sources"}
    headings: list[str] = []
    seen: set[str] = set()
    title_slug = slugify(title)
    for level, heading in markdown_headings(text):
        heading_slug = slugify(heading)
        if heading_slug == title_slug:
            continue
        if heading.lower() in excluded:
            continue
        if level == 1:
            continue
        if heading_slug in seen:
            continue
        seen.add(heading_slug)
        headings.append(heading)
    return headings


def humanize_name(value: str) -> str:
    cleaned = re.sub(r"[-_]+", " ", value).strip()
    return cleaned or "Untitled post"


def dedupe_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized:
            continue
        key = normalized.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(normalized)
    return deduped


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def supported_source_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix.lower() in SUPPORTED_INPUT_SUFFIXES else []
    if not root.exists():
        raise FileNotFoundError(f"Source path does not exist: {root}")
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED_INPUT_SUFFIXES)


def user_asset_files(input_root: Path, exclude: set[Path] | None = None) -> list[Path]:
    excluded = {path.resolve() for path in (exclude or set())}
    if not input_root.exists():
        return []
    return sorted(path for path in input_root.rglob("*") if path.is_file() and path.resolve() not in excluded)


def resolve_input_path(input_candidate: Path) -> Path:
    if input_candidate.is_file():
        if input_candidate.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
            raise ValueError(f"Unsupported input format: {input_candidate.suffix}")
        return input_candidate

    if not input_candidate.is_dir():
        raise FileNotFoundError(f"Input path does not exist: {input_candidate}")

    for filename in PREFERRED_INPUT_FILENAMES:
        candidate = input_candidate / filename
        if candidate.exists():
            return candidate

    candidates = sorted(
        path for path in input_candidate.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_INPUT_SUFFIXES
    )
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ValueError(
            f"No supported main source file found in {input_candidate}. Add one of: {', '.join(PREFERRED_INPUT_FILENAMES)}."
        )
    raise ValueError(
        f"Multiple supported main source files found in {input_candidate}. Keep a single main source file at the top level."
    )


def resolve_main_input_path(input_root: Path) -> Path:
    input_path = input_root / "input.md"
    if input_path.exists():
        return input_path
    return resolve_input_path(input_root)


def parse_input(input_path: Path) -> InputContent:
    input_path = resolve_input_path(input_path)
    suffix = input_path.suffix.lower()
    if suffix in {".md", ".markdown", ".qmd", ".txt"}:
        raw = read_text(input_path)
        frontmatter, body = extract_frontmatter(raw)
        body_headings = markdown_headings(body)
        title = str(frontmatter.get("title") or (body_headings[0][1] if body_headings else input_path.stem))
        urls = re.findall(r"https?://[^\s)]+", raw)
        cleaned_text = clean_markdown_input_text(body)
        headings = usable_markdown_headings(body, title)
        return InputContent(title=title, text=cleaned_text, headings=headings, urls=urls, kind="markdown")

    if suffix == ".pptx":
        presentation = Presentation(input_path)
        slide_titles: list[str] = []
        fragments: list[str] = []
        for index, slide in enumerate(presentation.slides, start=1):
            slide_texts: list[str] = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_texts.append(shape.text.strip())
            if slide_texts:
                slide_titles.append(slide_texts[0].splitlines()[0].strip())
                fragments.append(f"Slide {index}: " + " | ".join(slide_texts))
        text = "\n".join(fragments)
        urls = re.findall(r"https?://[^\s)]+", text)
        title = slide_titles[0] if slide_titles else input_path.stem
        return InputContent(title=title, text=text, headings=slide_titles, urls=urls, kind="pptx")

    raise ValueError(f"Unsupported input format: {input_path.suffix}")


def summarize_text(text: str, max_sentences: int = 3) -> str:
    return " ".join(sentences(text)[:max_sentences]).strip()


def section_slug(heading: str) -> str:
    return slugify(heading) or "section"


def default_must_cover(input_content: InputContent) -> list[str]:
    headings = [heading for heading in input_content.headings if heading.strip()]
    if headings:
        return [heading.rstrip(".") for heading in headings[:5]]
    return [
        f"The real problem or decision behind {input_content.title}",
        "How the workflow, system, or argument works in practice",
        "The key tradeoffs, limits, and failure modes",
    ]


def required_strategy_section_issues(strategy_body: str) -> list[str]:
    issues: list[str] = []
    for heading in REQUIRED_STRATEGY_SECTIONS:
        if not re.search(rf"^##\s+{re.escape(heading)}\s*$", strategy_body, flags=re.MULTILINE):
            issues.append(f"Missing required section: {heading}.")
    return issues


def strategy_approval_issues(strategy_text: str) -> list[str]:
    _, body = extract_frontmatter(strategy_text)
    issues = required_strategy_section_issues(body)

    for marker in UNRESOLVED_STRATEGY_MARKERS:
        if marker in body:
            if marker == "[REQUIRED:":
                issues.append("Resolve every `[REQUIRED: ...]` prompt before approval.")
            elif marker == "- [ ]":
                issues.append("Check every item in the approval checklist before approval.")

    return issues


def outline_approval_issues(outline_text: str) -> list[str]:
    _, body = extract_frontmatter(outline_text)
    issues: list[str] = []
    headings = re.findall(r"^##\s+(.+)$", body, flags=re.MULTILINE)
    if not headings:
        issues.append("Outline has no sections. Add at least one ## heading before approving.")
        return issues

    flagged_headings: list[str] = []
    for heading in headings:
        normalized = heading.strip()
        lowered = normalized.casefold()
        if lowered in NON_PUBLISHABLE_OUTLINE_HEADINGS or lowered.startswith("body section "):
            flagged_headings.append(normalized)

    for heading in flagged_headings:
        issues.append(
            f"Replace generic outline heading `{heading}` with a publishable, reader-facing section title."
        )
    return issues


def extract_section_bullets(body: str, heading: str) -> list[str]:
    match = re.search(rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)", body, flags=re.MULTILINE)
    if not match:
        return []
    return [item.strip() for item in re.findall(r"^\-\s+(.+)$", match.group(1), flags=re.MULTILINE)]


def render_strategy_template(template_text: str, context: dict[str, str]) -> str:
    rendered = template_text
    for key, value in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)

    unresolved = sorted(set(re.findall(r"\{\{([a-z0-9_]+)\}\}", rendered)))
    if unresolved:
        raise ValueError("Strategy template has unresolved tokens: " + ", ".join(unresolved))
    return rendered.strip() + "\n"


def supporting_input_contents(input_root: Path, main_input: Path) -> list[tuple[Path, InputContent]]:
    supporting: list[tuple[Path, InputContent]] = []
    for asset in user_asset_files(input_root, exclude={main_input}):
        if asset.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
            continue
        supporting.append((asset, parse_input(asset)))
    return supporting


def merge_input_contents(main_input: Path, main_content: InputContent, supporting: list[tuple[Path, InputContent]]) -> InputContent:
    headings = main_content.headings[:]
    urls = main_content.urls[:]
    text_parts = [main_content.text] if main_content.text else []

    for path, content in supporting:
        label = path.name
        if content.text.strip():
            text_parts.append(f"{label}\n{content.text.strip()}")
        headings.extend([content.title, *content.headings])
        urls.extend(content.urls)

    return InputContent(
        title=main_content.title,
        text="\n\n".join(part for part in text_parts if part.strip()).strip(),
        headings=dedupe_preserving_order(headings),
        urls=dedupe_preserving_order(urls),
        kind=main_content.kind if not supporting else "bundle",
    )


def load_post_input_bundle(slug: str) -> tuple[Path, InputContent, list[Path]]:
    paths = post_paths(slug)
    main_input = resolve_main_input_path(paths.user_provided_root)
    main_content = parse_input(main_input)
    supporting = supporting_input_contents(paths.user_provided_root, main_input)
    bundle = merge_input_contents(main_input, main_content, supporting)
    return main_input, bundle, [path for path, _ in supporting]


def derive_title(topic: str | None, supporting: list[tuple[Path, InputContent]], assets: list[Path]) -> str:
    if topic and topic.strip():
        for line in topic.splitlines():
            cleaned = line.strip()
            if cleaned:
                return cleaned.rstrip(".")
    if supporting:
        return supporting[0][1].title
    if assets:
        return humanize_name(assets[0].stem)
    return "Untitled post"


def render_input_markdown(title: str, topic: str | None, input_root: Path, assets: list[Path], supporting: list[tuple[Path, InputContent]]) -> str:
    lines = [f"# {title}", ""]

    if topic and topic.strip():
        lines.extend([topic.strip(), ""])
    else:
        lines.extend(["This post starts from the files currently under `inputs/user_provided/`.", ""])

    if assets:
        lines.extend(["## Supporting Materials", ""])
        lines.extend(f"- `{path.relative_to(input_root)}`" for path in assets)
        lines.append("")

    if supporting:
        lines.extend(["## Supporting Material Notes", ""])
        for path, content in supporting:
            summary = summarize_text(content.text, 2) or f"Supporting material from {path.name}."
            lines.extend([f"### {path.relative_to(input_root)}", "", summary, ""])

    frontmatter = {
        "title": title,
        "generated_at": now_iso(),
    }
    return format_markdown_with_frontmatter(frontmatter, "\n".join(lines).strip() + "\n")


def copy_user_source(source: Path, destination_root: Path) -> Path:
    source = source.resolve()
    destination_root = destination_root.resolve()

    if is_relative_to(source, destination_root):
        return source

    ensure_dir(destination_root)
    target = destination_root / source.name
    if source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)
        return target
    if source.is_file():
        shutil.copy2(source, target)
        return target
    raise FileNotFoundError(f"Source path does not exist: {source}")


def generate_strategy(
    slug: str,
    input_content: InputContent,
    input_path: Path,
    input_root: Path,
    preset_name: str,
    repo_context: Path,
) -> str:
    preset = preset_paths(preset_name, repo_context)
    must_cover = default_must_cover(input_content)
    strategy_template_path = repo_relative_path(preset.strategy_template, repo_context)
    writing_guide_path = repo_relative_path(preset.writing_guide, repo_context)
    brand_guide_path = repo_relative_path(preset.brand_guide, repo_context)
    frontmatter = {
        "slug": slug,
        "title": input_content.title,
        "input_path": str(input_path),
        "input_root": str(input_root),
        "input_type": input_content.kind,
        "preset": preset.name,
        "preset_dir": repo_relative_path(preset.root, repo_context),
        "preset_strategy_template": strategy_template_path,
        "preset_writing_guide": writing_guide_path,
        "preset_brand_guide": brand_guide_path,
        "generated_at": now_iso(),
        "status": "needs_review",
    }
    body = render_strategy_template(
        read_text(preset.strategy_template),
        {
            "topic_summary": summarize_text(input_content.text) or f"{input_content.title} is the working topic for this post.",
            "title": input_content.title,
            "preset_name": preset.name,
            "strategy_template_path": strategy_template_path,
            "writing_guide_path": writing_guide_path,
            "brand_guide_path": brand_guide_path,
            "must_cover_bullets": "\n".join(f"- {item}" for item in must_cover),
        },
    )
    template_issues = required_strategy_section_issues(body)
    if template_issues:
        raise ValueError("Preset strategy template is incomplete:\n- " + "\n- ".join(template_issues))
    return format_markdown_with_frontmatter(frontmatter, body)


def generate_outline(strategy_text: str, input_content: InputContent) -> str:
    strategy_frontmatter, _ = extract_frontmatter(strategy_text)
    slug = strategy_frontmatter.get("slug", "")
    title = strategy_frontmatter.get("title", input_content.title)
    preset_name = str(strategy_frontmatter.get("preset") or default_preset_name())
    preset_dir = str(strategy_frontmatter.get("preset_dir") or repo_relative_path(preset_paths(preset_name).root))
    outline_frontmatter = {
        "slug": slug,
        "title": title,
        "preset": preset_name,
        "preset_dir": preset_dir,
        "generated_at": now_iso(),
        "status": "needs_review",
    }
    stub_body = f"# Outline\n\nTitle: {title}\n"
    return format_markdown_with_frontmatter(outline_frontmatter, stub_body)


def generate_draft(strategy_text: str, outline_text: str, input_content: InputContent) -> str:
    frontmatter, strategy_body = extract_frontmatter(strategy_text)
    title = frontmatter.get("title", "Untitled post")
    preset_name = str(frontmatter.get("preset") or default_preset_name())
    preset_dir = str(frontmatter.get("preset_dir") or repo_relative_path(preset_paths(preset_name).root))
    outline_headings = re.findall(r"^##\s+(.+)$", outline_text, flags=re.MULTILINE)
    source_sentences = [
        sentence.rstrip(".")
        for sentence in sentences(input_content.text)
        if len(sentence.split()) >= 6 and not sentence.endswith("?")
    ]
    if not source_sentences:
        source_sentences = [summarize_text(input_content.text, 1) or f"{title} is the focus of this draft."]
    cursor = 0

    draft_frontmatter = {
        "title": title,
        "format": "gfm",
        "preset": preset_name,
        "preset_dir": preset_dir,
    }

    lines = [
        f"# {title}",
        "",
    ]
    intro = summarize_text(strategy_body, 2) or f"{title} is the focus of this draft."
    lines.extend([intro, ""])

    for heading in outline_headings:
        if heading.lower() == "opening":
            continue
        lines.extend([f"## {heading}", ""])
        section_lines = source_sentences[cursor : cursor + 2]
        if not section_lines:
            section_lines = [f"Explain {heading.lower()} with concrete examples, tradeoffs, and operator detail."]
        cursor += len(section_lines)
        for section_line in section_lines:
            lines.append(f"{section_line}.")
            lines.append("")

    if "Conclusion" not in outline_headings:
        lines.extend(["## Conclusion", "", "Close with the practical takeaway.", ""])
    else:
        lines.append("Close with the practical takeaway.")
        lines.append("")

    return format_markdown_with_frontmatter(draft_frontmatter, "\n".join(lines).strip() + "\n")


def scaffold_preset(name: str, template_name: str = "default") -> Path:
    target_root = presets_root() / name
    if target_root.exists():
        raise ValueError(f"Preset `{name}` already exists at {repo_relative_path(target_root)}.")

    template = preset_paths(template_name)
    ensure_dir(target_root)
    for source_file in (template.strategy_template, template.writing_guide, template.brand_guide):
        shutil.copy2(source_file, target_root / source_file.name)
    return target_root


def run_new_post(
    slug: str | None,
    title: str | None,
    topic: str | None,
    source_paths: list[Path] | None = None,
    preset_name: str | None = None,
) -> dict[str, str]:
    source_paths = [path.resolve() for path in (source_paths or [])]
    if not slug and not title and not topic and not source_paths:
        raise ValueError("new-post requires a topic, a title, a slug for an existing input folder, or at least one --source.")

    derived_slug = slug
    if not derived_slug:
        preview_assets = source_paths[:1]
        preview_title = title or derive_title(topic, [], preview_assets)
        derived_slug = slugify(preview_title)

    paths = post_paths(derived_slug)
    if paths.strategy.exists() or paths.outline.exists() or paths.draft.exists():
        raise ValueError(f"Post `{derived_slug}` already has generated artifacts. Use the existing post commands for that post.")

    ensure_dir(paths.user_provided_root)
    for source_path in source_paths:
        copy_user_source(source_path, paths.supporting_root)

    assets = user_asset_files(paths.user_provided_root, exclude={paths.main_input})
    parseable_supporting = [(path, parse_input(path)) for path in assets if path.suffix.lower() in SUPPORTED_INPUT_SUFFIXES]
    if not topic and not assets:
        raise ValueError(
            f"No post brief or supporting files found for `{derived_slug}`. Add files under {paths.user_provided_root} or pass --topic."
        )

    derived_title = title or derive_title(topic, parseable_supporting, assets)
    write_text(paths.main_input, render_input_markdown(derived_title, topic, paths.user_provided_root, assets, parseable_supporting))

    main_input, input_content, _ = load_post_input_bundle(derived_slug)
    resolved_preset_name = preset_name or default_preset_name(paths.root)
    strategy_text = generate_strategy(derived_slug, input_content, main_input, paths.user_provided_root, resolved_preset_name, paths.root)
    write_text(paths.strategy, strategy_text)

    return {
        "slug": derived_slug,
        "preset": resolved_preset_name,
        "input": str(paths.main_input),
        "strategy": str(paths.strategy),
    }


def run_generate_outline(slug: str) -> dict[str, str]:
    paths = post_paths(slug)
    if not paths.strategy.exists():
        raise FileNotFoundError(f"Strategy does not exist: {paths.strategy}")

    main_input, input_content, _ = load_post_input_bundle(slug)
    strategy_text = read_text(paths.strategy)
    frontmatter, _ = extract_frontmatter(strategy_text)
    if frontmatter.get("status") != "approved":
        raise ValueError(
            f"Strategy is not approved. Review posts/{slug}/strategy.md and run `autobloggy approve-strategy --slug {slug}` first."
        )
    discovery_decision = str(frontmatter.get("discovery_decision", "")).strip().lower()
    if discovery_decision not in {"yes", "no"}:
        raise ValueError(
            "Discovery decision is missing. Ask the user for an explicit yes/no decision and run "
            f"`autobloggy decide-discovery --slug {slug} --decision yes|no` before generating the outline."
        )
    if discovery_decision == "yes" and not paths.discovery_summary.exists():
        raise ValueError(
            f"Discovery was approved but not completed. Write discovery output to posts/{slug}/inputs/discovery/discovery.md before generating the outline."
        )

    outline_text = generate_outline(strategy_text, input_content)
    write_text(paths.outline, outline_text)
    return {
        "input": str(main_input),
        "outline": str(paths.outline),
    }


def run_generate_draft(slug: str) -> dict[str, str]:
    paths = post_paths(slug)
    if not paths.strategy.exists():
        raise FileNotFoundError(f"Strategy does not exist: {paths.strategy}")
    if not paths.outline.exists():
        raise FileNotFoundError(f"Outline does not exist: {paths.outline}")

    strategy_text = read_text(paths.strategy)
    strategy_frontmatter, _ = extract_frontmatter(strategy_text)
    if strategy_frontmatter.get("status") != "approved":
        raise ValueError(
            f"Strategy is not approved. Review posts/{slug}/strategy.md and run `autobloggy approve-strategy --slug {slug}` first."
        )

    outline_text = read_text(paths.outline)
    outline_frontmatter, _ = extract_frontmatter(outline_text)
    if outline_frontmatter.get("status") != "approved":
        raise ValueError(
            f"Outline is not approved. Review posts/{slug}/outline.md and run `autobloggy approve-outline --slug {slug}` first."
        )
    outline_issues = outline_approval_issues(outline_text)
    if outline_issues:
        raise ValueError("Outline is not draftable:\n- " + "\n- ".join(outline_issues))

    _, input_content, _ = load_post_input_bundle(slug)
    draft_text = generate_draft(strategy_text, outline_text, input_content)
    write_text(paths.draft, draft_text)
    return {"draft": str(paths.draft)}


def resolve_post_preset(strategy_path: Path, requested_preset: str | None) -> str:
    recorded_preset = strategy_frontmatter_preset(strategy_path)
    if requested_preset and recorded_preset and requested_preset != recorded_preset:
        raise ValueError(
            "Preset mismatch: strategy.md is using preset "
            f"`{recorded_preset}`, but this post was asked to use `{requested_preset}`. "
            "Create a new post with `autobloggy new-post --preset "
            f"{requested_preset}` or keep the recorded preset."
        )

    return requested_preset or recorded_preset or default_preset_name(strategy_path)
