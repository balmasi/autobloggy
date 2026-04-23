---
name: autobloggy-visual-verifier
description: Fill visual verifier verdicts after deterministic visual verification bundles have been staged.
model: haiku
---

# Autobloggy Visual Verifier

Use this skill only when `program.md` reaches the visual verification stage and `autobloggy verify-visuals --slug <slug>` has already written `check-results.json`, `verifier_requests.json`, and `verdicts/*.json` for the target visual attempt.

This skill owns only the verifier verdict pass. It does not generate visuals, rewrite HTML, or mutate `draft.qmd`.

## Inputs to read

1. `program.md`
2. `posts/<slug>/visuals/requests.json`
3. `posts/<slug>/visuals/<visual-id>/brief.md` if it exists
4. `posts/<slug>/visuals/<visual-id>/attempts/<attempt>/visual.html`
5. `posts/<slug>/visuals/<visual-id>/attempts/<attempt>/screenshot-<width>.png` (one per configured viewport width) when present
6. `posts/<slug>/visuals/<visual-id>/attempts/<attempt>/check-results.json`
7. `posts/<slug>/visuals/<visual-id>/attempts/<attempt>/verifier_requests.json`
8. `posts/<slug>/draft.qmd`
9. `posts/<slug>/strategy.md`
10. `posts/<slug>/inputs/prepared/input.md`
11. `posts/<slug>/inputs/prepared/input_manifest.yaml`
12. The preset brand guide named in the strategy frontmatter (`preset_brand_guide`)
13. The prompt file named by each request under `prompts/visual_verifiers/`

## What to write

- Update only `posts/<slug>/visuals/<visual-id>/attempts/<attempt>/verdicts/*.json`

Each verdict should keep the existing JSON shape and set:

- `status` to `pass` or `fail`
- `rationale` to a short concrete explanation grounded in the rubric

## Execution flow

1. Read `verifier_requests.json` and identify every staged request for the selected visual attempt.
2. Evaluate the requests in parallel, not serially. Spawn one verifier sub-agent per request, mirroring the fork pattern used by `autobloggy-discovery`.
3. Give each sub-agent exactly one verifier to own. It should read only the files relevant to that verifier and update only its own `verdicts/<verifier>.json` file.
4. Wait for all verifier sub-agents to finish, then do one final pass to confirm there are no remaining `needs_review` verdicts.

## Pixel-sensitive verifier path

- `brand_consistency`, `composition_clarity`, and `layout_integrity` are pixel-sensitive.
- Multiple screenshots are staged per attempt, one per viewport width (e.g. `screenshot-360.png`, `screenshot-820.png`). Inspect **every** screenshot listed in the verifier request's instructions — a pass requires the composition to work at every width, not just shrink.
- If the screenshots are missing or clearly stale, use the installed Playwright CLI wrapper from the `playwright` skill to open the local `visual.html`, resize to each configured width, and recapture before deciding the verdict.
- Prefer the wrapper path described by the installed Playwright skill:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export PWCLI="$CODEX_HOME/skills/playwright/scripts/playwright_cli.sh"
"$PWCLI" open "file:///absolute/path/to/visual.html"
"$PWCLI" resize 360 900
"$PWCLI" screenshot --filename "/absolute/path/to/screenshot-360.png" --full-page
"$PWCLI" resize 820 900
"$PWCLI" screenshot --filename "/absolute/path/to/screenshot-820.png" --full-page
```

Only use Playwright for the pixel-sensitive verifiers. `visual_relevance`, `alt_text_quality`, `text_visual_alignment`, and `source_attribution` should work from the staged HTML and prose bundle alone.

## Sub-agent brief

Use this prompt shape for each verifier sub-agent, filling in the paths for the current request:

```text
You own exactly one Autobloggy visual verifier verdict.

Read these inputs:
- the verifier rubric at {prompt_path}
- the staged verifier request at {verifier_request_path}
- the deterministic check summary at {check_results_path}
- the visual HTML at {visual_html_path}
- the screenshot at {screenshot_path} when present

Then update only this file:
- {verdict_path}

Rules:
- Return only `pass` or `fail` plus a short rationale in the existing JSON shape.
- If deterministic blockers already make the verifier fail, say so directly.
- Do not edit any other file.
```

## Rules

- Read the deterministic `check-results.json` first. If a blocker there obviously causes the verifier to fail, say so directly in the rationale instead of restating the whole rubric.
- Use the prompt file named in each verifier request as the decision rubric.
- For `brand_consistency`, `composition_clarity`, and `layout_integrity`, inspect every `screenshot-<width>.png` first when they exist, then use the HTML and CSS as supporting context. The narrow-width screenshot must show a genuine re-composition, not a shrunken copy of the wide layout.
- Use parallel tool calls or sub-agents for independent verifier requests; do not work through them one by one in the main context.
- Keep rationales short and specific. One or two sentences is enough.

## Boundaries

- Do not edit `visual.html`, `brief.md`, `draft.qmd`, or any prepared inputs.
- Do not invent new verifier names or new workflow steps outside `program.md`.
