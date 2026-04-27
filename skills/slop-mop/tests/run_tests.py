#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
DETECTOR = ROOT / "scripts" / "detect_slop.py"


def load_detector():
    spec = importlib.util.spec_from_file_location("detect_slop", DETECTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load detector: {DETECTOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def assert_rules(findings, expected: set[str]) -> None:
    actual = {finding.rule for finding in findings}
    missing = expected - actual
    if missing:
        raise AssertionError(f"missing rules {sorted(missing)}; saw {sorted(actual)}")


def test_sloppy_markdown(detector) -> None:
    text = (FIXTURES / "sloppy_article.md").read_text(encoding="utf-8")
    findings = detector.detect(text)
    assert_rules(
        findings,
        {
            "we_will_explore",
            "inflated_modifier",
            "generic_vocabulary",
            "not_just_but",
            "when_it_comes_to",
            "important_to_note",
            "no_discussion_complete",
            "vague_authority",
            "superficial_analysis",
            "false_range",
            "conclusion_boilerplate",
            "grand_metaphor_vocabulary",
            "ai_response_leak",
        },
    )


def test_clean_markdown(detector) -> None:
    text = (FIXTURES / "clean_article.md").read_text(encoding="utf-8")
    findings = detector.detect(text)
    if findings:
        raise AssertionError(f"expected no findings; saw {findings}")


def test_html_ignores_code(detector) -> None:
    path = FIXTURES / "sloppy_article.html"
    text = detector.visible_text(path.read_text(encoding="utf-8"), path)
    findings = detector.detect(text)
    assert_rules(findings, {"this_piece_will", "inflated_modifier", "generic_vocabulary"})
    matches = {finding.match for finding in findings}
    if any("revolutionary" in match for match in matches):
        raise AssertionError("detector should ignore slop-like words inside code blocks")


def test_literal_patterns_use_wordish_boundaries(detector) -> None:
    findings = detector.detect("This overallocation is not a conclusion.")
    if findings:
        raise AssertionError(f"expected literal pattern not to match inside words; saw {findings}")


def main() -> int:
    detector = load_detector()
    tests = [
        test_sloppy_markdown,
        test_clean_markdown,
        test_html_ignores_code,
        test_literal_patterns_use_wordish_boundaries,
    ]
    for test in tests:
        test(detector)
        print(f"ok {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
