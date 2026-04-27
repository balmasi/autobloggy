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
uv run autobloggy prepare-inputs --slug my-post
uv run autobloggy generate-strategy --slug my-post
uv run autobloggy decide-discovery --slug my-post --decision no
uv run autobloggy generate-outline --slug my-post
uv run autobloggy approve-outline --slug my-post
uv run autobloggy generate-draft --slug my-post
uv run autobloggy verify --slug my-post
uv run autobloggy export --slug my-post
```

## File Layout

| Path | Purpose |
|------|---------|
| `program.md` | Canonical workflow, gates, and named skill invocations |
| `posts/<slug>/inputs/user_provided/` | Human-owned brief plus raw source files |
| `posts/<slug>/inputs/prepared/` | Canonical LLM-facing input bundle and manifest |
| `posts/<slug>/` | Per-post artifacts (`meta.yaml`, `strategy.md`, `outline.md`, `draft.html`) |
| `posts/<slug>/.verify/` | Transient per-iteration verify pack and screenshots (gitignored) |
| `presets/<name>/` | Editorial packs (`strategy_template.md`, `writing_guide.md`, `brand_guide.md`, `template.html`) |
| `prompts/verifier_rubrics.md` | Single source of truth for what "good" looks like; shipped to writer and verifier |
| `config.yaml` | Repo-level config including `prepare.default_preset` |
| `skills/` | Source skill definitions |
| `shared/` | Shared deterministic checks |

## Core Modules

| File | Role |
|------|------|
| `cli.py` | Stage-based CLI entrypoint |
| `prepare.py` | Input bundle setup, preset scaffolding, and artifact generation |
| `verify.py` | The `autobloggy verify` command (programmatic markers + Playwright screenshots + verify-pack) |
| `verifiers/programmatic.py` | `@check`-decorated programmatic checks that insert `<!-- fb[...] -->` markers in `<main>` |
| `presets.py` | Repo config loading and preset resolution |
| `artifacts.py` | Post paths and `meta.yaml` read/write |

## Skills

`skills-lock.json` is the source of truth. `.agents/skills/` and `.claude/skills/` are generated outputs — gitignored, never edited directly, and always reproducible from the lockfile.

**Restore (fresh clone or after any skill change):**
```bash
npx skills experimental_install -y
# or: ./scripts/install.sh  (also runs uv sync + playwright install)
```

**Add a local skill** — create `skills/<name>/SKILL.md`, then:
```bash
npx skills add ./skills --skill <name> -y
```

**Add a GitHub skill:**
```bash
npx skills add <owner/repo> -y
```

**Remove a skill:**
```bash
npx skills remove <name> --all -y
# if local: also delete skills/<name>/
```

Both `add` and `remove` update `skills-lock.json` automatically. An orphaned skill (installed but not in the lockfile, or in the lockfile but not in `skills/`) is structurally impossible as long as you use the CLI.

- Use the skill named by `program.md`.

## Rules

Keeping the orchestrator (main agent) context window minimal is critical.
- When doing work that can be done in parallel use parallel subagents.
- When doing work that is independent you can use a general purpose subagent with a clean context and wait for the results.

## Simplicity

All else being equal, simpler is better. This repo has a clear seam between deterministic CLI stages and the agent layer — complexity in either direction erodes that clarity.

- A small improvement that adds hacky code or blurs the deterministic/agent boundary is not worth it.
- Deleting code and getting equal or better results is a win.
- An improvement of ~0 but simpler code? Keep it.

When evaluating a change, weigh the complexity cost against the improvement magnitude. Prefer fewer CLI flags, fewer prompt-pack fields, and fewer skill steps over marginal quality gains.

## Invariants

- `program.md` is authoritative for the workflow.
- `posts/<slug>/inputs/user_provided/brief.md` is the only conversational brief file.
- `posts/<slug>/inputs/user_provided/raw/` is the only home for human-dropped source files.
- `posts/<slug>/inputs/prepared/` is a deterministic output only.
- `posts/<slug>/meta.yaml` is the only home for pipeline state (status, preset, discovery decision, timestamps).
- `strategy.md` is the post-specific source of truth once the human signs off.
- Only `posts/<slug>/draft.html` (inside `<main>`) is editable during the verify loop.
- Verifier feedback flows through `<!-- fb[rule_id]: rationale -->` HTML comments inside `<main>`. Empty-check is `grep -c '<!-- fb\[' draft.html` returning `0`.
