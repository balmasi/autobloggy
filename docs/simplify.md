# Autobloggy Pipeline Simplification — Handoff

This document is the design spec for a major simplification of the Autobloggy pipeline. It was produced through an extended grilling session that walked the design tree branch by branch. **A fresh agent with zero prior context should be able to pick up implementation from this file alone.**

**This redesign is now implemented.** `src/autobloggy/`, `program.md`, `CLAUDE.md`, `README.md`, and the skills are the current state. This document is the design record; see the "As-built delta" section below for where the implementation diverged from the original spec.

---

## Why this redesign

The current pipeline is over-engineered relative to what it actually buys:

- **Verification fan-out is wasteful.** 10 prose verifiers run as 10 parallel sub-agents, each re-reading the prompt file and a 1600-character excerpt of the draft. Visual verifiers run as 6 sub-agents per visual. Most tokens are spent re-loading shared context across sub-agents.
- **Excerpt-based verification is shallow.** Verdicts on `voice`, `overstatement`, `so_what`, `paragraph_focus` etc. are made on tiny windows because the parallelization model can't ship the whole draft to every verifier.
- **The acceptance-tuple / hill-climb loop is heavy machinery for a job nobody asked for.** `runs/<id>/attempts/<n>/`, `state.json`, `results.tsv`, `is_strict_improvement`, baseline diffs, task prioritization — all of it exists to support automatic regression rejection during a 25-iteration sweep that never actually happens. The realistic loop is "fix obvious things, hand back to the human."
- **`draft.qmd` → Quarto → HTML is indirection for nothing.** The publishable artifact is HTML; everything in between is a translation step that adds dependencies (Quarto, mistune candidates, custom iframe-rewrite logic).
- **Visuals are a separate late-phase pipeline.** `prepare-visuals` → `autobloggy-visuals` → screenshot → `verify-visuals` → 6 sub-agent verdicts → `embed-visuals` → re-export. By the time visuals exist, the prose loop has already converged on text that doesn't account for the figures it will eventually carry.

The new pipeline collapses all of this onto **HTML as the single working format**, **inline `<!-- fb[...] -->` markers as the single feedback mechanism**, **two-pass loop with a fresh-context verifier sub-agent**, and **the writer LLM seeing the verifier rubrics upfront** so most issues are pre-empted at first generation.

---

## Mental model (the user's flow)

```
1. Inputs: agent interview + file uploads → extraction → prepared inputs
2. Optional: discovery research → enriched source material
3. Strategy: preset strategy template + inputs → strategy.md (the editorial brief)
4. Outline: strategy + sources → outline.md (with visual placeholders)
5. HUMAN GATE: human reviews and modifies outline
6. Draft v0: outline + strategy + writing guide + brand guide + verifier rubrics + preset template.html
   → draft.html (with visuals inline from the start)
7. LOOP (up to N iterations, where N is set by the user):
     a. autobloggy verify → Python: strip stale markers, run programmatic checks (insert markers at offending DOM nodes), render via Playwright, screenshot at multiple viewport widths, write verify-pack.md
     b. Main agent dispatches autobloggy-verifier (fresh-context sub-agent): reads pack + screenshots + draft, inserts <!-- fb[rule]: rationale --> markers via Edit tool, returns. Never edits prose.
     c. Main agent reads marked-up draft, surgically fixes each issue and removes its marker. For <!-- fb[needs_visual]: hint --> markers, the main agent authors the visual inline (svg, canvas+script, or lightweight JS library chart) — no sub-agent dispatch. For visual feedback markers on existing visuals, edits the visual HTML/SVG/CSS in place.
     d. Re-run verify. If marker count is zero, exit loop. Else iterate.
8. Final human review.
```

The only mid-pipeline human gate is **outline approval**.

---

## Design decisions (the grilled tree)

These are the load-bearing decisions, with rationale. Each was actively grilled and resolved in conversation.

### D1. Drop the multi-attempt / scoring / keep-revert machinery

**Decision:** No `runs/`, no `attempts/`, no `state.json`, no `results.tsv`, no `EvaluationSummary` aggregate, no acceptance tuple, no `is_strict_improvement`, no task prioritization. Draft is edited in place. Git is the audit trail.

**Why:** The hill-climb loop was built to make 25 small mechanical edits autonomously and reject regressions. The realistic loop is 1–5 iterations of substantial agent edits, then human review. Regression-on-some-axis just shows up in the next verify cycle and gets fixed; git diff is the audit.

**What's gone:** `loop.py` (most of it), `scoring.py`, `tasks.py`, `RunState`, `EvaluationSummary`, `results.tsv`, attempt directories, diff files, `stage-attempt`/`check`/`evaluate` CLI commands.

### D2. Inline `<!-- fb[rule_id]: rationale -->` markers as the only feedback mechanism

**Decision:** Verifiers annotate `draft.html` in place with HTML comments of the form `<!-- fb[rule_id]: rationale -->`. Empty-check = zero markers. Document-level findings (e.g. "no real conclusion") go at the very top of `<main>`. Each verify run **strips all existing `fb` markers first** and regenerates from scratch — agent never has to clean stale ones.

**Format:** `<!-- fb[rule_id]: short rationale -->`. Square brackets carry the rule id (matches log/grep patterns); colon-separated rationale. Invisible in any HTML render. Empty-check: `grep -c '<!-- fb\[' draft.html` → 0 means done.

**Why:** Locality is solved natively (marker is right next to the offending span). Empty-check is one grep. Single source of truth (the draft file itself); no separate feedback file to keep in sync. Diff-friendly: a marker disappearing and surrounding prose changing is the visible signal of resolution.

**Special markers:**
- `<!-- fb[needs_visual]: hint -->` — verifier identified that a section would benefit from a visual; fix pass authors the visual inline.
- `<!-- fb[document]: ... -->` — document-level findings without a natural anchor; placed at top of `<main>`.

**What's gone:** `Verdict` model, `VerifierVerdict`, `prose-verdicts.json`, `visual-verdicts.json`, all JSON staging code.

### D3. Two-pass loop with fresh-context verifier sub-agent

**Decision:** Each cycle has two distinct passes:

- **Pass A (judge-and-mark):** `autobloggy verify` (Python) prepares the verify-pack and screenshots; main agent dispatches a **fresh-context `autobloggy-verifier` sub-agent** whose only job is read pack + screenshots + draft → insert markers via Edit tool → return. The sub-agent has no memory of prior iterations, no prose-editing privileges.
- **Pass B (fix):** Main agent reads the marked-up draft, surgically fixes each issue (removing the marker as it goes). Multi-marker fixes can batch into one edit when sensible.
- **Stop:** the fix pass reduces marker count to zero AND the next verify run inserts zero new markers (programmatic + sub-agent both clean). Or the user-specified iteration cap is hit.

**Why:** Fresh context for verification prevents drift and contamination from earlier judgments. Splitting judge from fix keeps each prompt narrow. Two-pass is more round-trips than one-pass, but the audit trail (markers visible in git history) and the unambiguous stop condition (`grep '<!-- fb\['`) are worth it.

### D4. HTML is the working format end to end

**Decision:** No markdown, no pandoc, no mistune, no Quarto. The agent authors and edits `draft.html` directly. Visuals are inline — the right tool for the job: `<svg>` for diagrams and callouts, a lightweight JS library via CDN (Observable Plot / Chart.js / ECharts / D3 on `cdn.jsdelivr.net` / `unpkg.com` / `cdnjs.cloudflare.com`) for real data visualization, `<img>` for source assets. Verify opens the file in Playwright and screenshots it. Programmatic checks parse the DOM via BeautifulSoup.

**Why:** Markdown was a translation layer that bought nothing — text models read markdown OR HTML fine, the publishable artifact is HTML, and rendering during verify costs nothing if the working file is already HTML. Pandoc/mistune both leave the dependency surface; killing that step removes external system deps from the hot path.

**What's gone:** `draft.qmd`, `quarto-cli` dependency, custom iframe-resize-postMessage script, `_stage_for_html` Quarto YAML, `rasterize_embeds`, `copy_visuals_with_resize_hook`, mistune/pandoc dependency.

### D5. Preset-template bootstrap with `<main>` content slot

**Decision:** Each preset ships `template.html`, a complete styled HTML document with a `<main data-content></main>` slot. First-draft generation fills the slot only. Subsequent edits are scoped to `<main>` (programmatic checks scope there too, so chrome doesn't pollute results). Brand styling (CSS, fonts, layout) lives in the template `<head>`.

**Why:**
- The agent's edit surface shrinks. Working in `<main>`, not the whole document. Smaller context, smaller diffs.
- Brand consistency is structural, not aspirational. Can't accidentally drift colors across posts.
- "Use brand colors / fonts" stops being a rubric the LLM has to satisfy every cycle — it's just part of the template.
- Per-post layout overrides are out of scope; if you need a different chrome, fork a new preset.

### D6. Verifiers are plain functions, no abstraction or protocol

**Decision:** No `Verifier` protocol, no class hierarchy, no `VerifierContext`, no `Verdict` model. Verifiers are plain `(text: str) -> str` functions that insert markers. Programmatic checks live in `verifiers/programmatic.py` and self-register via a `@check` decorator into a module-level `CHECKS` list. Adding a check is one decorator. The LLM verifier sub-agent is one prompt file + one skill; no Python class involved.

```python
# verifiers/programmatic.py
CHECKS = []
def check(fn): CHECKS.append(fn); return fn

```

**Why:** The protocol existed to support uniform iteration in a `run_all_verifiers` aggregator that fed `is_strict_improvement` scoring. Both are gone. Verifiers no longer share an interface beyond `(html) -> html with markers inserted`. Forcing a Protocol pays nothing.

### D7. Visuals are first-class inline content, generated alongside prose

**Decision:**
- v0 draft generation produces prose AND inline visuals together in one shot. No `<!-- visual: -->` placeholder phase, no late-phase `prepare-visuals`/`embed-visuals`. Visuals are inline `<svg>`, fenced HTML+JS for `<canvas>`, or `<img>` references — all rendered natively when Playwright opens `draft.html`.
- Visual checks happen at the **whole-post level**, not per-visual. Verify renders the entire draft and screenshots full-page at multiple viewport widths. The multimodal LLM judges prose, visuals, layout, coherence in one pass. No isolated per-visual screenshot, no per-visual verifier pack.
- During the fix pass, `<!-- fb[needs_visual]: hint -->` markers are resolved by the main fix-pass agent authoring the visual inline — no sub-agent dispatch. For complex data visualization the agent uses a lightweight JS library via CDN (Observable Plot, Chart.js, ECharts, D3 — smallest fit for the job); for diagrams and callouts, inline `<svg>`. Visual feedback markers on existing visuals (`fb[layout_integrity]`, `fb[brand_consistency]`, etc.) are fixed by editing the visual in place.

**Why:** Coherence between text and visuals is a generation-time concern. Letting the writer emit both together (with the verifier rubrics in hand) means most coherence issues never arise. Whole-page screenshots solve "does this layout actually work" without a separate per-visual pipeline. A separate visuals sub-agent added round-trip overhead without real benefit — the fix-pass agent has the draft in context and can author/edit visuals inline.

**What's gone:** `<!-- visual: -->` marker grammar, `prepare-visuals`/`embed-visuals`/`verify-visuals` CLI commands, `visuals.py`, `visual_verifiers.py`, per-visual `verifier_requests.json`, per-visual screenshot files, `autobloggy-visual-verifier` skill, `autobloggy-visuals` skill (deleted entirely — not refactored).

**What survives:** Playwright wrapper for screenshots (now used at the whole-post level only).

### D8. Strategy stays as an editorial artifact; only outline has a human approval gate

**Decision:** `strategy.md` is the rich elicited brief — core question, audience, voice, must-cover, guardrails, positioning. Generated from the preset's strategy template + extracted inputs + agent's interview gap-asking. The writer LLM consults it for both outline and draft generation. **No `approve-strategy` CLI gate.**

`outline.md` is markdown (it's a planning artifact, never rendered). Human review and modification of the outline is the only mid-pipeline gate.

**Why:** Strategy is genuinely useful information for the writer. Approval gates that don't add a real check are ceremony; the human reading strategy.md before approving the outline is sufficient.

### D9. Metadata split: `<head>` for public-facing, `meta.yaml` for pipeline state

**Decision:**
- Public-facing meta (`<title>`, `<meta description>`, OG tags) lives in `draft.html`'s `<head>`.
- Pipeline state (`status`, `preset`, `approved_at`, `discovery_decision`, `generated_at`, etc.) lives in `posts/<slug>/meta.yaml`.

**Why:** `<head>` meta gets consumed by browsers/scrapers naturally; authoring it once doubles for export. Pipeline state is just bookkeeping — pollutes `<head>` and forces CLI commands to parse HTML to flip a status flag. YAML is a better home; CLI commands like `approve-outline` patch a key in `meta.yaml`.

### D10. Step 1 ingestion is unchanged; agent runs the conversation

**Decision:** File extraction (`prepare-inputs`) stays as-is. The agent runs the interview-style elicitation around CLI calls — asking the human gap-questions and then invoking `prepare-inputs` / `generate-strategy` / etc. No new "interview mode" CLI surface; the conversation is just normal agent behavior.

**Why:** The current `autobloggy-new-post` skill already does this. No code change needed.

### D11. Writer sees verifier rubrics upfront

**Decision (the user's last addition):** `generate-draft` ships the verifier rubrics — both prose and visual — to the writer LLM along with the strategy, outline, writing guide, brand guide, and prepared inputs. The writer's prompt explicitly says "your output will be evaluated by these rubrics; satisfy them in v0."

**Why:** Most regenerations come from violating rubrics that the writer didn't know about. Telling the writer the test ahead of time front-loads the work to where it's cheapest (one big generation pass), and minimizes loop iterations.

**Implementation:** The verifier rubric file (single consolidated `prompts/verifier_rubrics.md`) is a context input for both `generate-draft` and the `autobloggy-verifier` sub-agent. One source of truth for what "good" looks like.

---

## Resulting CLI surface

The pipeline collapses to a small command set:

| Command | Owner | Purpose |
|---------|-------|---------|
| `autobloggy new-post --topic <…> [--source <path>]…` | Agent | Create post directory, scaffold `inputs/` |
| `autobloggy prepare-inputs --slug <…>` | Agent | Deterministic file extraction → `inputs/prepared/input.md` |
| `autobloggy decide-discovery --slug <…> --decision yes\|no` | Agent (after asking human) | Record gate; agent runs `autobloggy-discovery` skill if yes |
| `autobloggy generate-strategy --slug <…>` | Agent | Apply preset strategy template to inputs → `strategy.md` |
| `autobloggy generate-outline --slug <…>` | Agent | Strategy + sources + (discovery if present) → `outline.md` |
| `autobloggy approve-outline --slug <…>` | Agent (after human approval) | Patch `meta.yaml` with status=approved |
| `autobloggy generate-draft --slug <…>` | Agent | Outline + strategy + writing guide + brand guide + verifier rubrics + preset template.html → `draft.html` (with visuals inline) |
| `autobloggy verify --slug <…>` | Agent (each loop iteration) | Strip markers, run programmatic checks, render via Playwright, screenshot at viewport widths, write `verify-pack.md` |
| `autobloggy new-preset --name <…>` | Agent | Scaffold `presets/<name>/` |

**Deleted commands:** `prepare-visuals`, `embed-visuals`, `verify-visuals`, `stage-attempt`, `check`, `evaluate`, `approve-strategy`.

---

## Resulting file layout

```
posts/<slug>/
  meta.yaml                  # pipeline state: status, preset, approved_at, discovery_decision, …
  strategy.md                # elicited brief (no frontmatter — meta is in meta.yaml now)
  outline.md                 # planning artifact; stays markdown
  draft.html                 # the working document; agent edits in <main> only
  inputs/
    user_provided/
      brief.md
      raw/                   # human-dropped source files
    extracted/               # deterministic extraction (text + visual)
    prepared/
      input.md               # canonical bundle for LLM prompts
      input_manifest.yaml
    discovery/
      discovery.md           # if discovery decision was yes
  .verify/                   # transient verify artifacts (gitignored)
    verify-pack.md
    screenshot-<width>.png
  export/
    html/draft.html          # cp of post-loop draft

presets/<name>/
  template.html              # complete styled HTML doc with <main data-content></main>
  strategy_template.md       # for generate-strategy
  writing_guide.md           # for generate-draft
  brand_guide.md             # for generate-draft and generate-outline (visual placeholder hints)
```

**Deleted from current layout:**
- `posts/<slug>/runs/<id>/attempts/<n>/...` (all of it)
- `posts/<slug>/visuals/<id>/...` (all of it — visuals are inline in draft.html)
- `posts/<slug>/draft.qmd` (replaced by draft.html)
- `posts/<slug>/strategy.md` frontmatter (migrates to meta.yaml)
- `posts/<slug>/outline.md` frontmatter (migrates to meta.yaml)

---

## Resulting module map

| Module | Status | Purpose |
|--------|--------|---------|
| `cli.py` | Refactor | New command set per above |
| `prepare.py` | Refactor | Drop `run_generate_outline`/`run_generate_draft` Quarto specifics. New `run_generate_strategy` step. `generate-draft` produces HTML using `presets/<name>/template.html` and ships verifier rubrics to the prompt. |
| `presets.py` | Light update | Add `template.html` to `PresetPaths` |
| `models.py` | Slim down | Remove `Verdict`, `VerifierVerdict`, `EvaluationSummary`, `RunState`, `CheckResult`, `CheckSummary`, `VerifierRequest` |
| `verifiers/` (new pkg) | New | `programmatic.py` (`@check`-decorated functions, BeautifulSoup-based, scoped to `<main>`); `__init__.py` exposes `verify(html: str) -> str` |
| `verify.py` (new) | New | The `autobloggy verify` CLI command: strip markers, run programmatic checks, render+screenshot via Playwright, write verify-pack.md |
| `render.py` | Not added | No markdown→HTML render step needed |
| `loop.py` | Delete | All of it |
| `scoring.py` | Delete | All of it |
| `tasks.py` | Delete | All of it |
| `checks.py` | Delete | Functions move to `verifiers/programmatic.py` |
| `verifiers.py` (current top-level module) | Delete | Replaced by `verifiers/` package |
| `visual_verifiers.py` | Delete | Whole concept gone |
| `visual_checks.py` | Delete or fold | If any rules survive (e.g., banned-CDN hosts), fold into `verifiers/programmatic.py`. Most don't survive because visuals are inline. |
| `visuals.py` | Delete | Entire module gone. |
| `artifacts.py` | Update | New `meta.yaml` reader/writer; drop frontmatter helpers from strategy/outline (those are now in meta.yaml). |
| `pyproject.toml` | Update | Removed `quarto-cli`, `python-pptx`, `py-readability-metrics`. Added `beautifulsoup4`, `playwright`. |

---

## Skill changes

| Skill | Status | New role |
|-------|--------|----------|
| `autobloggy-new-post` | Light update | No more `--preset` interactive selection ceremony beyond what exists; no `<!-- visual: -->` planning |
| `autobloggy-discovery` | Unchanged | Still optional research step |
| `autobloggy-first-draft` | Refactor | Now produces `draft.html` directly, populating `<main>` of the preset template, with inline visuals from v0. Authors visuals using right-tool-for-job: svg for diagrams, lightweight JS lib for data viz. |
| `autobloggy-draft-loop` | Slim down | Drives the two-pass loop. Iteration cap from human. Dispatches `autobloggy-verifier` sub-agent each cycle, then does the fix pass (prose + inline visual edits together), then re-runs verify. |
| `autobloggy-verifier` (new) | New | Fresh-context sub-agent. Inputs: verify-pack.md, screenshots, draft.html. Output: insert markers via Edit tool, return. Never edits prose or visuals. |
| `slop-mop` | New | Generic final unslop pass and drafting-time prevention rules for public-facing prose. Owns its detector under `skills/slop-mop/scripts/`. |
| `autobloggy-visuals` | **Deleted** | Not refactored — deleted entirely. The fix pass and first-draft agent author/edit visuals inline directly. No sub-agent dispatch for visuals. |
| `autobloggy-visual-verifier` | Delete | Whole concept folded into `autobloggy-verifier` |
| `autobloggy-claim-verifier` | Delete | Deleted. |
| `autobloggy-transcribe` | Unchanged | Local transcription for input prep |

---

## The `<!-- fb[...] -->` marker format

**Format:** `<!-- fb[rule_id]: short rationale -->`

**Examples (inline in draft.html, inside `<main>`):**

```html
<p>The new framework is revolutionary <!-- fb[overstatement]: "revolutionary" — soften or back with a number --> and changes everything.</p>

<p>This work helps you <span>leverage<!-- fb[banned_pattern]: word "leverage" is banned --></span> the model's capabilities.</p>

<h2>Conclusion <!-- fb[conclusion_quality]: this section restates the intro instead of synthesizing --></h2>

<!-- fb[document]: post is missing a clear thesis statement before the first H2 -->
```

**Anchoring rules:**
- Inline-span issues: comment placed immediately after the offending span.
- Heading-level issues: comment after the heading text, before close tag.
- Missing-element / document-level: at top of `<main>`, before the first child.
- Visual issues: comment right next to the offending visual node.

**Programmatic insertion:** Python checks parse the DOM, find the offending node, insert a `Comment` sibling. Output is then serialized back. (BeautifulSoup `insert_after` / `insert` work directly with comments.)

**LLM-sub-agent insertion:** Verifier sub-agent uses the Edit tool with anchored text replacement. Prompt explicitly forbids prose changes.

**Strip:** `BeautifulSoup` find_all on `Comment` instances matching `^fb\[`, remove. Or regex `<!--\s*fb\[([^\]]+)\][\s\S]*?-->` over the source (non-greedy `[\s\S]*?` handles rationale text that contains `<` or `>`). Done at the start of every verify cycle.

---

## What the writer LLM sees on `generate-draft` (D11)

The first-draft prompt receives, as context:

1. The preset's `template.html` (with `<main>` empty) — the writer fills it in.
2. `strategy.md` — editorial brief.
3. `outline.md` — section structure with placeholders.
4. `inputs/prepared/input.md` and `input_manifest.yaml` — source material.
5. `inputs/discovery/discovery.md` if discovery ran.
6. The preset's `writing_guide.md` and `brand_guide.md`.
7. **`prompts/verifier_rubrics.md` — the consolidated rubric the verifier sub-agent will use.** This is new; it's the key to D11.

The prompt explicitly tells the writer:
> Your output will be evaluated against the rubrics in `verifier_rubrics.md` (programmatic + LLM-judged + visual + coherence). Satisfy them in this generation. Visuals must be inline (`<svg>`, `<canvas>+<script>`, `<img>`) inside `<main>` and use only the brand colors/fonts in the brand guide.

The same `verifier_rubrics.md` file is the canonical input for the `autobloggy-verifier` sub-agent. One source of truth.

---

## Verify-pack contents (the verifier sub-agent's brief)

`posts/<slug>/.verify/verify-pack.md`:

```markdown
# Verification pack — <slug> — iteration <K>

You are the autobloggy-verifier sub-agent. Your only job is to read the draft and the screenshots, then insert <!-- fb[rule_id]: rationale --> markers in draft.html for any issues you find. Do NOT edit any prose.

## Files

- Draft: <absolute path to posts/<slug>/draft.html>
- Strategy: <absolute path to strategy.md>
- Outline: <absolute path to outline.md>
- Brand guide: <absolute path to preset brand_guide.md>
- Screenshots:
  - 360px: <absolute path>
  - 768px: <absolute path>
  - 1280px: <absolute path>

## Rubrics

<inline contents of prompts/verifier_rubrics.md>

## Marker rules

- Format: <!-- fb[rule_id]: short rationale -->
- Inline span issues: place comment immediately after offending span.
- Heading issues: inside heading, before close tag.
- Document-level: at top of <main>.
- Visual issues: next to the offending visual node.
- Use only the rule_ids defined in the rubric.

## Programmatic markers already inserted

<list of programmatic rule_ids and their anchors, so you don't double up>

Edit draft.html to insert your markers, then return.
```

---

## Iteration cap

The user-specified maximum number of iterations is communicated to the `autobloggy-draft-loop` skill conversationally ("iterate up to 3 times before checking back with me"). The CLI does not track iteration count — verify just runs each time and reports current marker count. The skill's instructions enforce the cap.

---

## Programmatic checks: porting from current `checks.py`

| Current check | Survives? | New form |
|---------------|-----------|----------|
| `one_h1` | Yes | `len(soup.select("main h1"))` (or scope to whole doc — depends whether template provides H1) |
| `heading_order` | Yes | Walk heading levels in `<main>`; check no level jumps |
| `presentable_headings` | **No — moves to LLM rubric** | Semantic judgment, not regex. Rubric `presentable_headings` lives in the verifier prompt now. |
| `intro_exists` | **No — moves to LLM rubric** | Same; quality-of-intro is semantic. |
| `conclusion_exists` | **No — moves to LLM rubric** | Same. |
| `code_fences_tagged` | Yes | `soup.select("pre code:not([class])")` |
| `latex_balance` | Reassess | If still relevant in HTML, scan text content. Probably drop. |
| `image_caption_alt` | Yes | `soup.select("main img:not([alt])")` and `<figure>` lacking `<figcaption>` |
| `readability_penalty` | Reassess | Was Flesch-Kincaid grade level. If kept, run on `get_text()`. May not be worth it given LLM voice rubric. |

The `@check` decorator pattern (D6) makes adding/removing checks one-line changes.

---

## Migration of existing posts

Existing posts have `draft.qmd`, `strategy.md` with frontmatter, `outline.md` with frontmatter, `runs/`, and `visuals/`. There is no automatic migration in scope. The user's existing posts can either:

1. Be regenerated from inputs under the new pipeline.
2. Be hand-converted (move frontmatter to `meta.yaml`, run draft.qmd's body through the new template, delete `runs/` and `visuals/`).

Plan does not commit to one. Tests for the new pipeline use freshly-created posts.

---

## Open questions / things this spec doesn't pin down

These are intentionally left unresolved — small enough that an implementing agent should pick reasonable defaults or flag them for human input mid-implementation.

All open questions are now resolved:

1. **Viewport widths** → **360 / 768 / 1280**. Implemented.
2. **Iteration history** → **git only**. No `.verify/log.md`.
3. **Discovery decision** → records to **`meta.yaml`** (not strategy frontmatter). Implemented.
4. **Readability penalty** → **dropped**. `py-readability-metrics` removed. Voice/clarity covered by LLM rubric.
5. **CSS location** → **inline `<style>` in `template.html`**. Implemented for default and georgian presets.
6. **Claims verifier** → **deleted**. `autobloggy-claim-verifier` not ported.
7. **Stale verify artifacts** → **`.verify/` cleaned at the start of every verify run** and gitignored.

---

## Implementation order (suggested)

A fresh agent picking this up should sequence the work to keep main branch green at each step:

**Completed.** The implementation order as executed:

1. ✅ New types and infrastructure: `verifiers/` package, `PostMeta` / `meta.yaml` model, `presets/<name>/template.html` for default + georgian.
2. ✅ `verify` CLI command: strip markers → programmatic checks → Playwright screenshots at 360/768/1280 → `verify-pack.md`.
3. ✅ `autobloggy-verifier` skill (new) + slimmed `autobloggy-draft-loop`.
4. ✅ `generate-draft` produces `draft.html` from template; `autobloggy-first-draft` updated for HTML + inline visuals.
5. ✅ `autobloggy-visuals` **deleted** (not refactored — see as-built delta).
6. ✅ Removed the old export command.
7. ✅ Metadata in `meta.yaml`; `approve-outline` and `decide-discovery` patch it.
8. ✅ Deleted: `loop.py`, `scoring.py`, `tasks.py`, `checks.py`, `verifiers.py` (old), `visual_verifiers.py`, `visual_checks.py`, `visuals.py`, `autobloggy-visual-verifier`, `autobloggy-visuals`, old CLI commands.
9. ✅ `program.md`, `CLAUDE.md`, `README.md` rewritten.
10. ✅ Tests: unit tests for all programmatic checks; integration tests for full pipeline through draft + verify.

---

## As-built delta

Where the implementation diverged from the original spec:

| Topic | Spec | As built |
|-------|------|----------|
| `autobloggy-visuals` for `fb[needs_visual]` | Slim refactor: returns HTML fragments via sub-agent dispatch | **Deleted entirely.** The fix-pass agent and first-draft agent author visuals inline — no sub-agent, no fragment hand-off. |
| Inline visual tools | `<svg>`, `<canvas>+<script>`, `<img>` | Same, plus **lightweight JS libraries via CDN** (Observable Plot, Chart.js, ECharts, D3) for real data visualization. Right tool for the job. |
| `pptx` input support | Not mentioned (spec focused on markdown) | **Dropped.** `python-pptx` removed; only markdown/text inputs supported. |
| `inputs/extracted/` layout | Text + visual subdirectories | **Simplified** — `extracted/` directory kept for structure but pptx visual extraction removed; text extraction is minimal. |
| Strip regex | `<!--\s*fb\[[^\]]+\]:[^>]*-->` | `<!--\s*fb\[([^\]]+)\][\s\S]*?-->` — non-greedy to handle `<`/`>` in rationale text without truncating. |
| `generate-strategy` | Listed in CLI table | Implemented as a **separate CLI command** (was implicit in spec); `autobloggy-new-post` skill calls it explicitly. |
| `autobloggy-claim-verifier` | "Reassess" | Deleted without reassessment. |

## Source of truth

**The code is the source of truth.** `program.md` owns the workflow; `CLAUDE.md` indexes the repo. This document is a design record, not an authority. The plan file at `/Users/balmasi/.claude/plans/this-pipeline-is-too-robust-porcupine.md` is an earlier snapshot — not authoritative.
