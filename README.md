# Autobloggy

Autobloggy is a writing harness for turning a post brief and source material into a strategy, reviewed outline, and a publishable HTML draft refined through a two-pass verify/fix loop.

`program.md` is the authoritative workflow document. Read it first.

## Install

```bash
./scripts/install.sh
```

Runs `uv sync`, installs the Playwright Chromium browser (used by `autobloggy verify` for full-page screenshots), and reinstalls agent skill copies into `.agents/skills/` and `.claude/skills/`.

If you only want a piece of it:

- `uv sync` — Python deps
- `uv run playwright install chromium` — verify-loop screenshots
- `npx skills add ./skills --agent claude-code codex` — agent skill copies

## Quick Start

1. `./scripts/install.sh`
2. Start a new post: `uv run autobloggy new-post --topic "Why AI eval loops fail"` (or pass `--source <path>` for files; or pre-place files under `posts/<slug>/inputs/user_provided/raw/` and run `--slug <slug>`)
3. If raw files change later: `uv run autobloggy prepare-inputs --slug <slug>`
4. `uv run autobloggy generate-strategy --slug <slug>` then review `posts/<slug>/strategy.md`
5. `uv run autobloggy decide-discovery --slug <slug> --decision yes|no`
6. If `yes`, run discovery before generating the outline
7. `uv run autobloggy generate-outline --slug <slug>` and rewrite the outline with publishable headings
8. `uv run autobloggy approve-outline --slug <slug>`
9. `uv run autobloggy generate-draft --slug <slug>` to scaffold `draft.html` from the preset's `template.html`
10. Use skill `autobloggy-first-draft` to fill `<main>` with prose AND inline visuals
11. Verify loop:
    - `uv run autobloggy verify --slug <slug>` (strips old markers, runs programmatic checks, captures screenshots, writes `.verify/verify-pack.md`)
    - dispatch the `autobloggy-verifier` sub-agent on the pack to insert LLM-judged markers
    - fix every `<!-- fb[rule_id]: rationale -->` marker — the same fix pass authors / edits inline visuals when `fb[needs_visual]` or visual rule markers are present
    - re-run until `marker_count == 0`
12. `uv run autobloggy export --slug <slug>` copies the final draft to `posts/<slug>/export/html/`

## Commands

- `new-post`: scaffolds the input layout, writes `meta.yaml` and `brief.md`, copies any `--source` files into `inputs/user_provided/raw/`
- `new-preset`: scaffolds a new preset from `presets/default/` (includes `template.html`)
- `prepare-inputs`: builds the canonical bundle at `inputs/prepared/input.md` plus `input_manifest.yaml`
- `generate-strategy`: applies the active preset's strategy template to the prepared inputs
- `decide-discovery`: records the operator's explicit `yes` or `no` discovery decision in `meta.yaml`
- `generate-outline`: writes a stub outline at `outline.md` after the strategy is reviewed and the discovery decision is recorded
- `approve-outline`: flips `meta.yaml` `status` to `outline_approved` once the outline has publishable headings
- `generate-draft`: materializes `draft.html` from the active preset's `template.html`
- `verify`: strips existing `<!-- fb[...] -->` markers from `draft.html`, runs programmatic checks (inserting markers), captures full-page screenshots at 360/768/1280, and writes `.verify/verify-pack.md` for the verifier sub-agent
- `export`: copies `draft.html` to `posts/<slug>/export/html/`

## Core Concepts

- `program.md`: canonical workflow, boundaries, and named skill invocations
- `posts/<slug>/meta.yaml`: pipeline state (status, preset, discovery decision, timestamps)
- `posts/<slug>/inputs/user_provided/`: human-owned brief and raw source files
- `posts/<slug>/inputs/prepared/`: canonical LLM-facing bundle and manifest
- `posts/<slug>/strategy.md`: post-specific editorial brief
- `posts/<slug>/outline.md`: section structure for human review
- `posts/<slug>/draft.html`: the working document; all loop edits happen inside `<main>`
- `posts/<slug>/.verify/`: transient per-iteration verify pack and screenshots (gitignored)
- `presets/<name>/`: reusable editorial packs (`strategy_template.md`, `writing_guide.md`, `brand_guide.md`, `template.html`)
- `prompts/verifier_rubrics.md`: single source of truth for what "good" looks like; shipped to writer and verifier
- `<!-- fb[rule_id]: rationale -->`: the only feedback channel; verifier inserts, fixer removes

## Repo Layout

- `program.md`: workflow law
- `config.yaml`: machine settings including `prepare.default_preset` and verify viewport widths
- `presets/`: reusable preset packs
- `prompts/`: shared prompts including the verifier rubrics
- `skills/`: source skill definitions; edit these, not generated agent copies
- `shared/`: shared check config (banned phrasing)
- `scripts/`: install and ops helpers
- `posts/<slug>/`: committed per-post state (gitignored by default)
