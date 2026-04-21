from __future__ import annotations

from .models import EvaluationSummary


def is_strict_improvement(candidate: EvaluationSummary, current: EvaluationSummary | None) -> bool:
    if current is None:
        return True

    if not current.passes_baseline:
        return candidate.acceptance_tuple < current.acceptance_tuple

    if not candidate.passes_baseline:
        return False

    return candidate.acceptance_tuple < current.acceptance_tuple

