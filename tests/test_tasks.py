from __future__ import annotations

from autobloggy.models import EvaluationSummary
from autobloggy.tasks import choose_next_task


def _summary() -> EvaluationSummary:
    return EvaluationSummary(
        run_id="r",
        attempt_id="a",
        target="draft.qmd",
        blocker_count=0,
        must_have_verifier_fail_count=0,
        improvement_fail_count=0,
        readability_penalty=0,
        banned_pattern_count=0,
        passes_baseline=True,
        acceptance_tuple=(0, 0, 0, 0, 0),
        missing_verdicts=[],
    )


def test_choose_next_task_batches_all_failing_deterministic_blockers() -> None:
    check_summary = {
        "results": [
            {"id": "one_h1", "passed": True, "details": "ok"},
            {"id": "heading_order", "passed": False, "details": "bad headings"},
            {"id": "intro_exists", "passed": False, "details": "missing intro"},
            {"id": "em_dash_scan", "passed": False, "details": "em dash found"},
        ]
    }
    task = choose_next_task(check_summary, _summary())
    assert task["priority"] == "deterministic_blockers"
    assert task["task"] == "heading_order"
    assert [item["id"] for item in task["batch"]] == ["heading_order", "intro_exists", "em_dash_scan"]


def test_choose_next_task_falls_through_to_missing_verifier() -> None:
    check_summary = {"results": [{"id": "one_h1", "passed": True, "details": "ok"}]}
    summary = _summary()
    summary.missing_verdicts = ["paragraph_focus", "voice"]
    task = choose_next_task(check_summary, summary)
    assert task["priority"] == "must_have_verifiers"
    assert task["task"] == "paragraph_focus"
    assert [item["id"] for item in task["batch"]] == ["paragraph_focus"]


def test_choose_next_task_hillclimb_when_nothing_failing() -> None:
    check_summary = {"results": [{"id": "one_h1", "passed": True, "details": "ok"}]}
    task = choose_next_task(check_summary, _summary())
    assert task["priority"] == "hillclimb"
    assert task["task"] == "specificity"
    assert task["batch"] == [{"id": "specificity", "reason": task["reason"]}]
