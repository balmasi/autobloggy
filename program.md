# Autobloggy Program

## Editable Surface

- The autonomous edit loop may edit only `draft.qmd` and `claims.yaml` inside the active candidate workspace.
- `program.md`, `config.yaml`, `brief.md`, `outline.md`, `sources.yaml`, and everything under `shared/` are fixed during a run.
- New sources may be added only through `prepare` or `refresh-sources`.

## Brief Gate

- A human must review and approve `brief.md` before `claims.yaml` or the first `draft.qmd` are generated.
- Do not start the first draft until the user has confirmed the brief.

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
