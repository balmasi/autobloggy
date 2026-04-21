---
name: autobloggy-prepare
description: Generate or refresh Autobloggy post artifacts from a PPTX or Markdown seed. Use when creating or updating `brief.md`, `outline.md`, `claims.yaml`, `sources.yaml`, or the initial `draft.qmd` for a post slug.
---

# Autobloggy Prepare

Use this skill when working on the staged `prepare` flow for an Autobloggy post.

## Workflow

1. Read `program.md` and the seed file.
2. Ask the user direct briefing questions until you have a usable starting brief.
3. Generate or update `brief.md`.
4. Stop and get explicit user approval before generating `claims.yaml` or the first `draft.qmd`.
5. Generate or update `outline.md`.
6. Generate or update `claims.yaml` and `sources.yaml`.
7. Generate or update the initial `draft.qmd`.

## Rules

- Preserve stable claim IDs when a claim is semantically the same.
- Add new sources only in `prepare` or `refresh-sources`.
- Keep citations in `draft.qmd` in Pandoc form: `[@source-id]`.
- Prefer primary sources; if using a secondary source, say so explicitly.
- Do not generate the first draft until the user has approved the brief.

## File Contracts

- `brief.md`: YAML frontmatter plus short prose about the post, audience, and constraints.
- `outline.md`: one section per heading with a purpose note.
- `claims.yaml`: lean claim registry with stable IDs and last-verification state.
- `sources.yaml`: source registry plus evidence snippets.
- `draft.qmd`: the main editable artifact for the loop.
