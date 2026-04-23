---
name: autobloggy-visuals
description: Generate per-marker visuals after deterministic visual requests have been prepared.
---

# Autobloggy Visuals

Use this skill only when `program.md` reaches the visual stage and `autobloggy prepare-visuals --slug <slug>` has already written `posts/<slug>/visuals/requests.json`.

This skill owns non-deterministic visual generation only. It does not own input extraction, request staging, or embed rewriting.

## Inputs to read

1. `program.md`
2. `posts/<slug>/strategy.md`
3. `posts/<slug>/draft.qmd`
4. `posts/<slug>/visuals/requests.json` — treat its `visual_identity`, `visual_requirements`, and `visual_verifiers` fields as the first-stop generation contract
5. `posts/<slug>/inputs/prepared/input.md`
6. `posts/<slug>/inputs/prepared/input_manifest.yaml`
7. The preset brand guide named in the strategy frontmatter (`preset_brand_guide`)

## What to write

For each request in `posts/<slug>/visuals/requests.json`:

- Write `posts/<slug>/visuals/<visual-id>/brief.md`
- Write `posts/<slug>/visuals/<visual-id>/attempts/001/visual.html`

Each visual should be self-contained HTML with inline CSS and JS unless the brief explicitly points to an existing source asset that should be framed or adapted.

## Brand Contract

- Start from the `visual_identity` section already bundled into `requests.json`. Read the full brand guide only for extra context or disclosure language.
- Satisfy every item in `visual_requirements` before you write `visual.html`. The goal is to pass `autobloggy verify-visuals` on the first attempt.
- Treat every rubric under `visual_verifiers.must_have` as a generation target, not just a later review checklist.
- Copy hex codes, font stacks, component names, icon guidance, and aspect ratios exactly from the brand guide. Do not invent substitute brand tokens when the guide already defines them.
- Define CSS custom properties from the listed tokens near the top of `visual.html`, then use those tokens consistently throughout the visual.
- **Responsiveness is a COMPOSITION decision, not a scaling trick.** Design mobile-first at 360 px and enhance upward — not the other way around. The narrow view must *re-compose*, not shrink. Before you commit to a pattern, ask: "does this pattern still communicate at 360 px?"
  - Wide comparison tables → stacked cards or a key:value list at narrow widths. Never ship a horizontally-scrolling wide table as the mobile experience.
  - Grids with 3+ columns → collapse to 1–2 columns with `grid-template-columns: repeat(auto-fit, minmax(...))` or explicit media queries.
  - Dense multi-series charts → simplify at narrow widths (drop secondary series, switch to a summary, or contain horizontal scroll *inside* the visual frame — never let the page scroll).
  - Side-by-side diagrams → restack vertically.
  - If the concept cannot survive this recomposition, pick a different visual pattern entirely. Don't try to force an unsuitable pattern to "be responsive."
  - Use fluid units (`%`, `fr`, `minmax`, `clamp`) and real `@media` breakpoints. No fixed pixel widths on the root container. Include `<meta name="viewport" content="width=device-width, initial-scale=1">` in `<head>`.
  - The verifier harness screenshots the visual at multiple widths (currently 360 px and 820 px) and fails the visual if either width is a broken or naive-shrunk layout.
- **Prevent footer / source-note overlap.** Whenever `.frame` has `aspect-ratio` and uses `display: grid` with named rows, write the content slot as `minmax(0, 1fr)`, never bare `1fr`. A bare `1fr` collapses to zero when the fixed aspect-ratio makes the frame too short, causing the last `auto` row (footer) to drift up into the content area. Also add `overflow: hidden` to `.frame` and `overflow: hidden` to the direct content container (table, card grid, chart wrapper) so that any remaining overflow clips rather than overlaps.
- When adapting a user-provided source asset, keep the asset intact unless the brief explicitly calls for annotation or framing. Apply brand identity in the surrounding chrome, caption, typography, spacing, and supporting labels.
- Keep interactions restrained. Motion should clarify the idea, not advertise the animation.
- Add a visible caption or source note when the visual makes a factual or data-backed claim.

## Brief Expectations

- `brief.md` should name the selected visual pattern, target aspect ratio, and the exact brand tokens the HTML must use.
- `brief.md` must include a **Narrow-width behavior** line that states, in one sentence per breakpoint, how the pattern re-composes at 360 px (e.g. "table → stacked cards, one per row, key on top and value below"). If the answer is "the same layout, just smaller," pick a different pattern.
- `brief.md` should include a short verifier-target checklist that calls out how the planned visual will satisfy each must-have rubric in `visual_verifiers.must_have`.
- If the brief reuses a source asset, record that asset path or id explicitly and explain whether the HTML is framing it, annotating it, or lightly adapting it.

## Boundaries

- Never write under `posts/<slug>/inputs/user_provided/`.
- Never write under `posts/<slug>/inputs/extracted/`.
- Never write under `posts/<slug>/inputs/prepared/`.
- Do not edit `draft.qmd`. `autobloggy embed-visuals` owns the committed draft mutation.
- Do not invent alternate workflow steps outside `program.md`.
