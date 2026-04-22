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
| `posts/<slug>/inputs/user_provided/` | Default home for the post brief and supporting files |
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
- Never edit files under `.agents/skills/` or `.claude/skills/` directly.
- Reinstall generated agent copies after skill changes:

```bash
npx skills add ./skills --skill <name> --agent 'claude-code,codex' -y --copy
```

- Use the skill named by `program.md`.

## Invariants

- `program.md` is authoritative for the workflow.
- `posts/<slug>/inputs/user_provided/` is the default input home.
- `strategy.md` is the post-specific source of truth once approved.
- Only attempt candidates under `posts/<slug>/runs/.../draft.qmd` are editable during the loop.
