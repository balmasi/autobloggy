from __future__ import annotations

import math
import re
from pathlib import Path

from readability import Readability
from readability.exceptions import ReadabilityException
import yaml

from .artifacts import extract_frontmatter, read_text
from .models import CheckResult, CheckSummary
from .utils import now_iso, paragraphs, repo_root, words


def load_banned_patterns() -> list[str]:
    root = repo_root()
    raw = yaml.safe_load((root / "shared" / "banned_patterns.yaml").read_text(encoding="utf-8")) or {}
    return list(raw.get("patterns", []))


def load_readability_config() -> tuple[float, float]:
    root = repo_root()
    raw = yaml.safe_load((root / "config.yaml").read_text(encoding="utf-8")) or {}
    readability = raw.get("readability") or {}
    return (
        float(readability.get("target_flesch_kincaid_grade_level", 10)),
        float(readability.get("allowed_grade_level_deviation", 1)),
    )


def normalize_readability_sample(text: str, minimum_words: int = 100) -> str:
    sample = text.strip()
    word_count = len(words(sample))
    if word_count == 0 or word_count >= minimum_words:
        return sample

    # Repeating the same sample preserves the underlying readability ratios.
    repeats = math.ceil(minimum_words / word_count)
    return "\n".join(sample for _ in range(repeats))


def flesch_kincaid_grade_level(text: str) -> float | None:
    sample = normalize_readability_sample(text)
    if not sample:
        return None

    try:
        return Readability(sample).flesch_kincaid().score
    except ReadabilityException:
        return None


def readability_penalty(text: str) -> int:
    target_grade_level, allowed_deviation = load_readability_config()
    grade_level = flesch_kincaid_grade_level(text)
    if grade_level is None:
        return math.ceil(target_grade_level)

    deviation = abs(grade_level - target_grade_level) - allowed_deviation
    return max(0, math.ceil(deviation))


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
    in_fence = False
    for line in text.splitlines():
        if not line.startswith("```"):
            continue
        if in_fence:
            in_fence = False
        else:
            in_fence = True
            if line.strip() == "```":
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
    if re.search(r"^##\s+(Conclusion|Takeaways?|Closing)\b", text, flags=re.MULTILINE | re.IGNORECASE):
        return True

    sections = re.findall(r"^##\s+(.+)$", text, flags=re.MULTILINE)
    if len(sections) < 3:
        return False

    matches = list(re.finditer(r"^##\s+.+$", text, flags=re.MULTILINE))
    if not matches:
        return False
    last_heading = matches[-1]
    trailing_body = text[last_heading.end() :].strip()
    return len(words(trailing_body)) >= 20


def generic_heading_labels(text: str) -> list[str]:
    labels: list[str] = []
    generic_labels = {
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
        "drafting notes",
        "notes for drafting",
    }
    for match in re.finditer(r"^##\s+(.+)$", text, flags=re.MULTILINE):
        heading = match.group(1).strip()
        lowered = heading.casefold()
        if lowered in generic_labels or lowered.startswith("body section "):
            labels.append(heading)
    return labels


def valid_heading_order(text: str) -> bool:
    levels = [len(match.group(1)) for match in re.finditer(r"^(#+)\s+.+$", text, flags=re.MULTILINE)]
    if not levels:
        return False
    return all(next_level - current_level <= 1 for current_level, next_level in zip(levels, levels[1:]))


def run_checks(draft_path: Path) -> CheckSummary:
    draft_text = read_text(draft_path)
    _, draft_body = extract_frontmatter(draft_text)
    if draft_body:
        draft_text = draft_body
    banned = load_banned_patterns()

    h1_count = len(re.findall(r"^#\s+.+$", draft_text, flags=re.MULTILINE))
    banned_hits = [pattern for pattern in banned if pattern.lower() in draft_text.lower()]
    generic_headings = generic_heading_labels(draft_text)

    results = [
        CheckResult(id="one_h1", passed=h1_count == 1, details=f"Found {h1_count} H1 headings."),
        CheckResult(id="heading_order", passed=valid_heading_order(draft_text), details="Heading levels must not jump by more than one."),
        CheckResult(
            id="presentable_headings",
            passed=not generic_headings,
            details="Replace outline-style section headings with publishable, reader-facing titles. "
            f"Found: {', '.join(generic_headings) or 'none'}.",
        ),
        CheckResult(id="intro_exists", passed=paragraph_intro_exists(draft_text), details="Intro paragraph must exist before deeper sections."),
        CheckResult(id="conclusion_exists", passed=conclusion_exists(draft_text), details="A conclusion heading is required."),
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
