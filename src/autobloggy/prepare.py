from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from pptx import Presentation

from .artifacts import (
    claim_fingerprint,
    extract_frontmatter,
    format_markdown_with_frontmatter,
    post_paths,
    read_claims,
    read_sources,
    read_text,
    write_claims,
    write_sources,
    write_text,
)
from .models import ClaimRecord, ClaimsDocument, SourceRecord, SourceSnippet, SourcesDocument
from .utils import now_iso, sentences, slugify


class SeedContent:
    def __init__(self, title: str, text: str, headings: list[str], urls: list[str], kind: str):
        self.title = title
        self.text = text
        self.headings = headings
        self.urls = urls
        self.kind = kind


REQUIRED_BRIEF_SECTIONS = (
    "Core Question",
    "Audience",
    "Reader Outcome",
    "Target Voice",
    "Style Guardrails",
    "Must Cover",
    "Must Avoid",
    "Evidence Standards",
    "Open Questions Before Approval",
    "Approval Checklist",
)

UNRESOLVED_BRIEF_MARKERS = (
    "[REQUIRED:",
    "- [ ]",
)

SUPPORTED_SEED_SUFFIXES = {".md", ".markdown", ".qmd", ".txt", ".pptx"}
PREFERRED_SEED_FILENAMES = (
    "seed.md",
    "seed.markdown",
    "seed.qmd",
    "seed.txt",
    "seed.pptx",
)


def markdown_headings(text: str) -> list[tuple[int, str]]:
    matches = re.finditer(r"^(#{1,6})\s+(.+)$", text, flags=re.MULTILINE)
    return [(len(match.group(1)), match.group(2).strip()) for match in matches]


def clean_markdown_seed_text(text: str) -> str:
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


def resolve_seed_path(seed_input: Path) -> Path:
    if seed_input.is_file():
        if seed_input.suffix.lower() not in SUPPORTED_SEED_SUFFIXES:
            raise ValueError(f"Unsupported seed format: {seed_input.suffix}")
        return seed_input

    if not seed_input.is_dir():
        raise FileNotFoundError(f"Seed path does not exist: {seed_input}")

    for filename in PREFERRED_SEED_FILENAMES:
        candidate = seed_input / filename
        if candidate.exists():
            return candidate

    candidates = sorted(
        path for path in seed_input.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED_SEED_SUFFIXES
    )
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ValueError(
            f"No supported seed file found in {seed_input}. Add one of: {', '.join(PREFERRED_SEED_FILENAMES)}."
        )
    raise ValueError(
        f"Multiple supported seed files found in {seed_input}. Pass a file path or keep a single canonical seed file."
    )


def parse_seed(seed_path: Path) -> SeedContent:
    seed_path = resolve_seed_path(seed_path)
    suffix = seed_path.suffix.lower()
    if suffix in {".md", ".markdown", ".qmd", ".txt"}:
        raw = read_text(seed_path)
        frontmatter, body = extract_frontmatter(raw)
        body_headings = markdown_headings(body)
        title = str(frontmatter.get("title") or (body_headings[0][1] if body_headings else seed_path.stem))
        urls = re.findall(r"https?://[^\s)]+", raw)
        cleaned_text = clean_markdown_seed_text(body)
        headings = usable_markdown_headings(body, title)
        return SeedContent(title=title, text=cleaned_text, headings=headings, urls=urls, kind="markdown")

    if suffix == ".pptx":
        presentation = Presentation(seed_path)
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
        title = slide_titles[0] if slide_titles else seed_path.stem
        return SeedContent(title=title, text=text, headings=slide_titles, urls=urls, kind="pptx")

    raise ValueError(f"Unsupported seed format: {seed_path.suffix}")


def summarize_text(text: str, max_sentences: int = 3) -> str:
    return " ".join(sentences(text)[:max_sentences]).strip()


def section_slug(heading: str) -> str:
    return slugify(heading) or "section"


def default_must_cover(seed: SeedContent) -> list[str]:
    headings = [heading for heading in seed.headings if heading.strip()]
    if headings:
        return [heading.rstrip(".") for heading in headings[:5]]
    return [
        f"The real problem or decision behind {seed.title}",
        "How the workflow, system, or argument works in practice",
        "The key tradeoffs, limits, and failure modes",
    ]


def brief_approval_issues(brief_text: str) -> list[str]:
    _, body = extract_frontmatter(brief_text)
    issues: list[str] = []

    for heading in REQUIRED_BRIEF_SECTIONS:
        if not re.search(rf"^##\s+{re.escape(heading)}\s*$", body, flags=re.MULTILINE):
            issues.append(f"Missing required section: {heading}.")

    for marker in UNRESOLVED_BRIEF_MARKERS:
        if marker in body:
            if marker == "[REQUIRED:":
                issues.append("Resolve every `[REQUIRED: ...]` prompt before approval.")
            elif marker == "- [ ]":
                issues.append("Check every item in the approval checklist before approval.")

    return issues


def generate_brief(slug: str, seed: SeedContent, seed_path: Path, seed_root: Path) -> str:
    frontmatter = {
        "slug": slug,
        "title": seed.title,
        "seed_path": str(seed_path),
        "seed_root": str(seed_root),
        "seed_type": seed.kind,
        "generated_at": now_iso(),
        "status": "needs_review",
    }
    must_cover = default_must_cover(seed)
    body = "\n".join(
        [
            summarize_text(seed.text) or f"{seed.title} is the working topic for this post.",
            "",
            "## Core Question",
            f"What should the reader understand about {seed.title} by the end of the piece?",
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
            "- Sound opinionated when the evidence earns it, and precise when nuance matters.",
            "- Make every paragraph useful to a capable reader.",
            "",
            "## Must Cover",
            "[REQUIRED: add or remove points until this captures the non-negotiable substance of the post.]",
            *[f"- {item}" for item in must_cover],
            "",
            "## Must Avoid",
            "[REQUIRED: record any tones, claims, examples, or framing that should be avoided.]",
            "- Hype, vague claims, and generic assistant phrasing.",
            "- Abstract advice with no mechanism, evidence, or operator takeaway.",
            "- Overclaiming speed, impact, certainty, or generality.",
            "",
            "## Evidence Standards",
            "- Prefer primary evidence.",
            "- Keep claims traceable to source IDs.",
            "- If a point depends on secondary reporting or anecdote, label that clearly.",
            "",
            "## Open Questions Before Approval",
            "- [REQUIRED: What specific reader or buyer context should shape the framing?]",
            "- [REQUIRED: Which claims or examples are mandatory because they matter to this audience?]",
            "- [REQUIRED: What should the post sound like, and what should it never sound like?]",
            "- [REQUIRED: What practical takeaway should the reader leave with?]",
            "",
            "## Approval Checklist",
            "- [ ] Audience is specific enough to guide structure and examples.",
            "- [ ] Target voice reflects the user's actual preference, not the default.",
            "- [ ] Style guardrails are concrete enough to guide generation.",
            "- [ ] Must-cover points capture the non-negotiable substance of the post.",
            "- [ ] Must-avoid and evidence rules are explicit.",
        ]
    )
    return format_markdown_with_frontmatter(frontmatter, body)


def generate_outline(brief_text: str, seed: SeedContent) -> str:
    frontmatter, _ = extract_frontmatter(brief_text)
    title = frontmatter.get("title", seed.title)
    headings = seed.headings[:]
    if len(headings) < 2:
        headings = ["Problem", "What Changed", "What It Means"]

    sections = ["# Outline", "", f"Title: {title}", ""]
    if headings and headings[0].lower() != "opening":
        headings = ["Opening", *headings]
    if not any("conclusion" in heading.lower() for heading in headings):
        headings.append("Conclusion")

    for heading in headings:
        sections.extend(
            [
                f"## {heading}",
                f"Purpose: Explain {heading.lower()} with one clear argument and explicit evidence.",
                "",
            ]
        )
    return "\n".join(sections).strip() + "\n"


def extract_claim_texts(seed: SeedContent, headings: list[str]) -> list[tuple[str, str]]:
    raw_sentences = sentences(seed.text)
    candidate_sentences = [line for line in raw_sentences if len(line.split()) >= 6 and not line.endswith("?")]
    if not candidate_sentences:
        candidate_sentences = [summarize_text(seed.text, 1) or f"{seed.title} is the topic of this post."]
    pairs: list[tuple[str, str]] = []
    for index, sentence in enumerate(candidate_sentences[: max(3, len(headings))], start=1):
        heading = headings[min(index - 1, len(headings) - 1)] if headings else "Opening"
        pairs.append((sentence.rstrip("."), section_slug(heading)))
    return pairs


def build_source_registry(
    seed: SeedContent, seed_path: Path, seed_root: Path, existing: SourcesDocument | None = None
) -> SourcesDocument:
    existing_sources = {source.id: source for source in (existing.sources if existing else [])}
    local_source_id = "src-seed"
    local_source = SourceRecord(
        id=local_source_id,
        title=seed.title,
        kind="local_pptx" if seed.kind == "pptx" else "local_markdown",
        locator=str(seed_path),
        notes=f"Original seed material. Supporting seed files live under {seed_root}.",
        snippets=[SourceSnippet(id="snip-seed-001", text=summarize_text(seed.text, 2) or seed.title)],
    )
    existing_sources[local_source_id] = local_source

    deduped_urls: list[str] = []
    seen_urls: set[str] = set()
    for url in seed.urls:
        if url in seen_urls:
            continue
        seen_urls.add(url)
        deduped_urls.append(url)

    for index, url in enumerate(deduped_urls, start=1):
        parsed = urlparse(url)
        source_id = f"src-url-{index:03d}"
        existing_sources[source_id] = SourceRecord(
            id=source_id,
            title=parsed.netloc or url,
            kind="url",
            locator=url,
            notes="Discovered from seed content.",
            snippets=[SourceSnippet(id=f"snip-url-{index:03d}", text=url)],
        )

    ordered = [existing_sources[key] for key in sorted(existing_sources)]
    return SourcesDocument(sources=ordered)


def merge_claims(existing: ClaimsDocument | None, extracted_claims: list[tuple[str, str]], source_ids: list[str]) -> ClaimsDocument:
    existing_by_id = {claim.id: claim for claim in (existing.claims if existing else [])}
    active_existing = [claim for claim in existing_by_id.values() if claim.status == "active"]
    used_ids: set[str] = set()
    merged: list[ClaimRecord] = []
    next_numeric_id = max(
        [int(match.group(1)) for claim_id in existing_by_id for match in [re.match(r"clm-(\d+)$", claim_id)] if match],
        default=0,
    )

    for index, (text, section) in enumerate(extracted_claims, start=1):
        matched = next((claim for claim in active_existing if claim.text == text), None)
        if matched:
            claim_id = matched.id
        else:
            next_numeric_id += 1
            claim_id = f"clm-{next_numeric_id:03d}"
        while claim_id in used_ids:
            next_numeric_id += 1
            claim_id = f"clm-{next_numeric_id:03d}"
        used_ids.add(claim_id)
        record = ClaimRecord(
            id=claim_id,
            text=text,
            section=section,
            source_ids=matched.source_ids if matched else source_ids,
            status="active",
        )
        fingerprint = claim_fingerprint(record.model_dump(mode="json"))
        previous = existing_by_id.get(claim_id)
        if previous and previous.last_verification.claim_fingerprint == fingerprint:
            record.last_verification = previous.last_verification
        else:
            record.last_verification.claim_fingerprint = fingerprint
            record.last_verification.status = "needs_rerun"
            record.last_verification.reason = "claim changed"
        merged.append(record)

    for claim in active_existing:
        if claim.id not in used_ids:
            claim.status = "inactive"
            claim.last_verification.status = "needs_rerun"
            claim.last_verification.reason = "claim removed from extracted set"
            merged.append(claim)

    merged.sort(key=lambda item: item.id)
    return ClaimsDocument(claims=merged)


def generate_draft(brief_text: str, outline_text: str, claims: ClaimsDocument) -> str:
    frontmatter, brief_body = extract_frontmatter(brief_text)
    title = frontmatter.get("title", "Untitled post")
    outline_headings = re.findall(r"^##\s+(.+)$", outline_text, flags=re.MULTILINE)
    claims_by_section: dict[str, list[ClaimRecord]] = {}
    for claim in claims.claims:
        if claim.status != "active":
            continue
        claims_by_section.setdefault(claim.section, []).append(claim)

    lines = ["---", "title: " + str(title), "format: gfm", "---", "", f"# {title}", ""]
    intro = summarize_text(brief_body, 2) or f"{title} is the focus of this draft."
    lines.extend([intro, ""])

    for heading in outline_headings:
        if heading.lower() == "opening":
            continue
        lines.extend([f"## {heading}", ""])
        section_key = section_slug(heading)
        section_claims = claims_by_section.get(section_key, [])
        if not section_claims:
            lines.append(f"Explain {heading.lower()} with concrete evidence and citekeys.")
            lines.append("")
            continue
        for claim in section_claims:
            citation = f" [@{claim.source_ids[0]}]" if claim.source_ids else ""
            lines.append(f"{claim.text}.{citation}")
            lines.append("")

    if "Conclusion" not in outline_headings:
        lines.extend(["## Conclusion", "", "Close with the practical takeaway.", ""])
    else:
        lines.append("Close with the practical takeaway.")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def run_prepare(slug: str, seed_path: Path, through: str) -> dict[str, str]:
    seed_path = resolve_seed_path(seed_path)
    seed = parse_seed(seed_path)
    paths = post_paths(slug)
    seed_root = seed_path.parent
    paths.root.mkdir(parents=True, exist_ok=True)
    generated: dict[str, str] = {}

    if through == "brief" or not paths.brief.exists():
        brief_text = generate_brief(slug, seed, seed_path, seed_root)
        write_text(paths.brief, brief_text)
        generated["brief"] = str(paths.brief)
    else:
        brief_text = read_text(paths.brief)

    if through == "brief":
        return generated

    if through == "outline" or not paths.outline.exists():
        outline_text = generate_outline(brief_text, seed)
        write_text(paths.outline, outline_text)
        generated["outline"] = str(paths.outline)
    else:
        outline_text = read_text(paths.outline)

    if through == "outline":
        return generated

    headings = re.findall(r"^##\s+(.+)$", outline_text, flags=re.MULTILINE)
    existing_claims = read_claims(paths.claims) if paths.claims.exists() else None
    existing_sources = read_sources(paths.sources) if paths.sources.exists() else None
    source_doc = build_source_registry(seed, seed_path, seed_root, existing_sources)
    source_ids = [source.id for source in source_doc.sources[:1]]
    claim_doc = merge_claims(existing_claims, extract_claim_texts(seed, headings), source_ids)
    write_sources(paths.sources, source_doc)
    write_claims(paths.claims, claim_doc)
    generated["claims"] = str(paths.claims)
    generated["sources"] = str(paths.sources)
    if through == "claims":
        return generated

    draft_text = generate_draft(brief_text, outline_text, claim_doc)
    write_text(paths.draft, draft_text)
    generated["draft"] = str(paths.draft)
    return generated
