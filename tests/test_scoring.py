from __future__ import annotations

from autobloggy.models import EvaluationSummary
from autobloggy.scoring import is_strict_improvement


def make_summary(tup: tuple[int, int, int, int, int, int], baseline: bool) -> EvaluationSummary:
    return EvaluationSummary(
        run_id="run-001",
        attempt_id="attempt-001",
        target="draft.qmd",
        blocker_count=tup[0],
        must_have_verifier_fail_count=tup[1],
        claim_issue_count=tup[2],
        improvement_fail_count=tup[3],
        readability_penalty=tup[4],
        banned_pattern_count=tup[5],
        passes_baseline=baseline,
        acceptance_tuple=tup,
        missing_verdicts=[],
    )


def test_strict_improvement_compares_acceptance_tuple() -> None:
    current = make_summary((2, 3, 1, 2, 1, 0), False)
    candidate = make_summary((1, 3, 1, 2, 1, 0), False)
    assert is_strict_improvement(candidate, current)


def test_baseline_rejects_regression() -> None:
    current = make_summary((0, 0, 0, 2, 1, 0), True)
    candidate = make_summary((0, 1, 0, 1, 1, 0), False)
    assert not is_strict_improvement(candidate, current)

