# Autobloggy

A writing harness that turns a topic and source material into an approved `blog_brief.md`, then a publishable HTML draft refined through a verify/fix loop.

The agent drives the workflow. You answer a few questions, review the brief, and approve.

## Install

```bash
./scripts/install.sh
```

Installs Python deps, the Playwright Chromium browser used during verification, and agent skill copies.

## Usage

Ask the agent in plain English:

```text
Let's write a [guide|blog] post about [topic] using the [fast|guided|expert] intake.
```

To include source material, drop files into a folder and mention them, or pass paths — the agent will copy them into `posts/<slug>/inputs/raw/` and prepare normalized versions alongside.

From there the agent will:

1. Run prep and draft `blog_brief.md`
2. Hand it to you to review (angle, outline, evidence, required points, things to avoid, visual plan)
3. On your approval, generate the draft scaffold and write the first draft into `posts/<slug>/draft.html`
4. Run the verify/fix loop until no automated or manually inserted feedback  `<!-- fb[...] -->` markers remain (guided from the `quality_criteria.md` file)
5. Finish with a `slop-mop` pass to remove generic AI-sounding prose

You add image/chart requests directly to `blog_brief.md` before approving — the first-draft step authors them inline.

## Intake Depths

How much the agent asks before drafting:

- **fast** — agent fills the brief from topic and sources. Discovery skipped.
- **guided** — you answer the strategic questions, agent fills the rest.
- **expert** — you drive most substantive decisions.

`guided` and `expert` need `--select audience=...` and `--select format=...` (the agent will ask).

## Presets

A preset is a reusable editorial pack — brand voice, writing rules, HTML template, audience, and format options. The default preset supports:

- `audience`: `general`, `practitioner`, `decision-maker`
- `format`: `blog`, `guide`

Make a new one:

```bash
uv run autobloggy new-preset --name acme
```

Defaults (preset, intake depth, brief sections, verify viewport widths) live in `config.yaml`.

## Where Things Live

| Path | Purpose |
|------|---------|
| `posts/<slug>/blog_brief.md` | The one pre-draft approval artifact |
| `posts/<slug>/draft.html` | Working draft; loop edits happen inside `<main>` |
| `posts/<slug>/inputs/raw/` | Your original source files (only put originals here) |
| `posts/<slug>/inputs/prepared/` | Normalized LLM-readable copies (system-owned) |
| `posts/<slug>/meta.yaml` | Pipeline state |
| `presets/<name>/` | Editorial packs |
| `program.md` | Authoritative workflow for agents |

## CLI

Mostly run by the agent, but available to you:

- `prep` — scaffold a post, ingest sources, draft `blog_brief.md`
- `approve-brief` — validate the brief and mark it approved
- `generate-draft` — materialize `draft.html` from the template
- `verify` — run programmatic checks and capture screenshots into `.verify/`
- `new-preset` — copy `presets/default/` to a new preset folder

`uv run autobloggy --help` for flags.
