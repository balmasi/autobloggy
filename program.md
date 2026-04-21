# Autobloggy Program

## Editable Surface

- The autonomous edit loop may edit only `draft.qmd` inside the active candidate workspace.
- `program.md`, `config.yaml`, `strategy.md`, `outline.md`, and everything under `shared/` are fixed during a run.

## Strategy Gate

- Before generating `strategy.md`, confirm the actual user-provided topic and canonical input source.
- Do not infer the live input from open tabs, active files, examples, sample posts, or test fixtures.
- Treat files under `tests/fixtures/`, example content, and existing posts as non-authoritative unless the user explicitly says to use them.
- A human must review and approve `strategy.md` before the first `draft.qmd` is generated.
- Do not start the first draft until the user has confirmed the strategy.
- `strategy.md` is not approval-ready unless it includes concrete guidance for audience, reader outcome, target voice, style guardrails, must-cover points, and must-avoid points.
- Defaults are allowed as a starting point, but unresolved required markers must be cleared before approval.

## Orchestrator Contract

- After the strategy is approved and the first `draft.qmd` exists, the orchestrator should continue directly into the attempt loop unless the operator explicitly pauses or stops the run.
- Do not treat initial draft generation as the end of the workflow. It is the handoff point into `stage-attempt`, not the stopping point.
- The orchestrator owns the full loop: `stage-attempt`, edit the candidate workspace, `verify`, fill verifier verdict JSON files, `evaluate`, then repeat while improvements are still being made and runtime allows.
- `verify` is verifier bundle preparation. `evaluate` is the keep-or-revert gate.
- Missing verdict files are loop work to complete, not a reason to stop and wait for a human unless the operator explicitly wants manual review.
- During a run, edit only `draft.qmd` inside the active attempt workspace. Do not edit committed `posts/<slug>/` artifacts directly except through `prepare` or `evaluate` copying back a kept attempt.

## Default Loop Order

1. Clear deterministic blockers.
2. Clear must-have verifier failures.
3. Hillclimb readability, specificity, and reader value.

## Acceptance Rule

- Before baseline: keep only changes that strictly improve the acceptance tuple.
- After baseline: keep only changes that preserve all must-haves and strictly
  improve the acceptance tuple.
- Ties revert.

## House Style

- Write directly and concretely.
- State the problem or conclusion early.
- Keep paragraphs narrow; each paragraph should carry one main idea.

## Never Do

- Do not use hype, empty intensifiers, or generic assistant phrasing.
- Do not use em dashes.
- Do not overstate capability or certainty.
