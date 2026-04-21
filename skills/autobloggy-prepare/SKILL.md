---
name: autobloggy-prepare
description: Generate or refresh Autobloggy post artifacts from a PPTX or Markdown seed. Use when creating or updating `brief.md`, `outline.md`, `claims.yaml`, `sources.yaml`, or the initial `draft.qmd` for a post slug.
---

# Autobloggy Prepare

Use this skill when working on the staged `prepare` flow for an Autobloggy post.

Read `references/brief-template.md` before you interview the user or approve a brief.

## Workflow

1. Read `program.md` and the seed file.
2. Ask the user direct briefing questions until you can fill every required item from `references/brief-template.md`.
3. If you are Claude, prefer `AskUserTool` when it is available. If you are Codex, prefer `request_user_input` when it is available. Otherwise ask directly in chat.
4. Generate or update `brief.md` with all required sections, including `Target Voice` and `Style Guardrails`.
5. Leave explicit unresolved markers in the brief if user-specific guidance is still missing.
6. Do not approve the brief while any required markers or unchecked approval items remain.
7. Stop and get explicit user approval before generating `claims.yaml` or the first `draft.qmd`.
8. Generate or update `outline.md`.
9. Generate or update `claims.yaml` and `sources.yaml`.
10. Generate or update the initial `draft.qmd`.

## Rules

- Preserve stable claim IDs when a claim is semantically the same.
- Add new sources only in `prepare` or `refresh-sources`.
- Keep citations in `draft.qmd` in Pandoc form: `[@source-id]`.
- Prefer primary sources; if using a secondary source, say so explicitly.
- Do not generate the first draft until the user has approved the brief.
- Do not treat voice and style as implied. Capture them explicitly in the brief.
- A brief is incomplete if it lacks a concrete audience, target voice, style guardrails, must-cover points, or evidence expectations.

## File Contracts

- `brief.md`: YAML frontmatter plus a concrete writing brief with audience, reader outcome, target voice, style guardrails, must-cover points, must-avoid points, evidence standards, and approval checklist.
- `outline.md`: one section per heading with a purpose note.
- `claims.yaml`: lean claim registry with stable IDs and last-verification state.
- `sources.yaml`: source registry plus evidence snippets.
- `draft.qmd`: the main editable artifact for the loop.
