from __future__ import annotations

from .models import EvaluationSummary


def choose_next_task(check_summary: dict, evaluation_summary: EvaluationSummary | None) -> dict:
    failing = [result for result in check_summary["results"] if not result["passed"]]
    if failing:
        primary = failing[0]
        return {
            "priority": "deterministic_blockers",
            "task": primary["id"],
            "reason": primary["details"],
            "batch": [
                {"id": result["id"], "reason": result["details"]}
                for result in failing
            ],
        }

    if evaluation_summary:
        if evaluation_summary.missing_verdicts:
            verifier = evaluation_summary.missing_verdicts[0]
            return {
                "priority": "must_have_verifiers",
                "task": verifier,
                "reason": "Required verifier result is missing or failing.",
                "batch": [{"id": verifier, "reason": "Required verifier result is missing or failing."}],
            }

    return {
        "priority": "hillclimb",
        "task": "specificity",
        "reason": "No blockers remain; tighten specificity and reader value.",
        "batch": [{"id": "specificity", "reason": "No blockers remain; tighten specificity and reader value."}],
    }
