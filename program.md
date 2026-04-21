# Autobloggy Program

## Editable Surface

- The autonomous edit loop may edit only `draft.qmd` and `claims.yaml` inside the active candidate workspace.
- `program.md`, `config.yaml`, `brief.md`, `outline.md`, `sources.yaml`, and everything under `shared/` are fixed during a run.
- New sources may be added only through `prepare` or `refresh-sources`.

## Brief Gate

- A human must review and approve `brief.md` before `claims.yaml` or the first `draft.qmd` are generated.
- Do not start the first draft until the user has confirmed the brief.
- `brief.md` is not approval-ready unless it includes concrete guidance for audience, reader outcome, target voice, style guardrails, must-cover points, must-avoid points, and evidence standards.
- Defaults are allowed as a starting point, but unresolved required markers must be cleared before approval.

## Orchestrator Contract

- After the brief is approved and the first `draft.qmd` exists, the orchestrator should continue directly into the attempt loop unless the operator explicitly pauses or stops the run.
- Do not treat initial draft generation as the end of the workflow. It is the handoff point into `stage-attempt`, not the stopping point.
- The orchestrator owns the full loop: `stage-attempt`, edit the candidate workspace, `verify`, fill verifier verdict JSON files, `evaluate`, then repeat while improvements are still being made and runtime allows.
- `verify` is evidence collection and verdict preparation. `evaluate` is the keep-or-revert gate.
- Missing verdict files are loop work to complete, not a reason to stop and wait for a human unless the operator explicitly wants manual review.
- During a run, edit only `draft.qmd` and `claims.yaml` inside the active attempt workspace. Do not edit committed `posts/<slug>/` artifacts directly except through `prepare`, `refresh-sources`, or `evaluate` copying back a kept attempt.

## Default Loop Order

1. Clear deterministic blockers.
2. Clear must-have verifier failures.
3. Resolve claim issues.
4. Hillclimb readability, specificity, and reader value.

## Acceptance Rule

- Before baseline: keep only changes that strictly improve the acceptance tuple.
- After baseline: keep only changes that preserve all must-haves and strictly
  improve the acceptance tuple.
- Ties revert.

## House Style

- Write directly and concretely.
- State the problem or conclusion early.
- Keep paragraphs narrow; each paragraph should carry one main idea.
- Prefer primary sources and explicit evidence.
- Use citekeys in `draft.qmd` as `[@source-id]`.

## Never Do

- Do not invent evidence.
- Do not use hype, empty intensifiers, or generic assistant phrasing.
- Do not use em dashes.
- Do not overstate capability or certainty.
