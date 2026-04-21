from __future__ import annotations

import re
from pathlib import Path

import yaml

from .artifacts import cited_source_ids, extract_frontmatter, read_claims, read_sources, read_text
from .models import CheckResult, CheckSummary
from .utils import now_iso, paragraphs, repo_root, sentences, words


def load_banned_patterns() -> list[str]:
    root = repo_root()
    raw = yaml.safe_load((root / "shared" / "banned_patterns.yaml").read_text(encoding="utf-8")) or {}
    return list(raw.get("patterns", []))


def sentence_word_counts(text: str) -> list[int]:
    return [len(words(sentence)) for sentence in sentences(text)]


def readability_penalty(text: str) -> int:
    counts = sentence_word_counts(text)
    if not counts:
        return 5
    average = sum(counts) / len(counts)
    if average < 8:
        return 8 - int(average)
    if average > 26:
        return int(average) - 26
    return 0


def image_caption_failures(text: str) -> int:
    failures = 0
    lines = text.splitlines()
    for index, line in enumerate(lines):
        image_match = re.search(r"!\[(.*?)\]\((.*?)\)", line)
        if not image_match:
            continue
        if not image_match.group(1).strip():
            failures += 1
            continue
        next_non_empty = ""
        for follow in lines[index + 1 :]:
            if follow.strip():
                next_non_empty = follow.strip()
                break
        if not (next_non_empty.startswith("*Caption:*") or next_non_empty.startswith("Figure:")):
            failures += 1
    return failures


def code_fence_language_failures(text: str) -> int:
    failures = 0
    for line in text.splitlines():
        if line.startswith("```") and line.strip() == "```":
            failures += 1
    return failures


def latex_failures(text: str) -> int:
    inline_count = text.count("$")
    display_count = text.count("$$")
    return 1 if inline_count % 2 != 0 or display_count % 2 != 0 else 0


def paragraph_intro_exists(text: str) -> bool:
    blocks = paragraphs(text)
    if len(blocks) < 2:
        return False
    first_non_title = next((block for block in blocks if not block.startswith("# ")), "")
    return bool(first_non_title and len(words(first_non_title)) >= 10)


def conclusion_exists(text: str) -> bool:
    return bool(re.search(r"^##\s+(Conclusion|Takeaways?|Closing)\b", text, flags=re.MULTILINE | re.IGNORECASE))


def valid_heading_order(text: str) -> bool:
    levels = [len(match.group(1)) for match in re.finditer(r"^(#+)\s+.+$", text, flags=re.MULTILINE)]
    if not levels:
        return False
    return all(next_level - current_level <= 1 for current_level, next_level in zip(levels, levels[1:]))


def run_checks(draft_path: Path, claims_path: Path, sources_path: Path) -> CheckSummary:
    draft_text = read_text(draft_path)
    _, draft_body = extract_frontmatter(draft_text)
    if draft_body:
        draft_text = draft_body
    claims_doc = read_claims(claims_path)
    sources_doc = read_sources(sources_path)
    source_ids = {source.id for source in sources_doc.sources}
    banned = load_banned_patterns()

    h1_count = len(re.findall(r"^#\s+.+$", draft_text, flags=re.MULTILINE))
    banned_hits = [pattern for pattern in banned if pattern.lower() in draft_text.lower()]
    missing_claims = [
        claim.id
        for claim in claims_doc.claims
        if claim.status == "active" and claim.text not in draft_text
    ]

    cited_ids = cited_source_ids(draft_text)
    unknown_citations = sorted({source_id for source_id in cited_ids if source_id not in source_ids})

    results = [
        CheckResult(id="one_h1", passed=h1_count == 1, details=f"Found {h1_count} H1 headings."),
        CheckResult(id="heading_order", passed=valid_heading_order(draft_text), details="Heading levels must not jump by more than one."),
        CheckResult(id="intro_exists", passed=paragraph_intro_exists(draft_text), details="Intro paragraph must exist before deeper sections."),
        CheckResult(id="conclusion_exists", passed=conclusion_exists(draft_text), details="A conclusion heading is required."),
        CheckResult(id="citations_resolve", passed=not unknown_citations, details=f"Unknown citekeys: {', '.join(unknown_citations) or 'none'}."),
        CheckResult(id="claims_present", passed=not missing_claims, details=f"Missing active claim text in draft: {', '.join(missing_claims) or 'none'}."),
        CheckResult(id="code_fences_tagged", passed=code_fence_language_failures(draft_text) == 0, details="All fenced code blocks need a language tag."),
        CheckResult(id="latex_balance", passed=latex_failures(draft_text) == 0, details="Inline and display math delimiters must be balanced."),
        CheckResult(id="image_caption_alt", passed=image_caption_failures(draft_text) == 0, details="Images need alt text and a caption line."),
        CheckResult(id="banned_patterns", passed=not banned_hits, details=f"Banned patterns found: {', '.join(banned_hits) or 'none'}."),
        CheckResult(id="em_dash_scan", passed="—" not in draft_text, details="Em dashes are forbidden."),
    ]

    blocker_count = sum(1 for result in results if not result.passed and result.severity == "blocker")
    return CheckSummary(
        target=str(draft_path),
        generated_at=now_iso(),
        results=results,
        blocker_count=blocker_count,
        readability_penalty=readability_penalty(draft_text),
        banned_pattern_count=len(banned_hits),
    )
