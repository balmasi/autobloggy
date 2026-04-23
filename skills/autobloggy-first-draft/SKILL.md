---
name: autobloggy-first-draft
description: Turn the scaffold produced by `autobloggy generate-draft` into a real first draft before the attempt loop starts.
---

# Autobloggy First Draft

Use this skill only when `program.md` reaches step 9, immediately after `autobloggy generate-draft --slug <slug>` has produced the scaffold at `posts/<slug>/draft.qmd`. This skill owns the one allowed direct edit of `posts/<slug>/draft.qmd` before the attempt loop begins.

This skill does not own kickoff, discovery, outline generation, strategy approval, or the attempt loop.

## Inputs to read

1. `program.md`
2. `posts/<slug>/strategy.md`
3. `posts/<slug>/outline.md`
4. `posts/<slug>/inputs/prepared/input.md`
5. `posts/<slug>/inputs/prepared/input_manifest.yaml`
6. `posts/<slug>/inputs/discovery/discovery.md` if it exists
7. The preset writing and brand guides named in the strategy frontmatter (`preset_writing_guide`, `preset_brand_guide`).

## What to write

Rewrite the body of `posts/<slug>/draft.qmd` in place:

- Preserve the existing YAML frontmatter block exactly. Do not change `title`, `format`, `preset`, or `preset_dir`.
- Keep the single `# <title>` H1 from the scaffold.
- Produce a complete first draft grounded in the strategy, outline, and input bundle. Every `##` section from `outline.md` must appear, in order, as a real reader-facing section.
- Cover every "Must Cover" item from the strategy. Respect every "Must Avoid" rule.
- Follow the preset writing guide for voice, paragraph length, and prose discipline. Follow the brand guide for tone and framing.
- Do not invent facts, claims, examples, or numbers that are not supported by the strategy, outline, or input bundle.
- No em dashes. No assistant or marketing boilerplate. No placeholder text such as "TBD" or "[REQUIRED:...]".
- End with a closing section that gives the reader a concrete takeaway.
- Respect the input boundary: treat `inputs/user_provided/` as human-owned, and do not write under `inputs/extracted/` or `inputs/prepared/`.

## Handing off to the attempt loop

- After writing, run `autobloggy check --slug <slug>` to confirm the deterministic checks pass. Fix any blockers in place.
- Do not run `autobloggy stage-attempt` from this skill. Return control to the operator so they can start the attempt loop.

## Do Not

- Edit `strategy.md`, `outline.md`, `program.md`, `config.yaml`, or anything under `presets/` or `shared/`.
- Edit `draft.qmd` after the first attempt has been staged. From that point forward, only attempt candidates are editable and the `autobloggy-draft-loop` skill owns the work.
- Invent alternate workflow steps outside `program.md`.
