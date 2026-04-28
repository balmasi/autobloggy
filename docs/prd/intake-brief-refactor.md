# PRD: Intake And Blog Brief Refactor

## Summary

Autobloggy should move from a multi-artifact pre-draft workflow to a single approved drafting interface: `blog_brief.md`.

The current workflow exposes too many intermediate artifacts to the operator: prepared input, input manifest, strategy, discovery decision, discovery output, outline, outline approval, and draft scaffold. The refactor should preserve rigor while making the operator experience smoother:

```text
intake -> blog_brief.md approval -> draft.html -> verify/export
```

The central invariant is:

```text
An isolated draft agent should only need blog_brief.md as its entry point.
```

Every other file the draft agent needs must be explicitly referenced from `blog_brief.md`. The draft agent should not rely on implicit knowledge of repo paths, preset layout, or generated artifact conventions.

## Why This Change Exists

The current workflow is technically understandable but operationally noisy. It asks the user to understand the internal pipeline before they can get to a draft:

```text
brief.md -> input.md -> input_manifest.yaml -> strategy.md -> discovery decision -> discovery.md -> outline.md -> draft.html
```

That creates three problems:

1. The user has too many decisions to make before seeing useful output.
2. The visible artifact list does not map cleanly to the user's mental model.
3. Agents need hidden repo knowledge to know which files matter at each stage.

The intended user model is simpler:

```text
I give direction and source material.
The system prepares one complete blog brief.
I approve that brief.
The system drafts against the approved brief.
The verifier checks the result.
```

The refactor should make that model true in the filesystem, CLI, and skills.

## Current State To Replace

The current authoritative workflow in `program.md` has these pre-draft stages:

1. `new-post`
2. `prepare-inputs`
3. `generate-strategy`
4. human review of `strategy.md`
5. `decide-discovery`
6. optional discovery under `inputs/discovery/`
7. `generate-outline`
8. human review of `outline.md`
9. `approve-outline`
10. `generate-draft`

Important current files:

- `posts/<slug>/inputs/user_provided/brief.md`: user-owned kickoff brief.
- `posts/<slug>/inputs/user_provided/raw/`: user-owned raw source files.
- `posts/<slug>/inputs/prepared/input.md`: deterministic LLM-facing source bundle.
- `posts/<slug>/inputs/prepared/input_manifest.yaml`: provenance for prepared input.
- `posts/<slug>/strategy.md`: post-specific editorial strategy.
- `posts/<slug>/outline.md`: approved section structure.
- `posts/<slug>/meta.yaml`: pipeline state.
- `posts/<slug>/draft.html`: generated HTML scaffold and working draft.

The refactor replaces the pre-draft strategy/outline/discovery-decision chain with:

```text
intake -> blog_brief.md -> approve-brief -> generate-draft
```

It does not change the verify loop's core marker model.

## Mental Model For The Refactor

There are four kinds of artifacts:

| Kind | Example | Owner | Purpose |
|---|---|---|---|
| Raw inputs | `inputs/raw/deck.pptx` | Human | Original source material. Never generated into this folder. |
| Prepared sources | `inputs/prepared/source-001/source.md` | System/agent | LLM-readable normalization of raw or discovered material. |
| Approved brief | `blog_brief.md` | Human approves, agent fills | The drafting contract and the only pre-draft user-facing approval artifact. |
| Runtime outputs | `draft.html`, `.verify/*`, `export/html/draft.html` | CLI/agent | Draft, verification, and export artifacts. |

The most important boundary:

```text
Prepared sources explain source material.
The blog brief explains how to use source material to write this post.
```

Do not put drafting instructions in prepared sources. Do not bury source extraction detail in the blog brief.

## Goals

- Collapse `strategy.md` and `outline.md` into one user-facing pre-draft artifact: `blog_brief.md`.
- Replace multiple pre-draft approval gates with one gate: `approve-brief`.
- Make intake configurable by intake depth so users can choose quick, guided, or expert workflows.
- Keep raw human inputs isolated from normalized/generated source material.
- Support both source repurposing workflows and from-scratch topic workflows.
- Allow preset packages to define configurable resources without code changes.
- Keep verifier quality criteria reusable while keeping verifier marker mechanics owned by verifier code.

## Non-Goals

- Do not implement full PPT, video, URL, or image normalization in this refactor.
- Do not preserve deprecated strategy/outline commands for compatibility.
- Do not introduce a large top-level split into separate `brands/`, `formats/`, and `audiences/` packages yet.
- Do not make source normalization aware of the drafting pipeline.
- Do not make `blog_brief.md` a dumping ground for every extracted source detail.
- Do not preserve old command aliases unless a test or user-facing doc proves they are still needed. Simpler is better here.

## User Experience

Fast path:

```bash
uv run autobloggy prep --topic "Why AI eval loops fail"
# review posts/<slug>/blog_brief.md
uv run autobloggy approve-brief --slug <slug>
uv run autobloggy generate-draft --slug <slug>
```

More explicit path:

```bash
uv run autobloggy prep \
  --topic "NPS is too lossy to be a primary CX metric" \
  --preset georgian \
  --intake-depth guided \
  --select audience=ai-founders \
  --select format=thesis \
  --source ./deck.pptx
```

The operator should mostly provide:

- Direction
- Judgment
- Taste
- Business context
- Approval on the angle and outline

The system should provide:

- Structure
- Research and discovery when configured
- Synthesis
- Evidence organization
- Specificity
- Draft readiness

## Human And System Responsibilities

The setup should avoid asking the user to fill a long strategic template. Instead, intake depths decide what to ask, what to infer, and what to omit.

The user is responsible for:

- Supplying a topic or source material.
- Providing business context when the intake depth asks for it.
- Providing taste and constraints when they matter.
- Approving the angle and full outline inside `blog_brief.md`.

The system is responsible for:

- Resolving preset resources and defaults.
- Normalizing raw sources into readable prepared sources.
- Running or skipping discovery based on intake policy.
- Filling inferred sections of `blog_brief.md`.
- Making the draft generator's required context explicit inside `blog_brief.md`.
- Verifying the draft against the same quality bar referenced by the brief.

## Artifact Design

### Post Layout

Target layout:

```text
posts/<slug>/
  blog_brief.md
  draft.html
  meta.yaml
  inputs/
    raw/
      ...
    prepared/
      manifest.yaml
      intake/
        source.md
      source-001/
        source.md
        assets/
          ...
      discovery/
        source.md
        threads/
          ...
  .verify/
    verify-pack.md
    screenshot-360.png
    screenshot-768.png
    screenshot-1280.png
  export/
    html/
      draft.html
```

Rules:

- `inputs/raw/` is human-owned. The user or agent may copy original source files here.
- `inputs/prepared/` is system-owned. Normalized LLM-readable source artifacts live here.
- `blog_brief.md` is the only approved drafting interface.
- `.verify/` remains transient and rebuildable.
- `draft.html` remains the working document after draft generation.
- Do not write generated files into `inputs/raw/`.
- Do not require the draft agent to know about `inputs/prepared/` unless `blog_brief.md` points there.

### Why `inputs/raw/` And `inputs/prepared/` Both Exist

The user will often be told to "drop source files here" or pass `--source`. That location must not be mixed with generated markdown, extracted images, transcripts, or discovery summaries.

The split is:

```text
inputs/raw/       = original user-owned inputs
inputs/prepared/  = generated LLM-readable inputs
```

This is especially important for PPT, video, URL, and multi-file workflows. A slide deck may produce normalized slide text, image annotations, and extracted slide images. Those generated artifacts need a source-local home without polluting the raw input folder.

### Prepared Source Manifest

Replace the current `input_manifest.yaml` shape with a simple structural index:

```yaml
sources:
  - id: intake
    kind: intake
    description: Operator intake from the kickoff conversation.
    normalized: inputs/prepared/intake/source.md
    origins:
      - conversation

  - id: source-001
    kind: ppt
    description: Normalized slide deck about customer metrics and retention.
    normalized: inputs/prepared/source-001/source.md
    origins:
      - inputs/raw/customer-metrics-board-deck.pptx

  - id: discovery
    kind: discovery
    description: Synthesized external discovery about NPS as a primary CX metric.
    normalized: inputs/prepared/discovery/source.md
    origins:
      - inputs/prepared/discovery/threads/main.md
      - inputs/prepared/discovery/threads/technical.md
      - https://example.com/source
```

Decisions:

- Use `origins` as a list of strings.
- Use `description`, not `title`.
- Do not add `role`, `ref`, or typed origin objects yet.
- Multiple origins can merge into one normalized source.
- Discovery is a prepared source, not a separate top-level artifact.
- Intake is also a prepared source with stable ID `intake`.

The manifest is intentionally structural. It should not explain how to draft the article. If a source image needs semantic explanation, put that explanation next to the image in that source's `source.md`, not in the manifest.

### Prepared Source Content

Prepared source files have one job:

```text
Make the original input understandable to an LLM.
```

They should not include drafting instructions, CTA guidance, audience targeting, or section planning. That synthesis belongs in `blog_brief.md`.

No universal source template is required. Each source kind can use natural markdown:

```markdown
# Customer Metrics Board Deck

## Slide 7

Text:
...

Image:
`assets/slide-007.png`

Image description:
This chart shows NPS rising while churn also rises.
```

For a PPT use case, a prepared source should make both text and images understandable:

```markdown
## Slide 12

Visible text:
- NPS increased from 28 to 43.
- Renewal churn increased from 9% to 14%.

Image:
`assets/slide-012.png`

Image description:
Line chart with NPS trending upward while renewal churn also trends upward. The useful meaning is divergence between stated recommendation intent and actual retention behavior.
```

This refactor only needs to support this shape. It does not need to implement extraction yet.

## Blog Brief Design

`blog_brief.md` is generated from a deterministic scaffold, then filled by the LLM and reviewed by the operator.

The scaffold uses only two fill markers:

```text
[ASK_USER] = collect this during interview
[AUTO_FILL] = LLM fills this from topic, preset selections, prepared sources, and discovery
```

If a section is excluded by the intake depth, omit it entirely. Do not use `[excluded]` markers.

Example scaffold:

```markdown
# Blog Brief: NPS is too lossy to be a primary CX metric

## Generation Context

- Brand: `presets/georgian/brand_guide.md`
- Writing: `presets/georgian/writing_guide.md`
- Format: `presets/default/formats/thesis.md`
- Audience: `presets/georgian/audience/ai_founders.md`
- Quality criteria: `prompts/quality_criteria.md`
- Prepared source manifest: `inputs/prepared/manifest.yaml`

## Goal

[ASK_USER]
What business or audience goal should this post serve?
[/ASK_USER]

Reader outcome:

[AUTO_FILL]

## Target Reader

[ASK_USER]
Who exactly is this for? Include role, context, and the decision they are facing.
[/ASK_USER]

What they misunderstand:

[AUTO_FILL]

What they are skeptical of:

[AUTO_FILL]

## Core Thesis

[AUTO_FILL]

## Angle

[AUTO_FILL]

## Scope

[AUTO_FILL]

## Evidence

[AUTO_FILL]

## Full Outline

[AUTO_FILL]

## Required Points

[ASK_USER]
Are there any arguments, examples, terms, or objections that must appear?
[/ASK_USER]

Inferred required points:

[AUTO_FILL]

## Things To Avoid

[ASK_USER]
Are there any claims, phrases, angles, or examples to avoid?
[/ASK_USER]

## Quality Bar

Use `prompts/quality_criteria.md`.

Post-specific checks:

[AUTO_FILL]
```

The approved brief should not contain `[ASK_USER]` or `[AUTO_FILL]` markers.

### Blog Brief As The Draft Agent Interface

The draft agent should be instructed:

```text
Read blog_brief.md first.
Follow the file references in its Generation Context.
Do not assume any other repo structure.
Generate or edit draft.html according to the approved brief.
```

This means `blog_brief.md` must include every path the isolated drafting context needs, including:

- selected brand guidance
- selected writing guidance
- selected format guidance
- selected audience guidance
- selected HTML template or template identity
- prepared source manifest
- quality criteria

Use normal path references by default. Do not use `@path/to/file.md` in generated briefs unless the intent is to inline the referenced file into context automatically. Most resources should be referenced by path so the agent can pull them on demand.

### Required Blog Brief Content

The approved brief must contain enough information to draft without returning to `strategy.md` or `outline.md`.

Minimum required sections for v1:

- `Generation Context`
- `Goal`
- `Target Reader`
- `Core Thesis`
- `Angle`
- `Scope`
- `Evidence`
- `Full Outline`
- `Required Points`
- `Things To Avoid`
- `Quality Bar`

Depths may omit optional sections such as SEO or conversion path. They should not omit `Full Outline` because the outline is the single pre-draft structural approval point.

## Preset Configuration

Presets should define a configurable vocabulary. Code should resolve selected keys generically instead of knowing which resources are flat files or folders.

Example:

```yaml
# presets/georgian/preset.yaml

extends: default

defaults:
  brand: georgian
  writing: georgian
  html_template: georgian
  audience: ai-founders
  format: thesis

definitions:
  brand:
    georgian: brand_guide.md

  writing:
    georgian: writing_guide.md

  html_template:
    georgian: template.html
    longform: templates/longform.html

  audience:
    ai-founders: audience/ai_founders.md
    tech-lead: audience/tech_lead.md
    investor: audience/investor.md

  format:
    thesis: formats/thesis.md
    how-to: formats/how_to.md
    teardown: formats/teardown.md
```

Resolution:

1. Load selected preset.
2. Load parent preset if `extends` is present.
3. Start with parent defaults.
4. Overlay child defaults.
5. Apply CLI selections.
6. Resolve each selected value through child definitions, then parent definitions.
7. Store resolved selections in `meta.yaml`.
8. Write resolved paths into `blog_brief.md` generation context.

One selected value per dimension should be used for a post. Multiple definitions are allowed in the preset, but the post resolves to one selected value per dimension.

Only operational commands may require special resource kinds. For v1, `generate-draft` requires exactly one selected `html_template`.

### Why Presets Use `definitions`

The implementation should not hardcode that brand guides are flat files, audiences are folders, or formats live under `formats/`. Tomorrow's preset may put files elsewhere or introduce a new configurable dimension such as `seo`, `cta`, `compliance`, or `template_variant`.

The code should understand:

```text
dimension -> selected key -> path
```

It should not understand:

```text
audiences always live in presets/<name>/audiences/
formats always live in presets/<name>/formats/
```

This keeps future preset changes mostly configuration-only.

## Intake Depths

Depths control intake UX. They decide:

- Which brief sections are `[ASK_USER]`
- Which brief sections are `[AUTO_FILL]`
- Which brief sections are omitted
- Discovery policy
- Approval strictness
- Whether arbitrary preset dimensions must be explicitly selected

Depths do not control:

- Brand
- Voice
- HTML template
- Post format guidance
- Audience guidance
- Quality criteria

The intake depth may require the user to explicitly select a dimension such as `audience` or `format`, but it should not define what those resources say.

Example config:

```yaml
intake:
  default_depth: fast

  depths:
    fast:
      ask:
        - topic_or_source
      auto_fill:
        - goal
        - target_reader
        - core_thesis
        - angle
        - scope
        - evidence
        - full_outline
        - reader_objections
        - quality_bar
      omit:
        - seo
        - conversion_path
      discovery: auto
      require_selections: []

    guided:
      ask:
        - topic_or_source
        - goal
        - target_reader
        - required_points
        - things_to_avoid
      auto_fill:
        - core_thesis
        - angle
        - scope
        - evidence
        - full_outline
        - reader_objections
        - quality_bar
      omit:
        - seo
      discovery: ask
      require_selections:
        - audience
        - format

    expert:
      ask:
        - topic_or_source
        - goal
        - target_reader
        - core_thesis
        - angle
        - scope
        - evidence
        - required_points
        - things_to_avoid
        - reader_objections
        - seo
        - conversion_path
      auto_fill:
        - full_outline
        - quality_bar
      omit: []
      discovery: ask
      require_selections:
        - audience
        - format
```

Discovery policy values:

```text
never
auto
ask
required
```

There should be no separate discovery decision command.

Discovery is part of intake because discovery affects the brief. If discovery runs, it should produce a prepared source before the brief is finalized. The brief can then cite the prepared discovery source like any other source.

Policy intent:

- `never`: do not run discovery.
- `auto`: the agent decides whether the topic needs discovery.
- `ask`: ask the user during intake.
- `required`: run discovery before finalizing the brief.

## CLI Changes

### Add

```bash
autobloggy prep
```

Inputs:

- `--topic`
- `--slug`
- `--preset`
- `--intake-depth`
- `--source`, repeatable
- `--select key=value`, repeatable

Responsibilities:

- Resolve preset, intake depth, and selections.
- Scaffold post directories.
- Copy user-provided sources into `inputs/raw/`.
- Create normalized intake source at `inputs/prepared/intake/source.md`.
- Create `inputs/prepared/manifest.yaml`.
- Create `blog_brief.md` scaffold with `[ASK_USER]` and `[AUTO_FILL]` markers.
- Store post state and resolved selections in `meta.yaml`.

The LLM agent fills the scaffold after the CLI creates it. The CLI should not pretend to complete inference that requires LLM judgment.

This is the deterministic/agent boundary:

| Responsibility | Owner |
|---|---|
| Slug generation | CLI |
| Directory creation | CLI |
| Source file copying | CLI |
| Preset/intake depth/resource resolution | CLI |
| Scaffold shape and markers | CLI |
| Filling `[AUTO_FILL]` sections | LLM agent |
| Interviewing for `[ASK_USER]` sections | LLM agent |
| Rich source normalization | LLM agent or future deterministic extractor |
| Discovery synthesis | LLM agent |
| Approval status changes | CLI |

```bash
autobloggy approve-brief --slug <slug>
```

Responsibilities:

- Fail if `blog_brief.md` is missing.
- Fail if `[ASK_USER]` or `[AUTO_FILL]` markers remain.
- Validate that a full outline exists.
- Validate that generation context references required resources.
- Set `meta.yaml` status to `brief_approved`.

`approve-brief` should be intentionally mechanical. It should not judge whether the brief is strategically good; that is the human's job. It should only block obviously incomplete or undraftable briefs.

### Change

```bash
autobloggy generate-draft --slug <slug>
```

New behavior:

- Require `meta.status == brief_approved`.
- Require `blog_brief.md`.
- Resolve selected `html_template`.
- Render `draft.html` scaffold from the selected HTML template.
- Fill title/H1 from `blog_brief.md`.
- The first-draft skill then fills `<main>` using only `blog_brief.md` as the entry point and follows references listed there.

### Delete

Remove these workflow commands:

- `generate-strategy`
- `decide-discovery`
- `generate-outline`
- `approve-outline`

Remove `strategy.md` and `outline.md` as generated artifacts.

Deletion is intentional. Do not keep deprecated commands around as a compatibility layer unless this PRD is revised. The goal is one clear workflow, not two parallel workflows.

## Meta State

Extend `meta.yaml`:

```yaml
slug: nps-is-too-lossy-to-be-a-primary-cx-metric
preset: georgian
intake_depth: fast
status: brief_approved
created_at: "2026-04-27T13:43:43+00:00"
brief_approved_at: "2026-04-27T14:04:53+00:00"
selections:
  brand: georgian
  writing: georgian
  html_template: georgian
  audience: ai-founders
  format: thesis
discovery:
  policy: auto
  ran: true
```

`meta.yaml` stores resolved state only. It should not duplicate full intake depth or preset configuration.

The implementation should tolerate older posts while commands for the new workflow should expect the new fields. A legacy post can fail with a clear message telling the user to rerun intake or migrate the post manually.

## Quality Criteria And Verifier Mechanics

Split current `prompts/verifier_rubrics.md` into:

```text
prompts/quality_criteria.md
src/autobloggy/verify.py owns verifier marker mechanics
```

`quality_criteria.md` should contain reusable editorial and visual quality criteria:

- Prose quality
- Evidence/citation expectations
- Heading quality
- Specificity
- Overstatement
- Visual relevance
- Source attribution
- Layout integrity
- Brand consistency

Verifier mechanics should be assembled by `verify.py` into `verify-pack.md`:

- Marker format
- Marker placement
- Do not edit prose
- Screenshots to inspect
- Programmatic marker summary
- File paths

Reasoning:

- The draft generator can reference `quality_criteria.md` without being confused by verifier marker instructions.
- Marker syntax and behavior belong with the verifier subsystem because code strips, inserts, and counts those markers.

Do not create a standalone `prompts/verifier_instructions.md` unless there is a later concrete need. Verifier instructions should be assembled close to `run_verify` so marker syntax, marker counting, stripping behavior, and verifier packet instructions cannot drift apart.

## Skill Updates

Update skills to use `blog_brief.md`:

- `autobloggy-new-post` should become intake-oriented or be replaced by an intake skill.
- `autobloggy-first-draft` should read `blog_brief.md` first and follow its references.
- `autobloggy-draft-loop` should continue to operate only on `draft.html`.
- `autobloggy-verifier` should read the verify pack as before, but quality criteria now come from `quality_criteria.md`.
- Discovery skill should write a prepared source under `inputs/prepared/discovery/source.md`, not top-level `inputs/discovery/discovery.md`.

After skill source edits, reinstall generated copies:

```bash
npx skills add ./skills --agent claude-code codex
```

## Implementation Phases

Each phase should leave the repo in a testable state. Prefer deleting old workflow pieces in the same phase that the replacement becomes functional rather than carrying both paths for long.

### Phase 1: Core Models And Paths

- Update `PostPaths` to include:
  - `blog_brief`
  - `inputs_raw_root`
  - `prepared_manifest`
  - prepared source roots
- Rename or replace old user-provided/prepared path concepts carefully.
- Add Pydantic models for:
  - preset manifest
  - source manifest
  - post selections
  - intake depth config

Notes:

- Current `InputManifest` and `InputTextSource` are shaped around `input.md`; replace them with the new manifest model.
- Current `PostMeta` has `approved_at`, `discovery_decision`, and `discovery_decided_at`; replace with `brief_approved_at`, `intake_depth`, `selections`, and `discovery`.
- Avoid broad compatibility abstractions unless needed by tests. The old workflow is being removed.

### Phase 2: Preset Resolution

- Add `preset.yaml` to `presets/default/` and `presets/georgian/`.
- Implement generic `extends`, `defaults`, and `definitions` resolution.
- Support CLI `--select key=value` overrides.
- Add tests for:
  - child override
  - parent fallback
  - missing required resource
  - selected `html_template` resolution

Notes:

- Resource paths in `preset.yaml` should resolve relative to the preset directory where they are declared.
- Parent fallback should preserve the declaring preset path. If Georgian falls back to `default` for `format: thesis`, the generated brief should reference the default file path.
- CLI `--select key=value` should error on unknown dimensions or unknown selected values with a clear message listing available values.

### Phase 3: Intake Scaffold

- Add `autobloggy prep`.
- Create `inputs/raw/` and `inputs/prepared/`.
- Copy `--source` files to `inputs/raw/`.
- Generate `inputs/prepared/intake/source.md`.
- Generate `inputs/prepared/manifest.yaml`.
- Generate `blog_brief.md` scaffold based on intake depth.
- Persist `intake_depth`, `selections`, and discovery policy to `meta.yaml`.

Notes:

- `--topic` should become part of `inputs/prepared/intake/source.md`.
- If `--source` is supplied, copy the original file into `inputs/raw/` and create a manifest entry. Full normalization can be a placeholder for unsupported kinds in v1.
- The scaffold should be deterministic given the resolved intake depth and selections.
- Do not generate `strategy.md` or `outline.md`.

### Phase 4: Approval Gate

- Add `approve-brief`.
- Validate no fill markers remain.
- Validate full outline section exists.
- Validate generation context references key resources.
- Set `status: brief_approved`.

Suggested v1 validation:

- no literal `[ASK_USER]`
- no literal `[AUTO_FILL]`
- has `## Full Outline`
- has at least two `###` headings under `## Full Outline` or another simple, documented outline check
- has `## Generation Context`
- referenced required resource paths exist

### Phase 5: Draft Generation

- Change `generate-draft` to use `blog_brief.md` and selected `html_template`.
- Remove strategy/outline status gates.
- Extract title/H1 from `blog_brief.md`.
- Update tests to reflect `brief_approved`.

Notes:

- Title extraction should be simple and documented. Prefer `# Blog Brief: <title>` or a required `Working title:` field.
- `generate-draft` should still only scaffold the HTML document. The first-draft skill remains responsible for filling `<main>`.
- The generated scaffold should make it easy for the first-draft skill to edit only inside `<main>`.

### Phase 6: Delete Old Workflow

- Remove old CLI commands:
  - `generate-strategy`
  - `decide-discovery`
  - `generate-outline`
  - `approve-outline`
- Remove `strategy_template.md` usage from the workflow.
- Remove tests for the old workflow or rewrite them around intake/brief.
- Update `program.md`, `README.md`, and `AGENTS.md` command overview.

Also update any skills that mention:

- `strategy.md`
- `outline.md`
- `approve-outline`
- `decide-discovery`
- `inputs/discovery/`
- `prompts/verifier_rubrics.md`

### Phase 7: Quality Criteria Split

- Move reusable criteria from `prompts/verifier_rubrics.md` to `prompts/quality_criteria.md`.
- Move verifier instructions into `verify.py` runtime pack assembly.
- Update verifier pack tests.
- Update skills to reference `quality_criteria.md`.

Notes:

- Preserve the existing marker IDs unless there is a reason to rename them.
- `verify.py` should still insert programmatic markers before screenshots.
- `verify-pack.md` should include the runtime marker instructions plus the content of `quality_criteria.md`.

### Phase 8: Skill Updates

- Update source skill files under `skills/`.
- Reinstall generated agent copies.
- Verify generated copies are not edited directly.

## Acceptance Criteria

- A user can start a new post with only:

  ```bash
  uv run autobloggy prep --topic "..."
  ```

- The post contains one visible pre-draft artifact: `blog_brief.md`.
- `approve-brief` is the only pre-draft approval gate.
- `generate-draft` works from approved `blog_brief.md`.
- Strategy and outline commands are gone.
- Discovery decision command is gone.
- Raw files and prepared files are clearly separated.
- Prepared manifest uses `sources[].id`, `kind`, `description`, `normalized`, and `origins`.
- Preset resources are resolved from `preset.yaml` definitions, not hardcoded folder conventions.
- Verifier quality criteria can be referenced by the draft generator without including marker mechanics.
- Existing verify loop still inserts, strips, counts, and fixes `<!-- fb[...] -->` markers.

## Developer Guardrails

- Keep the new workflow single-path. Do not preserve strategy/outline code "just in case".
- Keep `blog_brief.md` human-reviewable. Do not inline every prepared source into it.
- Keep prepared sources source-focused. Do not add drafting advice there.
- Keep the manifest structural. Do not turn it into a planning document.
- Keep intake depth behavior about UX only: ask, auto-fill, omit, discovery policy, required selections.
- Keep preset behavior about resource selection only.
- Keep verifier marker instructions with verifier code.
- Keep generated agent copies out of direct edits; edit `skills/` source files and reinstall.

## Likely Failure Modes

- Recreating the old workflow by generating `blog_brief.md`, `strategy.md`, and `outline.md` together. Do not do this.
- Making the draft agent rely on implicit repo conventions instead of `blog_brief.md` references.
- Mixing raw user files and generated normalized sources.
- Overdesigning source manifests with roles, typed refs, nested metadata, or drafting notes.
- Letting `quality_criteria.md` include marker insertion instructions.
- Making intake depths control brand or writing guidance instead of just intake UX.
- Implementing full rich media extraction during this refactor and expanding scope.

## Open Implementation Questions

- Exact default brief sections for `fast`, `guided`, and `expert` depths.
- Whether the intake skill should be renamed from `autobloggy-new-post` or introduced as a new `autobloggy-intake` skill.
- Whether old post folders should be migrated or left as legacy examples.
