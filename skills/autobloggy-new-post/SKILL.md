---
name: autobloggy-new-post
description: Kick off a new Autobloggy post from a plain-language brief and the post input folder, then help the user review the generated strategy.
---

# Autobloggy New Post

Use this skill only when `program.md` says to start a new post.

This skill owns kickoff and strategy review only. It does not own discovery, outline generation, draft generation, or the attempt loop.

Read `references/kickoff-reference.md` before you interview the user or approve a strategy.

## Kickoff Rules

1. Read `program.md`.
2. Do not lead with slug, preset, or file-path jargon.
3. Start with plain-language intake. If structured question tools are available, use them for:
   - start mode: topic, files, or both
   - preset choice: use the default preset or create a new preset
4. Ask briefly whether to use the default preset or create a new preset. Explain that the default preset is the repo's generic editorial pack.
5. Collect one short freeform brief covering:
   - the post topic
   - the likely audience
   - must-cover points
   - must-avoid framing or tone
6. If the user already has source files, use `posts/<slug>/inputs/user_provided/raw/` as the default home for them.
7. Conversational kickoff briefs belong only in `posts/<slug>/inputs/user_provided/brief.md`.
8. If the user passes file paths directly, let `autobloggy new-post` copy them into `inputs/user_provided/raw/`.
9. Never write generated files under `inputs/user_provided/`. Deterministic extracts and the canonical bundle belong under `inputs/extracted/` and `inputs/prepared/`.
10. Never infer the intended source from active files, open tabs, tests, or example posts.

## Execution

11. Run `autobloggy new-post`.
12. If the repo now has raw files or a substantive brief but no prepared input bundle, run `autobloggy prepare-inputs --slug <slug>`.
13. Read the generated `strategy.md` plus the active preset files.
14. Ask only the follow-up strategy questions needed to resolve the required fields from `references/kickoff-reference.md`.
15. Help edit `strategy.md` until the required sections are concrete and every unresolved marker is cleared.
16. Do not approve the strategy while any required marker or unchecked approval item remains.

## Do Not

- Decide the preset silently when the user has not yet confirmed default vs new preset.
- Treat this skill as the owner of outline generation, discovery, or the attempt loop.
- Edit files under `.agents/skills/` or `.claude/skills/`.
