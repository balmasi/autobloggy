---
name: autobloggy-prepare
description: Generate or refresh Autobloggy post artifacts from a PPTX or Markdown input. Use when creating or updating `strategy.md`, `outline.md`, or the initial `draft.qmd` for a post slug.
---

# Autobloggy Prepare

Use this skill when working on the staged `prepare` flow for an Autobloggy post.

Read `references/strategy-template.md` before you interview the user or approve a strategy.

This skill covers the staged `prepare` flow only. Once the first `draft.qmd` exists, the caller or orchestrator should continue into the attempt loop rather than stopping at the end of `prepare`.

## Workflow

1. Read `program.md`.
2. Confirm the real topic and canonical user-provided input source with the user before you treat any local file as authoritative.
3. Never infer the intended source from the active file, open tabs, example posts, or anything under `tests/fixtures/` unless the user explicitly tells you to use it.
4. Read the confirmed main input file and any relevant supporting files under `posts/<slug>/inputs/user_provided/`.
5. Ask the user direct strategy questions until you can fill every required item from `references/strategy-template.md`.
6. If you are Claude, prefer `AskUserTool` when it is available. If you are Codex, prefer `request_user_input` when it is available. Otherwise ask directly in chat.
7. Generate or update `strategy.md` with all required sections, including `Target Voice` and `Style Guardrails`.
8. Leave explicit unresolved markers in the strategy if user-specific guidance is still missing.
9. Do not approve the strategy while any required markers or unchecked approval items remain.
10. Stop and get explicit user approval before generating the first `draft.qmd`.
11. Generate or update `outline.md`.
12. Generate or update the initial `draft.qmd`.
13. Hand back to the main Autobloggy loop so it can run `stage-attempt`, edit, verify, evaluate, and repeat.

## Rules

- Do not generate the first draft until the user has approved the strategy.
- Do not generate a strategy until the user has either provided the source material or explicitly approved a topic-only starting point.
- Test fixtures, examples, and previously generated posts are not user input unless the user explicitly says they are.
- Do not treat voice and style as implied. Capture them explicitly in the strategy.
- A strategy is incomplete if it lacks a concrete audience, target voice, style guardrails, or must-cover points.

## File Contracts

- `strategy.md`: YAML frontmatter plus a concrete writing strategy with audience, reader outcome, target voice, style guardrails, must-cover points, must-avoid points, and approval checklist.
- `outline.md`: one section per heading with bullet talking points for human review before draft generation.
- `draft.qmd`: the main editable artifact for the loop.
