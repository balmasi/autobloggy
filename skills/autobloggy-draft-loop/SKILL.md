---
name: autobloggy-draft-loop
description: Drive the two-pass verify/fix loop on `posts/<slug>/draft.html` until no `<!-- fb[...] -->` markers remain or the iteration cap is hit.
---

# Autobloggy Draft Loop

Use this skill only when `program.md` reaches the verify loop and `posts/<slug>/draft.html` already has a real first draft inside `<main>`.

## Loop

Repeat until marker count is zero OR the iteration cap the user gave you is hit:

1. **Verify pass.** Run `autobloggy verify --slug <slug>`. This:
   - Strips every existing `<!-- fb[...] -->` marker from `draft.html`.
   - Runs the programmatic checks and re-inserts markers for any deterministic findings.
   - Renders `draft.html` via Playwright and writes full-page screenshots at 360 / 768 / 1280 to `posts/<slug>/.verify/`.
   - Writes `posts/<slug>/.verify/verify-pack.md`.
   - Prints `marker_count` to stdout.

2. **Judge pass.** Dispatch the `autobloggy-verifier` sub-agent (fresh context). Pass it the absolute path to `verify-pack.md`. Its only job is to read the pack + screenshots + draft, then insert additional `<!-- fb[rule_id]: rationale -->` markers in `draft.html` via Edit. It must not edit prose.

3. **Fix pass.** Read the marked-up `draft.html`. For each marker:
   - Surgical fix: rewrite the offending span and remove the marker as part of the same edit.
   - Multi-marker fixes that share a region can batch into one edit when sensible.
   - For `<!-- fb[needs_visual]: hint -->`, author the visual inline. Pick the right tool for the job: inline `<svg>` for simple diagrams and callouts, `<img>` for source assets, and a lightweight JS library via allowed CDN (Observable Plot / Chart.js / ECharts / D3, hosted on `cdn.jsdelivr.net` / `unpkg.com` / `cdnjs.cloudflare.com`) for real data visualization. Use brand tokens already defined as CSS variables in `<head>`, design mobile-first at 360px so it also works at 768/1280, and wrap factual visuals in `<figure>` with a `<figcaption>` source note. Same rules as `autobloggy-first-draft`.
   - For visual feedback markers (`fb[layout_integrity]`, `fb[composition_clarity]`, `fb[brand_consistency]`, `fb[visual_relevance]`, etc.) on an existing inline visual, edit the visual's HTML/SVG/CSS in place.
   - For `<!-- fb[document]: ... -->`, decide where the issue actually lives and fix at that anchor.

4. **Re-verify.** Go back to step 1. If `marker_count` is `0` AND the next verify run inserts no new markers, exit the loop.

If the iteration cap is hit before marker count reaches zero, stop and report the remaining markers to the user. Do not continue past the cap.

## Boundaries

- Edit only `posts/<slug>/draft.html` (and only inside `<main>`).
- Do not edit `strategy.md`, `outline.md`, `meta.yaml`, the preset files, or `program.md`.

## Do Not

- Insert `<!-- fb[...] -->` markers from the main agent context. Markers are inserted by `autobloggy verify` (programmatic) and the `autobloggy-verifier` sub-agent (LLM-judged).
- Skip the fresh-context sub-agent and try to "verify" the draft yourself.
- Continue iterating after the iteration cap.
