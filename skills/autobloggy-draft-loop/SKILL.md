---
name: autobloggy-draft-loop
description: Run the Autobloggy attempt loop after the first draft exists.
---

# Autobloggy Draft Loop

Use this skill only when `program.md` reaches the attempt loop.

This skill owns the candidate edit, verify, and evaluate cycle. It does not own kickoff, discovery, outline generation, or strategy approval.

## Loop

1. Read `program.md`, `strategy.md`, `outline.md`, and the active preset files.
2. Run `autobloggy stage-attempt --slug <slug>`.
3. Read `prompt-pack.md` and `next-task.json`.
4. Edit only the candidate `draft.qmd`.
5. Keep changes narrow and aligned to the active task.
6. Run `autobloggy verify --slug <slug> --run-id <run-id> --attempt <attempt-id>`.
7. Evaluate all verdicts concurrently. Each of the 10 verdicts in `verdicts/` is independent (different rubric, different excerpt, no shared state). Read the rubric at `prompt_path`, apply it to `target_excerpt`, and write the result to `verdicts/<verifier>.json` with `status` and `rationale`. Use parallel tool calls, sub-agents, or background jobs — not serial. Do not skip any verdict.
8. Run `autobloggy evaluate --slug <slug> --run-id <run-id> --attempt <attempt-id>`.
9. Repeat until the human stops the run or the draft is no longer improving.

## Escalation

- Use `autobloggy-copy-edit` only when the active task is narrow prose tightening.

## Do Not

- Edit committed `strategy.md`, `outline.md`, or `draft.qmd` inside the loop.
- Invent alternate loop rules outside `program.md`.
