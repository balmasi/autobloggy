# Autobloggy

Autobloggy is a writing harness for turning a post brief and source material into an approved strategy, reviewed outline, draft, and iterative improvement loop. The product bias is simple kickoff UX plus deterministic stage transitions.

`program.md` is the authoritative workflow document. Read it first.

## Quick Start

1. `uv sync`
2. Start a new post:
   - `uv run autobloggy new-post --topic "Why AI eval loops fail"`
   - or put files under `posts/<slug>/inputs/user_provided/` and run `uv run autobloggy new-post --slug <slug>`
3. Review `posts/<slug>/strategy.md`
4. `uv run autobloggy approve-strategy --slug <slug>`
5. Record the discovery decision: `uv run autobloggy decide-discovery --slug <slug> --decision yes|no`
6. If the decision is `yes`, run discovery before generating the outline
7. `uv run autobloggy generate-outline --slug <slug>`
8. Review `posts/<slug>/outline.md`
9. `uv run autobloggy approve-outline --slug <slug>`
10. `uv run autobloggy generate-draft --slug <slug>`
11. Enter the attempt loop:
   - `uv run autobloggy stage-attempt --slug <slug>`
   - edit the candidate draft
   - `uv run autobloggy verify --slug <slug> --run-id <run-id> --attempt <attempt-id>`
   - fill verdict files
   - `uv run autobloggy evaluate --slug <slug> --run-id <run-id> --attempt <attempt-id>`
   - continue the same run with `uv run autobloggy stage-attempt --slug <slug> --run-id <run-id>`
   - start a fresh run only when intentional: `uv run autobloggy stage-attempt --slug <slug> --new-run`

## Commands

- `new-post`: creates `posts/<slug>/inputs/user_provided/input.md`, copies any passed `--source` files into `inputs/user_provided/supporting/`, and generates `strategy.md`
- `new-preset`: scaffolds a new preset from `presets/default/`
- `decide-discovery`: records the operator's explicit `yes` or `no` discovery decision in `strategy.md`
- `generate-outline`: reads the existing post state and generates `outline.md` after strategy approval and an explicit discovery decision
- `generate-draft`: reads the existing post state and generates `draft.qmd` after outline approval
- `approve-strategy`: marks `strategy.md` approved once required sections and checklist items are resolved
- `approve-outline`: marks `outline.md` approved
- `stage-attempt`: creates a candidate workspace and prompt pack for the next scoped edit; after a run exists, use `--run-id` to continue it or `--new-run` to start over intentionally
- `check`: runs deterministic checks for a draft
- `verify`: creates verifier request bundles and verdict JSON templates
- `evaluate`: applies keep-or-revert logic and appends `results.tsv`

## Core Concepts

- `program.md`: canonical workflow, boundaries, and named skill invocations
- `posts/<slug>/inputs/user_provided/`: default home for a post brief and supporting user files
- `strategy.md`: the approved post-specific plan instantiated from the active preset
- `outline.md`: section structure for human review
- `draft.qmd`: the committed draft that the attempt loop improves through keep-or-revert evaluation
- `presets/<name>/`: reusable editorial packs with `strategy_template.md`, `writing_guide.md`, and `brand_guide.md`

## Repo Layout

- `program.md`: workflow law
- `config.yaml`: machine settings including `prepare.default_preset`
- `presets/`: reusable preset packs
- `prompts/`: task prompts and verifier prompts
- `skills/`: source skill definitions; edit these, not generated agent copies
- `shared/`: shared checks such as banned phrasing
- `posts/<slug>/`: committed per-post state
- `posts/<slug>/runs/`: ignored run state
