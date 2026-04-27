---
name: autobloggy-first-draft
description: Fill the `<main>` of `posts/<slug>/draft.html` with the v0 first draft — prose AND inline visuals — before the verify loop starts.
context: fork
---

# Autobloggy First Draft

Use this skill only when `program.md` reaches the first-draft step and `autobloggy generate-draft --slug <slug>` has produced an HTML scaffold (the preset's `template.html` with an empty `<main data-content></main>`).

This skill owns the one allowed direct edit of `posts/<slug>/draft.html` before the verify loop begins. The verify loop owns subsequent edits.

## Inputs to read

1. `program.md`
2. `prompts/verifier_rubrics.md` — your output will be evaluated against these. Satisfy them in v0.
3. `posts/<slug>/strategy.md`
4. `posts/<slug>/outline.md`
5. `posts/<slug>/inputs/prepared/input.md` and `posts/<slug>/inputs/prepared/input_manifest.yaml`
6. `posts/<slug>/inputs/discovery/discovery.md` if it exists
7. The active preset's `writing_guide.md` and `brand_guide.md` (preset name is in `posts/<slug>/meta.yaml`).
8. `posts/<slug>/draft.html` — the scaffolded HTML doc with empty `<main>`.

## What to write

Edit `posts/<slug>/draft.html` in place. **Only edit inside `<main>`** (and `<title>` / `<meta name="description">` in `<head>`). Leave the rest of the document alone.

- Open `<main>` with the `<h1>` already inserted by the scaffold (do not duplicate it).
- Write a complete first draft grounded in strategy + outline + input bundle. Every `##`-level heading from `outline.md` should appear, in order, as a real reader-facing `<h2>`.
- Cover every "Must Cover" item from the strategy. Respect every "Must Avoid" rule.
- Follow the preset writing guide for voice, paragraph length, and prose discipline.
- Use semantic HTML: `<p>`, `<h2>`, `<h3>`, `<ul>`, `<ol>`, `<blockquote>`, `<figure>` + `<figcaption>`, `<pre><code class="language-…">`, `<a href>`.
- **Author inline visuals as you go.** Where the argument lands harder with a figure, write the visual inline using `<svg>`, `<canvas>` + `<script>`, or `<img>` with a real `alt`. Wrap visuals in `<figure>` with a `<figcaption>` when they make a sourced or factual claim. Use only the brand colour tokens and font stacks defined in the preset's `brand_guide.md` — these are already wired up as CSS variables in `<head>`.
- Update `<title>` and `<meta name="description">` in `<head>` to match the post.
- Do not invent facts, claims, or numbers not supported by the strategy, outline, or input bundle.
- Do not insert `<!-- fb[...] -->` markers. Those are inserted by the verifier in the next phase.
- No em dashes. No assistant or marketing boilerplate. No placeholder text.

## Visual authoring rules

Pick the right tool for the job. Don't hand-roll an SVG bar chart when a 3kb library does it better; don't pull in D3 to draw two boxes and an arrow.

- **Inline `<svg>`** — simple diagrams, comparisons, callouts, structural figures, single-shape illustrations. Hand-author. Use brand colour tokens via `var(--…)`.
- **Inline `<img src="…" alt="…">`** — when the brief points to a source asset already in `posts/<slug>/inputs/`.
- **Lightweight JS library via CDN** — real data visualization (multi-series charts, geographic maps, force layouts, time-series, anything with axes/tooltips/responsive scales). Reach for the smallest library that fits:
  - [Observable Plot](https://cdn.jsdelivr.net/npm/@observablehq/plot) — declarative charts, ~50kb gzipped, the default for most quantitative figures.
  - [Chart.js](https://cdn.jsdelivr.net/npm/chart.js) — bar / line / pie / scatter when Plot's grammar feels heavy.
  - [ECharts](https://cdn.jsdelivr.net/npm/echarts) — when you need rich interactivity, complex composed charts, or geographic data.
  - [D3](https://cdn.jsdelivr.net/npm/d3) — only when you genuinely need the full primitives (force layouts, custom scales, bespoke shapes). Don't reach for D3 first.
  - Allowed CDN hosts: `cdn.jsdelivr.net`, `unpkg.com`, `cdnjs.cloudflare.com`. Pin a specific version. Load via `<script src="…">` in the section, then render into a sibling `<div>` with an inline `<script>`.
  - Style the chart with the brand CSS variables (pass `var(--color-brand-…)` strings into the library config). Don't accept default chart colours.
- Wrap factual / data-backed visuals in `<figure>` with `<figcaption>` naming the source.
- Every visual must work at 360px, 768px, and 1280px viewport widths — design mobile-first, re-compose at wider widths. The verify pass screenshots full-page at all three. For library charts, set `responsive: true` (or the equivalent) and use a container with no fixed pixel width.
- Prefer fewer, sharper visuals over many decorative ones.

## Hand-off

After writing, return control. Do not run `autobloggy verify` or any loop command from this skill. The operator decides when to start the verify loop.

## Do Not

- Edit `strategy.md`, `outline.md`, `program.md`, `meta.yaml`, the preset files, or anything outside `<main>` of `draft.html` (other than `<title>` / `<meta name="description">`).
- Insert any `<!-- fb[...] -->` marker. The verifier owns those.
- Author standalone `visual.html` files. Visuals are inline in `draft.html`.
- Invent alternate workflow steps outside `program.md`.
