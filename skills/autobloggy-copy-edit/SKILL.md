---
name: autobloggy-copy-edit
description: Tighten Autobloggy draft prose without changing the post thesis. Use when improving `draft.qmd` for clarity, specificity, reader value, anti-hype, and anti-AI-cleanup while respecting the repo's style rules.
---

# Autobloggy Copy Edit

Use this skill only for late-stage draft improvement after the structure is already mostly sound.

`program.md` or `autobloggy-draft-loop` should invoke this skill only when the active task is narrow prose tightening.

## Goals

- State the point early.
- Keep each paragraph on one idea.
- Replace vague verbs with concrete detail.
- Remove hype, filler transitions, em dashes, and generic assistant phrasing.

## Workflow

1. Read `program.md`, the current `strategy.md`, and the current `draft.qmd`.
2. If the strategy frontmatter records preset files, read the active preset's `writing_guide.md` and `brand_guide.md` before editing.
3. Treat the preset guides and strategy as read-only context. The draft is the only editable artifact in the loop.
4. Identify the smallest scope that improves the active task.
5. Edit only `draft.qmd`.

## Anti-AI Cleanup

- Remove phrases that sound canned, managerial, or inflated.
- Cut empty intensifiers.
- Prefer direct nouns and verbs over abstractions.
- Keep prose plain enough that a verifier can point to concrete draft language easily.

## Do Not

- Change the thesis of the post.
- Add new unsupported assertions.
- Edit `program.md`, preset files, `strategy.md`, or `outline.md`.
