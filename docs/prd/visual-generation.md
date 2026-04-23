# Visual Generation Stage

## Context

After the text draft loop finishes (human approves or stops), the post currently ends with a `draft.qmd` that is prose-only. The goal is a new pipeline stage that turns the approved draft into a post with embedded visuals — HTML/CSS/JS snippets, brand-aligned, quality-gated, human-approved — and later exportable to HTML/PDF/DOCX.

The existing text loop ([src/autobloggy/loop.py](../../src/autobloggy/loop.py), [src/autobloggy/cli.py](../../src/autobloggy/cli.py)) is powerful but has many moving parts: runs, attempts, acceptance tuples, lexicographic hillclimb, `results.tsv`, verdict bundles. That machinery is tuned for *continuous prose revision against a baseline*. Visuals are different: each visual is discrete, generated, critiqued, and approved individually. So we **reuse the elegant parts (disk-native JSON verdicts, skill + fork pattern, frontmatter-driven preset paths) but skip the hillclimb/acceptance-tuple layer**, which would be overkill.

Built as small INVEST-shaped epics so a thin end-to-end slice ships first. Replaces the short "Visual Loop" bullet in [future-work.md](future-work.md); Epic 6 below subsumes the "Render And Export" bullet.

## Status

Use this legend:

- `[x]` implemented in the repo
- `[ ]` not implemented yet

Current state:

- `[x]` Epic 0 landed, but under the newer input contract: `prepare-inputs`, `inputs/user_provided/{brief.md,raw/}`, `inputs/extracted/`, `inputs/prepared/input.md`, and `inputs/prepared/input_manifest.yaml`
- `[x]` Epic 1 landed as an MVP: `prepare-visuals`, `skills/autobloggy-visuals/`, and `embed-visuals`
- `[x]` Epic 2 landed: `Visual Identity` is now a shared preset contract, and `prepare-visuals` bundles that contract into `requests.json`
- `[x]` Epic 3 landed end-to-end: `visual_checks`, `verify-visuals`, deterministic `check-results.json`, `verifier_requests.json`, prompt rubrics, placeholder verdict JSON, Playwright-backed screenshots for pixel-sensitive checks, and parallel verifier execution via `autobloggy-visual-verifier`
- `[x]` Epic 3.5 landed: `verifier_viewport_width` config key (default 820px), all Playwright screenshots now taken at prose-column width, `layout_integrity` verifier added as a must-have
- `[~]` Epic 4 is **partially deferred** as of 2026-04-22 — Epic 4-Lite (single auto-retry on verifier failure) is the next planned slice; full discriminator loop remains deferred
- `[ ]` Epic 4-Lite is not yet implemented (see its section below)
- `[ ]` Epic 5 is not implemented yet
- `[x]` Epic 6 landed: `autobloggy export --slug X --format html|qmd|pdf|docx`, iframe auto-resize via postMessage, `quarto-cli` bundled via uv
- `[ ]` PDF input support is still deferred

Implementation note:

- This PRD started before the input-layout refactor. The shipped implementation uses `prepare-inputs` instead of `index-assets`, `prepare-visuals` instead of `stage-visuals`, and `input_manifest.yaml` instead of `assets.yaml`. Treat the status markers plus the current repo code as the source of truth for landed work.

## Reuse vs. new

**Reuse** (from text loop):

- Deterministic-CLI-owns-state pattern ([src/autobloggy/cli.py](../../src/autobloggy/cli.py))
- Verifier verdict JSON contract — one file per check, status + rationale ([src/autobloggy/verifiers.py](../../src/autobloggy/verifiers.py))
- Fork + synthesize pattern used by [autobloggy-discovery](../../skills/autobloggy-discovery/) and [ffmpeg-analyse-video](../../skills/ffmpeg-analyse-video/) — parallel sub-agents, text-only synthesis in main context
- Preset-driven guides, frontmatter references ([src/autobloggy/prepare.py](../../src/autobloggy/prepare.py) writes `preset_brand_guide` etc.)
- Configurable gate lists in [config.yaml](../../config.yaml) (`must_have_verifiers`, `improvement_verifiers`)
- Rubric-aware generation (generator prompt includes verifier prompts so it targets them from the start — already the pattern for text)

**Skip**:

- Acceptance-tuple / `is_strict_improvement` / baseline copy. Each visual is independent — a per-visual mini-attempt counter is enough, no lexicographic comparison.
- `results.tsv` metric tracking across attempts. Visual iteration is capped at 2-3 tries then gated on humans, not on monotonic improvement.
- Baseline summaries per visual — we compare each attempt to explicit verifier gates, not to "did this get better."

**New**:

- Per-visual attempt directory: `posts/<slug>/visuals/<visual-id>/attempts/<n>/{visual.html, verdicts/, critique.md}`
- Brand guide extension: a `visual_identity` section with color tokens, fonts, sample components, icon library pointers
- A small runtime: raw `{=html}` block embedding into `draft.qmd` (Quarto supports this natively)
- **User-provided asset inventory**: an extraction + mapping layer so diagrams/images/charts the operator provided during intake (PowerPoints, PDFs, loose images) become first-class inputs to visual generation, not an afterthought

## Epic breakdown

Each epic is shippable on its own. Build and land epics in order; do not start the next until the previous is operator-usable.

### [x] Epic 0 — User-provided visual asset intake (implemented under `prepare-inputs`)

**Outcome**: by the time Epic 1 runs, every operator-supplied file is separated cleanly into human-owned inputs and deterministic derivatives. Raw files live under `inputs/user_provided/raw/`, extracted text and images live under `inputs/extracted/`, and the canonical LLM-facing bundle lives under `inputs/prepared/`. Visual inventory is tracked inside `input_manifest.yaml`, not a separate `assets.yaml`.

**Implemented status**:

- `new-post` now scaffolds the raw/extracted/prepared layout
- `prepare-inputs` now owns deterministic extraction and manifest generation
- PPTX text extraction and embedded-image extraction are implemented
- legacy `inputs/user_provided/supporting/` and root-level `user_provided/` files are normalized forward into the manifest
- PDF support remains deferred

**Integration with the existing intake code** — extend, do not parallel. The current pipeline already does 80% of this:

- `SUPPORTED_INPUT_SUFFIXES` already includes `.pptx`; `parse_input()` already parses pptx slide text; `user_asset_files()` already enumerates everything in `user_provided/` regardless of extension
- `run_new_post()` already copies user sources via `copy_user_source()` and calls `generate_strategy()` with a frontmatter dict that we can extend
- `load_post_input_bundle()` is the canonical reader contract — extend its return instead of introducing a separate loader

Extension points, minimal surface:

1. **New sibling module `src/autobloggy/assets.py`** imported by `prepare.py`. Keeps `prepare.py` focused on text inputs and strategy; asset intake becomes a thin, well-tested module.
2. **Extend `parse_input()` for pptx** to *also* emit image references. It already opens the `Presentation` — we add a second loop that walks `slide.shapes` for picture shapes and hands them to `assets.extract_from_pptx_shape(...)` which writes to `inputs/user_provided/extracted/<pptx-stem>/slide-<n>-<i>.{png,jpg}`. Return value from `parse_input` stays the same (`InputContent`); extracted assets accumulate into the manifest via a side channel (the extractor appends, not returns).
3. **Add PDF to `SUPPORTED_INPUT_SUFFIXES`**. Extend `parse_input()` to handle `.pdf` — emit text (via `pypdf`) as `InputContent`, and emit embedded images via `assets.extract_from_pdf(...)` to the same `extracted/<pdf-stem>/` shape.
4. **Loose images** (`.png`, `.jpg`, `.jpeg`, `.svg`, `.webp`) do not become entries in `SUPPORTED_INPUT_SUFFIXES` (they aren't text sources), but `user_asset_files()` already surfaces them. `assets.index_loose_images(user_asset_files(root))` picks them up directly.
5. **Hook into `run_new_post`**: after `copy_user_source` and before `generate_strategy`, insert one call: `assets_manifest_path = assets.index_assets(paths)`. This writes `posts/<slug>/inputs/user_provided/assets.yaml`. `generate_strategy` frontmatter grows one key: `asset_manifest: inputs/user_provided/assets.yaml` (nullable). If no assets, manifest is empty — graceful no-op.
6. **Extend `load_post_input_bundle()`** to return a 4-tuple `(main_input, InputContent, supporting, VisualAssets)` where `VisualAssets` is a thin dataclass read from the manifest. All existing callers unpack the first three; new callers (Epic 1 brief skill) read the fourth.
7. **New CLI `autobloggy index-assets --slug X`** — exposes `assets.index_assets(paths)` as a reentrant command for posts that acquire assets later. Idempotent: re-scans and only describes newly-seen files.
8. **Describe skill `skills/autobloggy-asset-describe/`** (new): fork + synthesize, one sub-agent per asset batch (≈5 images per batch), haiku-class model. Each sub-agent reads images and writes caption/description/tags back as text; main context stays text-only. Same shape as [ffmpeg-analyse-video](../../skills/ffmpeg-analyse-video/). Invoked by `index-assets` after `assets.index_assets()` has written the skeleton manifest; the skill fills in the text fields.

**Manifest shape** (`assets.yaml`):

```yaml
assets:
  - id: deck-slide-03-01
    path: inputs/user_provided/extracted/architecture-deck/slide-03-01.png
    source_file: inputs/user_provided/architecture-deck.pptx
    source_locator: slide 3, picture 1
    format: png
    width_px: 1280
    height_px: 720
    caption: ""          # filled by autobloggy-asset-describe
    description: ""      # filled by autobloggy-asset-describe
    tags: []             # filled by autobloggy-asset-describe
```

**Out of scope for Epic 0**: no LibreOffice dependency for rendering full slide previews — that's a nice-to-have that can be added later if descriptions of extracted raw images prove insufficient. Start with embedded-picture extraction (cheap, no external binaries beyond what `python-pptx` and `pypdf` already give us).

**Why this is Epic 0**: if Epic 1 ships first and asset intake is bolted on later, the generator's mental model solidifies around "always generate from scratch" and we'll fight that assumption forever. Landing Epic 0 first keeps "reuse or adapt provided assets" as a primary path in the generator prompt from day one. It also reuses the existing `new-post` intake machinery almost entirely — the marginal code is small.

### [x] Epic 1 — Thin slice: prepare → generate → embed (implemented MVP)

**Outcome**: Operator runs `autobloggy prepare-visuals --slug X`. Deterministic code refreshes prepared inputs, scans the approved draft for `<!-- visual: hint -->` comments, and writes `posts/<slug>/visuals/requests.json`. The `autobloggy-visuals` skill then writes `brief.md` and `attempts/001/visual.html` per visual. Operator previews the generated HTML files and runs `autobloggy embed-visuals --slug X` to replace the markers in-place.

**Implemented status**:

- `prepare-visuals` is implemented
- `embed-visuals` is implemented
- `skills/autobloggy-visuals/` is implemented
- marker syntax `<!-- visual: hint -->` is implemented
- embed output is an iframe-based raw HTML block, not the original Quarto-specific inline HTML plan
- verifier/discriminator loops are not part of the shipped MVP

- `program.md`: append a Visuals stage block after the approval gate
- `src/autobloggy/cli.py`: new commands `stage-visuals`, `embed-visuals`
- `src/autobloggy/visuals.py` (new): marker scan → brief requests to disk → after briefs exist, generate requests to disk. Each visual gets a stable id derived from marker position + hint.
- `skills/autobloggy-visual-brief/` (new): reads the draft, the strategy, the brand guide's visual identity section, the marked section, **and the asset manifest from Epic 0**. Forks sub-agents one-per-marker (cheaper model — haiku class) so the main context sees only text summaries back. Each brief explicitly records either `source_asset: <asset-id>` (reuse/adapt an existing user-provided asset) or `source_asset: null` (generate from scratch). Writes `posts/<slug>/visuals/<id>/brief.md`.
- `skills/autobloggy-visual-generator/` (new): reads brief + brand guide **+ referenced source asset if any**; forks sub-agents one-per-brief, each producing `attempts/001/visual.html`. Two paths: (a) **Adapt** — embed the user's asset directly (via `<img>` for raster, inlined `<svg>` for vector) with brand-aligned chrome/typography/caption around it; or (b) **Generate** — produce a fresh HTML/CSS/JS visual. **Interactivity expectation: tasteful interactivity is encouraged** — hover states, transitions, small JS animations, interactive charts where they genuinely aid understanding. Self-contained single-file HTML (inline CSS + JS; external deps limited to a short allowlist declared in the brand guide: hosted fonts, one charting lib, icon CDN). Export/rasterization is Epic 6's problem, not the generator's.
- No verifiers or discriminator yet. Human previews all `visual.html` files in a browser (or `quarto preview draft.qmd` if available), then runs `autobloggy embed-visuals` which rewrites matching `<!-- visual: ... -->` markers into raw-HTML blocks referencing the visual.

**Why first**: smallest unit that *delivers visual output into the post across every section that wanted one*. Proves the skill surface, the fork pattern at scale, the file layout, and the Quarto embedding approach before investing in verifiers or discriminators.

### [x] Epic 2 — Brand visual identity

**Outcome**: generator produces on-brand output, not generic.

**Implemented status**:

- `presets/default/brand_guide.md` and `presets/georgian/brand_guide.md` now expose the same `## Visual Identity` schema
- `prepare-visuals` now fails fast if the active preset lacks `## Visual Identity`
- `requests.json` now bundles `visual_identity` directly so the generator does not need to re-derive the contract mid-run

- Extend `presets/*/brand_guide.md` schema with a `## Visual Identity` section covering: color tokens (with hex + semantic roles), font tokens, chart palette, sample component snippets (one or two tiny HTML examples), icon library pointer (e.g., lucide/heroicons CDN or local path to SVG set), aspect ratio conventions
- Implement in the `georgian` preset (which already has colors and fonts — easy to extend)
- Leave `default` preset's visual identity deliberately sparse (neutral fallback)
- Generator skill reads this section and is instructed to quote exact tokens in generated CSS

### [ ] Epic 3 — Visual verifiers (configurable quality gates)

**Outcome**: each generated visual is evaluated against must-have gates before hitting the human.

**Implemented slice**:

- `config.yaml` now has `visual_checks.must_have_verifiers`, `visual_checks.improvement_verifiers`, and `allowed_script_src_hosts`
- `prepare-visuals` now bundles `visual_requirements` plus the current verifier rubrics into `requests.json`, so generation can target the checks from attempt `001`
- `autobloggy verify-visuals --slug X` now writes `check-results.json`, `verifier_requests.json`, placeholder `verdicts/*.json`, and `screenshot.png` for the pixel-sensitive verifiers under the selected visual attempt
- `src/autobloggy/visual_checks.py`, `src/autobloggy/visual_verifiers.py`, `prompts/visual_verifiers/*.md`, and `skills/autobloggy-visual-verifier/` are implemented
- Playwright-backed screenshot capture is implemented for `brand_consistency` and `composition_clarity`, and `autobloggy-visual-verifier` now owns the parallel one-request-per-verifier execution pattern for filling staged verdict JSON files

- Add `visual_checks` block to `config.yaml` parallel to `checks`:

  ```yaml
  visual_checks:
    must_have_verifiers: [visual_relevance, alt_text_quality, text_visual_alignment, source_attribution]
    improvement_verifiers: [brand_consistency, composition_clarity]
  ```

- `src/autobloggy/visual_checks.py` (new): deterministic pre-checks — HTML parses, has `aria-label` or `alt`, no broken `<script src>` to unknown origins, references only colors/fonts from brand guide
- `skills/autobloggy-visual-verifier/` (new, parameterized by verifier name): reads visual + adjacent draft text + verifier rubric, writes JSON verdict (same shape as text verdicts)
- Verifier prompts under `prompts/visual_verifiers/*.md` (mirrors `prompts/verifiers/`)
- **Parallel execution**: verifier sub-agents launched in parallel per visual (fork pattern from `autobloggy-discovery`)
- **Playwright-enabled verifiers only where pixels matter**: `brand_consistency` and `composition_clarity` sub-agents navigate a local `file://` URL and screenshot it; verdict model reads the PNG. `visual_relevance`, `alt_text_quality`, `text_visual_alignment`, `source_attribution` work off HTML + prose only (cheaper, faster, smaller model)
- Generator is made verifier-aware: its prompt pack includes rubrics for all must-haves so it aims at them from attempt 1

### [ ] Epic 3.5 — Verifier viewport matches reader viewport (landed 2026-04-22)

**Outcome**: verifiers screenshot visuals at the width a reader actually sees (~820px prose column), not 1440px. Layout bugs like text clipping and overflow are now visible in the screenshot the verifier model evaluates.

**What shipped**:
- `verifier_viewport_width: 820` in `config.yaml` (overrideable per-repo)
- `capture_visual_screenshot` reads this config key and passes it to Playwright `resize`
- `layout_integrity` added as a must-have verifier with a Playwright-backed screenshot: fails if any text is clipped or overflows at the configured width
- `composition_clarity` rubric updated to reference the configured viewport width

### [ ] Epic 4-Lite — Single auto-retry on must-have verifier failure

**Outcome**: if `verify-visuals` finds a failing must-have, the generator runs once more (`attempts/002/`) with the verdict rationales appended as critique context. Caps at one retry; HITL owns anything still failing after that.

**What this is not**: no separate discriminator skill, no bounded-N loop, no `final` symlink, no monotonic-improvement tracking. Just: fail → one regeneration with critique → re-verify → HITL.

**What to build**:
- `autobloggy-visuals` skill accepts an optional `prior_verdicts` context block; when present the generator prompt includes failed rationales as explicit critique
- New CLI command `autobloggy retry-visual --slug X --visual-id Y` (or `--all-failing`): reads `verdicts/*.json`, extracts failed must-have rationales, calls the generator with critique context, writes `attempts/002/`
- `verify-visuals` then runs on `002/` as normal; `embed-visuals` picks the highest-numbered passing attempt

### [~] Epic 4 — Discriminator/improver mini-loop (deferred 2026-04-22)

**Status**: deferred in favour of Epic 4-Lite. The full discriminator (separate critique skill, bounded-N attempts, per-visual attempt counter) adds machinery that isn't warranted at current volume. Revisit if Epic 4-Lite still leaves too many failing visuals requiring manual intervention.

**Outcome** (if ever built): per-visual auto-improvement before human review.

- `skills/autobloggy-visual-discriminator/` (new): reads verifier verdicts + visual + brief, writes `critique.md` (what to change, concrete)
- Per-visual bounded loop: generator → verifiers (parallel) → if any must-have fails, discriminator → generator revises → try again, capped at N (config: `visual_loop.max_attempts_per_visual`, default 3)
- Each try is `attempts/002/`, `003/`, etc. inside the visual directory
- On exhaustion without passing, surface for human review with all critiques attached
- Human review is still the final gate; discriminator just raises the starting quality

### [ ] Epic 5 — Text+visual co-optimization

**Outcome**: prose referencing visuals reads naturally; no "as shown above" references to nothing.

- After all visuals approved, a single co-edit pass on draft.qmd
- Reuse [autobloggy-copy-edit](../../skills/autobloggy-copy-edit/) with a new `--mode visual-aware` signal: it sees the embedded visuals and can add/trim references, rewrite section intros that would read awkwardly next to a diagram, etc.
- Constraint: preserves thesis and verified claims (inherits copy-edit guardrails)

### [ ] Epic 6 — Export (separable, independent of Epics 1–5)

**Outcome**: `autobloggy export --slug X --format html|qmd|pdf|docx`.

- HTML: `quarto render draft.qmd --to html` (native — raw HTML blocks pass through)
- QMD: no-op (source format is already QMD)
- PDF: `quarto render --to pdf`. Interactive JS visuals need a rasterization fallback — Playwright opens each `visual.html`, screenshots as PNG, swaps raw-HTML block for `![alt](visual.png)` for the PDF build
- DOCX: `pandoc` with the rasterized-PNG path
- Punt to after Epic 1 ships; not in the critical path for "see a visual in the post"

## Critical files

Existing (read or lightly amend):

- `program.md` — visual stages now use `prepare-visuals`, skill `autobloggy-visuals`, `verify-visuals`, skill `autobloggy-visual-verifier`, and `embed-visuals`
- `src/autobloggy/cli.py` — new deterministic command handlers alongside `stage-attempt`; currently `prepare-inputs`, `prepare-visuals`, `verify-visuals`, and `embed-visuals`
- `src/autobloggy/prepare.py` — owns the input-layout refactor, PPTX text/image extraction, `input_manifest.yaml`, and prepared input generation
- `src/autobloggy/presets.py` — no change needed (brand guide path resolution already works)
- `config.yaml` — `visual_checks` is now implemented; `visual_loop` and `asset_intake` remain future work
- `presets/georgian/brand_guide.md` — add `## Visual Identity`
- `presets/default/brand_guide.md` — minimal visual identity stub
- `docs/prd/future-work.md` — the existing "Visual Loop" bullet is now tracked here; keep the shorter "Render And Export" bullet for Epic 6

New:

- `src/autobloggy/visuals.py` — request preparation plus deterministic embed rewriting
- `src/autobloggy/visual_checks.py` — deterministic HTML checks
- `src/autobloggy/visual_verifiers.py` — visual verifier bundle staging
- `prompts/visual_verifiers/*.md` — per-verifier rubrics
- `skills/autobloggy-visuals/`
- `skills/autobloggy-visual-verifier/`
- `posts/<slug>/inputs/extracted/` — deterministic text and image extracts
- `posts/<slug>/inputs/prepared/input_manifest.yaml` — input inventory and provenance
- `posts/<slug>/visuals/<visual-id>/` — per-post generated-visual home

## On-disk shape (Epic 4 fully rolled out)

```text
posts/<slug>/
├── draft.qmd                           (prose + {=html} blocks after embed-visuals)
├── inputs/
│   ├── user_provided/
│   │   ├── brief.md
│   │   └── raw/
│   │       └── <user sources>.pptx|.png|...
│   ├── extracted/
│   │   ├── text/
│   │   └── visuals/
│   └── prepared/
│       ├── input.md
│       └── input_manifest.yaml
└── visuals/
    ├── requests.json                   (candidate list, written by prepare-visuals)
    └── <visual-id>/                    (one dir per visual)
        ├── brief.md                    (from autobloggy-visuals)
        └── attempts/
            ├── 001/
            │   ├── visual.html         (generator output)
            │   ├── verdicts/*.json     (parallel verifier outputs)
            │   └── screenshot.png      (only if a Playwright verifier ran)
            ├── 002/
            │   ├── critique.md         (from discriminator)
            │   ├── visual.html
            │   └── verdicts/*.json
            └── final -> 002/           (symlink to approved attempt)
```

## Verification

- **Epic 0**: run `autobloggy new-post` against an input folder containing a `.pptx` with embedded images and a loose `.png`. Confirm (a) `inputs/prepared/input_manifest.yaml` exists, (b) it lists both extracted and raw visual sources, and (c) extracted files exist under `inputs/extracted/`. Then add another file and run `autobloggy prepare-inputs --slug X`; confirm deterministic outputs refresh without mutating raw inputs. Run `uv run pytest` and confirm the intake tests still pass.
- **Epic 1**: mark 2–3 sections of a test post with `<!-- visual: ... -->` comments, run `prepare-visuals`, generate the `visual.html` files through `autobloggy-visuals`, then run `embed-visuals`. Confirm `draft.qmd` contains the embed blocks and the remaining unselected markers stay untouched when embedding a subset.
- **Epic 3 slice**: after `visual.html` exists, run `verify-visuals`. Confirm `check-results.json`, `verifier_requests.json`, placeholder `verdicts/*.json`, and `screenshot.png` exist under the selected attempt where pixel-sensitive verifiers are enabled, and confirm `requests.json` already includes `visual_requirements` plus bundled verifier rubrics for generation.
- **Epic 2**: inspect generated HTML against georgian brand — colors/fonts match tokens exactly.
- **Epic 3**: intentionally break visual-text alignment (swap visual payload), verify the `text_visual_alignment` verdict fails.
- **Epic 4**: pin a must-have verifier to always fail in a dry-run, watch discriminator produce a critique and generator attempt a retry up to the cap.
- **Epic 5**: run co-edit pass, diff `draft.qmd`, confirm only visual-reference prose changed.
- **Epic 6**: export a post to all four formats, confirm PDF/DOCX show rasterized visuals, HTML preserves interactive JS.

## Resolved decisions

1. **MVP granularity**: all marked sections generate visuals in parallel (fork pattern from day one). Markers are `<!-- visual: hint -->` HTML comments authored during the text draft phase (or added post-approval by the operator).
2. **Interactivity**: tasteful interactivity encouraged — hover, transitions, small JS, interactive charts where they aid understanding. Static rasterization is a concern for export (Epic 6), not for the generator.
3. **Text-loop simplification**: opportunistic. If Epic 3 or Epic 4 surfaces a natural shared abstraction (e.g. a lighter "attempt unit" primitive that both text and visual loops could adopt), refactor the text loop to use it. Not pursued as a standalone goal; no big-bang refactor.
