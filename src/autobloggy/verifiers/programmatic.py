from __future__ import annotations

import re
from typing import Callable

from bs4 import BeautifulSoup, Comment, NavigableString, Tag


CheckFn = Callable[[str], tuple[str, list[str]]]
CHECKS: list[CheckFn] = []

FB_MARKER_PATTERN = re.compile(r"<!--\s*fb\[([^\]]+)\][\s\S]*?-->")


def check(fn: CheckFn) -> CheckFn:
    CHECKS.append(fn)
    return fn


def _load_html(html: str) -> tuple[BeautifulSoup, Tag | None]:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    return soup, main


def _serialize(soup: BeautifulSoup) -> str:
    return str(soup)


def _make_marker(soup: BeautifulSoup, rule_id: str, rationale: str) -> Comment:
    safe_rationale = (
        rationale.replace("\n", " ")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("-->", "--&gt;")
        .strip()
    )
    return Comment(f" fb[{rule_id}]: {safe_rationale} ")


def _insert_after(node: Tag | NavigableString, comment: Comment) -> None:
    node.insert_after(comment)



@check
def one_h1(html: str) -> tuple[str, list[str]]:
    soup, main = _load_html(html)
    if main is None:
        return html, []
    h1s = main.find_all("h1")
    if len(h1s) <= 1:
        return html, []
    inserted: list[str] = []
    for extra in h1s[1:]:
        marker = _make_marker(soup, "one_h1", "more than one H1 in <main>; demote to H2 or remove")
        extra.insert(0, marker)
        inserted.append("one_h1")
    return _serialize(soup), inserted


@check
def heading_order(html: str) -> tuple[str, list[str]]:
    soup, main = _load_html(html)
    if main is None:
        return html, []
    headings = main.find_all(re.compile(r"^h[1-6]$"))
    inserted: list[str] = []
    prev_level = 0
    for heading in headings:
        level = int(heading.name[1])
        if prev_level and level - prev_level > 1:
            marker = _make_marker(
                soup,
                "heading_order",
                f"heading level jumps from H{prev_level} to H{level}; insert intermediate level",
            )
            heading.insert(0, marker)
            inserted.append("heading_order")
        prev_level = level
    return (_serialize(soup), inserted) if inserted else (html, [])


@check
def code_fences_tagged(html: str) -> tuple[str, list[str]]:
    soup, main = _load_html(html)
    if main is None:
        return html, []
    inserted: list[str] = []
    for code in main.select("pre code"):
        classes = code.get("class") or []
        if not any(cls.startswith("language-") for cls in classes):
            marker = _make_marker(soup, "code_fences_tagged", "code block missing language class (e.g. language-python)")
            code.insert(0, marker)
            inserted.append("code_fences_tagged")
    return (_serialize(soup), inserted) if inserted else (html, [])


@check
def image_caption_alt(html: str) -> tuple[str, list[str]]:
    soup, main = _load_html(html)
    if main is None:
        return html, []
    inserted: list[str] = []
    for img in main.find_all("img"):
        alt = img.get("alt")
        if not alt or not str(alt).strip():
            marker = _make_marker(soup, "image_caption_alt", "img missing meaningful alt text")
            _insert_after(img, marker)
            inserted.append("image_caption_alt")
    for figure in main.find_all("figure"):
        if not figure.find("figcaption"):
            marker = _make_marker(soup, "image_caption_alt", "figure missing figcaption")
            _insert_after(figure, marker)
            inserted.append("image_caption_alt")
    return (_serialize(soup), inserted) if inserted else (html, [])

