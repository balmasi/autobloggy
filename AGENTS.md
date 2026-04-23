## Goal

Help an operator turn a topic and source material into a publishable blog post through deterministic CLI stages plus a narrow set of named skills.

When the user asks to write a post or continue any Autobloggy stage, read `program.md` first. `program.md` is the workflow authority.

## Business Context

- This repo optimizes for simple kickoff UX.
- Deterministic code should own stage transitions, path defaults, preset scaffolding, and approval gates.
- The agent layer should focus on conversation, review help, and dispatching the skill named by `program.md`.

## Command Overview

```bash
uv sync
uv run pytest
uv run pytest -v -k name
uv run autobloggy --help
uv run autobloggy new-post --topic "Why AI eval loops fail"
uv run autobloggy new-preset --name acme
uv run autobloggy decide-discovery --slug my-post --decision no
uv run autobloggy generate-outline --slug my-post
uv run autobloggy generate-draft --slug my-post
uv run autobloggy approve-strategy --slug my-post
uv run autobloggy approve-outline --slug my-post
uv run autobloggy stage-attempt --slug my-post
uv run autobloggy stage-attempt --slug my-post --run-id <run-id>
uv run autobloggy stage-attempt --slug my-post --new-run
```

## File Layout

| Path | Purpose |
|------|---------|
| `program.md` | Canonical workflow, gates, and named skill invocations |
| `posts/<slug>/inputs/user_provided/` | Human-owned brief plus raw source files |
| `posts/<slug>/inputs/extracted/` | Deterministic text and visual extracts |
| `posts/<slug>/inputs/prepared/` | Canonical LLM-facing input bundle and manifest |
| `posts/<slug>/` | Per-post artifacts (`strategy.md`, `outline.md`, `draft.qmd`) |
| `presets/<name>/` | Editorial packs (`strategy_template.md`, `writing_guide.md`, `brand_guide.md`) |
| `config.yaml` | Repo-level config including `prepare.default_preset` |
| `skills/` | Source skill definitions |
| `shared/` | Shared deterministic checks |

## Core Modules

| File | Role |
|------|------|
| `cli.py` | Stage-based CLI entrypoint |
| `prepare.py` | Input bundle setup, preset scaffolding, and artifact generation |
| `loop.py` | Run state, attempt creation, prompt packs, evaluation |
| `checks.py` | Deterministic validation plus readability |
| `verifiers.py` | Verifier request bundles |
| `presets.py` | Repo config loading and preset resolution |

## Skills

- Edit only `skills/` source files.
- Reinstall generated agent symlinks after skill changes:

```bash
npx skills add ./skills --skill <name> -y --agent claude-code codex
```

- Use the skill named by `program.md`.

## Rules
Keeping the orchestrator (main agent) context window minimal is critical.
- When doing work that can be done in parallel use parallel subagents
- When doing work that is independent you can use a general purpose subagent with a clean context and wait for the results

## Invariants

- `program.md` is authoritative for the workflow.
- `posts/<slug>/inputs/user_provided/brief.md` is the only conversational brief file.
- `posts/<slug>/inputs/user_provided/raw/` is the only home for human-dropped source files.
- `posts/<slug>/inputs/extracted/` and `posts/<slug>/inputs/prepared/` are deterministic outputs only.
- `strategy.md` is the post-specific source of truth once approved.
- Only attempt candidates under `posts/<slug>/runs/.../draft.qmd` are editable during the loop.
- Never edit files under `.agents/skills/` or `.claude/skills/` directly.
