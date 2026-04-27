from __future__ import annotations

import re

from .programmatic import CHECKS, FB_MARKER_PATTERN

__all__ = ["CHECKS", "FB_MARKER_PATTERN", "strip_markers", "run_programmatic", "marker_summary"]


def strip_markers(html: str) -> str:
    """Remove every `<!-- fb[...] -->` comment from the HTML."""
    return FB_MARKER_PATTERN.sub("", html)


def run_programmatic(html: str) -> tuple[str, list[str]]:
    """Run every registered programmatic check. Returns (html_with_markers, rule_ids_inserted)."""
    inserted: list[str] = []
    for check in CHECKS:
        new_html, rule_ids = check(html)
        html = new_html
        inserted.extend(rule_ids)
    return html, inserted


def marker_summary(html: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for match in FB_MARKER_PATTERN.finditer(html):
        rule_id = match.group(1)
        counts[rule_id] = counts.get(rule_id, 0) + 1
    return counts


def marker_count(html: str) -> int:
    return len(FB_MARKER_PATTERN.findall(html))
