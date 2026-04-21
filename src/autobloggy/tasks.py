from __future__ import annotations

from .models import EvaluationSummary


def choose_next_task(check_summary: dict, evaluation_summary: EvaluationSummary | None) -> dict:
    for result in check_summary["results"]:
        if not result["passed"]:
            return {
                "priority": "deterministic_blockers",
                "task": result["id"],
                "reason": result["details"],
            }

    if evaluation_summary:
        if evaluation_summary.missing_verdicts:
            return {
                "priority": "must_have_verifiers",
                "task": evaluation_summary.missing_verdicts[0],
                "reason": "Required verifier result is missing or failing.",
            }

    return {
        "priority": "hillclimb",
        "task": "specificity",
        "reason": "No blockers remain; tighten specificity and reader value.",
    }
