from __future__ import annotations

import re
from pathlib import Path

from pptx import Presentation

from .artifacts import extract_frontmatter, format_markdown_with_frontmatter, post_paths, read_text, write_text
from .utils import now_iso, sentences, slugify


class InputContent:
    def __init__(self, title: str, text: str, headings: list[str], urls: list[str], kind: str):
        self.title = title
        self.text = text
        self.headings = headings
        self.urls = urls
        self.kind = kind


REQUIRED_STRATEGY_SECTIONS = (
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
    "seed.md",
    "seed.markdown",
    "seed.qmd",
    "seed.txt",
    "seed.pptx",
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
        path for path in input_candidate.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED_INPUT_SUFFIXES
    )
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ValueError(
            f"No supported input file found in {input_candidate}. Add one of: {', '.join(PREFERRED_INPUT_FILENAMES)}."
        )
    raise ValueError(
        f"Multiple supported input files found in {input_candidate}. Pass a file path or keep a single canonical input file."
    )


def resolve_seed_path(seed_input: Path) -> Path:
    return resolve_input_path(seed_input)


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


def parse_seed(seed_path: Path) -> InputContent:
    return parse_input(seed_path)


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


def strategy_approval_issues(strategy_text: str) -> list[str]:
    _, body = extract_frontmatter(strategy_text)
    issues: list[str] = []

    for heading in REQUIRED_STRATEGY_SECTIONS:
        if not re.search(rf"^##\s+{re.escape(heading)}\s*$", body, flags=re.MULTILINE):
            issues.append(f"Missing required section: {heading}.")

    for marker in UNRESOLVED_STRATEGY_MARKERS:
        if marker in body:
            if marker == "[REQUIRED:":
                issues.append("Resolve every `[REQUIRED: ...]` prompt before approval.")
            elif marker == "- [ ]":
                issues.append("Check every item in the approval checklist before approval.")

    return issues


def brief_approval_issues(brief_text: str) -> list[str]:
    return strategy_approval_issues(brief_text)


def outline_approval_issues(outline_text: str) -> list[str]:
    _, body = extract_frontmatter(outline_text)
    issues: list[str] = []
    if not re.search(r"^##\s+", body, flags=re.MULTILINE):
        issues.append("Outline has no sections. Add at least one ## heading before approving.")
    return issues


def extract_section_bullets(body: str, heading: str) -> list[str]:
    match = re.search(rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)", body, flags=re.MULTILINE)
    if not match:
        return []
    return [item.strip() for item in re.findall(r"^\-\s+(.+)$", match.group(1), flags=re.MULTILINE)]


def generate_strategy(slug: str, input_content: InputContent, input_path: Path, input_root: Path) -> str:
    frontmatter = {
        "slug": slug,
        "title": input_content.title,
        "input_path": str(input_path),
        "input_root": str(input_root),
        "input_type": input_content.kind,
        "generated_at": now_iso(),
        "status": "needs_review",
    }
    must_cover = default_must_cover(input_content)
    body = "\n".join(
        [
            summarize_text(input_content.text) or f"{input_content.title} is the working topic for this post.",
            "",
            "## Core Question",
            f"What should the reader understand about {input_content.title} by the end of the piece?",
            "",
            "## Audience",
            "[REQUIRED: name the primary reader and the job they are trying to do.]",
            "Operators, engineers, and technical decision makers who need a practical answer, not a survey.",
            "",
            "## Reader Outcome",
            "By the end of the piece, the reader should understand:",
            "- the real problem, decision, or mistaken assumption behind this topic",
            "- how the approach works in practice",
            "- which tradeoffs, risks, and limits matter in the real world",
            "",
            "## Target Voice",
            "[REQUIRED: confirm or replace this with the user's preferred voice.]",
            "Write like a sharp practitioner explaining a hard-earned lesson to other capable builders and operators. The tone should be clear, grounded, and confident, with a slight edge of skepticism toward hype, vague claims, and cargo-cult best practices. Keep the prose conversational and business-aware, but technically credible. Favor plain English, concrete examples, operational implications, and crisp judgments. Aim for practical expert over research paper and working system insight over thought leadership.",
            "",
            "## Style Guardrails",
            "[REQUIRED: edit these guardrails until they match the user's expectations for the piece.]",
            "- Use short to medium sentences.",
            "- Lead with the real problem or mistaken assumption.",
            "- Explain through mechanisms, tradeoffs, and consequences.",
            "- Keep abstractions tied to implementation, decisions, or outcomes.",
            "- Sound opinionated when the material earns it, and precise when nuance matters.",
            "- Make every paragraph useful to a capable reader.",
            "",
            "## Must Cover",
            "[REQUIRED: add or remove points until this captures the non-negotiable substance of the post.]",
            *[f"- {item}" for item in must_cover],
            "",
            "## Must Avoid",
            "[REQUIRED: record any tones, claims, examples, or framing that should be avoided.]",
            "- Hype, vague claims, and generic assistant phrasing.",
            "- Abstract advice with no mechanism, example, or operator takeaway.",
            "- Overclaiming speed, impact, certainty, or generality.",
            "",
            "## Open Questions Before Approval",
            "- [REQUIRED: What specific reader or buyer context should shape the framing?]",
            "- [REQUIRED: Which examples, edge cases, or practical details are mandatory for this audience?]",
            "- [REQUIRED: What should the post sound like, and what should it never sound like?]",
            "- [REQUIRED: What practical takeaway should the reader leave with?]",
            "",
            "## Approval Checklist",
            "- [ ] Audience is specific enough to guide structure and examples.",
            "- [ ] Target voice reflects the user's actual preference, not the default.",
            "- [ ] Style guardrails are concrete enough to guide generation.",
            "- [ ] Must-cover points capture the non-negotiable substance of the post.",
            "- [ ] Must-avoid rules are explicit.",
        ]
    )
    return format_markdown_with_frontmatter(frontmatter, body)


def generate_brief(slug: str, seed: InputContent, seed_path: Path, seed_root: Path) -> str:
    return generate_strategy(slug, seed, seed_path, seed_root)


def generate_outline(strategy_text: str, input_content: InputContent) -> str:
    strategy_frontmatter, body = extract_frontmatter(strategy_text)
    slug = strategy_frontmatter.get("slug", "")
    title = strategy_frontmatter.get("title", input_content.title)
    headings = input_content.headings[:]
    if len(headings) < 2:
        headings = ["Problem", "What Changed", "What It Means"]

    must_cover = extract_section_bullets(body, "Must Cover")
    sections = ["# Outline", "", f"Title: {title}", ""]
    if headings and headings[0].lower() != "opening":
        headings = ["Opening", *headings]
    if not any("conclusion" in heading.lower() for heading in headings):
        headings.append("Conclusion")

    for heading in headings:
        heading_points = [point for point in must_cover if section_slug(point) in section_slug(heading) or section_slug(heading) in section_slug(point)]
        if not heading_points:
            heading_points = [
                f"State the key question or tension behind {heading.lower()}.",
                f"Add concrete examples or operator detail for {heading.lower()}.",
                f"Show why {heading.lower()} matters for the reader's decision or workflow.",
            ]
        sections.extend(
            [
                f"## {heading}",
                *[f"- {point}" for point in heading_points[:3]],
                "",
            ]
        )
    outline_frontmatter = {
        "slug": slug,
        "title": title,
        "generated_at": now_iso(),
        "status": "needs_review",
    }
    return format_markdown_with_frontmatter(outline_frontmatter, "\n".join(sections).strip() + "\n")


def generate_draft(strategy_text: str, outline_text: str, input_content: InputContent) -> str:
    frontmatter, strategy_body = extract_frontmatter(strategy_text)
    title = frontmatter.get("title", "Untitled post")
    outline_headings = re.findall(r"^##\s+(.+)$", outline_text, flags=re.MULTILINE)
    source_sentences = [
        sentence.rstrip(".")
        for sentence in sentences(input_content.text)
        if len(sentence.split()) >= 6 and not sentence.endswith("?")
    ]
    if not source_sentences:
        source_sentences = [summarize_text(input_content.text, 1) or f"{title} is the focus of this draft."]
    cursor = 0

    lines = ["---", "title: " + str(title), "format: gfm", "---", "", f"# {title}", ""]
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

    return "\n".join(lines).strip() + "\n"


def existing_strategy_path(paths) -> Path:
    legacy_path = paths.root / "brief.md"
    if paths.strategy.exists():
        return paths.strategy
    if legacy_path.exists():
        return legacy_path
    return paths.strategy


def run_prepare(slug: str, input_path: Path, through: str) -> dict[str, str]:
    input_path = resolve_input_path(input_path)
    input_content = parse_input(input_path)
    through = "strategy" if through == "brief" else through
    paths = post_paths(slug)
    strategy_path = existing_strategy_path(paths)
    input_root = input_path.parent
    paths.root.mkdir(parents=True, exist_ok=True)
    generated: dict[str, str] = {}

    if through == "strategy" or not strategy_path.exists():
        strategy_text = generate_strategy(slug, input_content, input_path, input_root)
        write_text(paths.strategy, strategy_text)
        generated["strategy"] = str(paths.strategy)
    else:
        strategy_text = read_text(strategy_path)

    if through == "strategy":
        return generated

    if through == "outline" or not paths.outline.exists():
        outline_text = generate_outline(strategy_text, input_content)
        write_text(paths.outline, outline_text)
        generated["outline"] = str(paths.outline)
    else:
        outline_text = read_text(paths.outline)

    if through == "outline":
        return generated

    draft_text = generate_draft(strategy_text, outline_text, input_content)
    write_text(paths.draft, draft_text)
    generated["draft"] = str(paths.draft)
    return generated
