---
name: autobloggy-new-post
description: Run Autobloggy prep for a new post, then help the user review and complete blog_brief.md.
---

# Autobloggy New Post

Use this skill only when `program.md` says to prepare post artifacts for a new post.

This skill owns intake and `blog_brief.md` review only. It does not own draft generation, verification, or final unslop.

Read `references/kickoff-reference.md` before you interview the user or approve a brief.

## Data
**Available Presets**:

!`find presets -maxdepth 1 -mindepth 1 -type d -exec basename {} \;`

**Available depths (from config.yaml)**:

- !`sed -n '/^intake:/,/^[a-zA-Z]/p' config.yaml | sed -n '/  depths:/,/^[ ]\{2\}[a-zA-Z]/p' | grep -E '^[ ]{4}[a-zA-Z0-9_-]+:' | sed 's/^[ ]*//;s/:.*//' | sed 's/^/- /'`


## Kickoff Rules

1. Read `program.md`.
2. Do not lead with slug, preset, intake depth, or file-path jargon.
3. Start with plain-language intake. If structured question tools are available, use them for start mode: topic, files, or both.
4. Ask briefly whether to use the default preset/intake depth only if the user has not already implied enough context. The fast path is `autobloggy prep --topic "..."`.
5. Collect one short freeform direction covering the topic, likely reader, must-cover points, and must-avoid framing.
6. If the user already has source files, use `posts/<slug>/inputs/raw/` as the default home for originals.
7. If the user passes file paths directly, let `autobloggy prep --source` copy them into `inputs/raw/`.
8. Never write generated files under `inputs/raw/`. Normalized or summarized material belongs under `inputs/prepared/`.
9. Never infer the intended source from active files, open tabs, tests, or example posts.

## Execution

1. Run `autobloggy prep` with the topic, sources, preset, intake depth, and `--select key=value` choices that were explicitly provided or safely defaulted.
2. Read `posts/<slug>/meta.yaml`. Check `discovery.policy`:
   - `required` — run the `autobloggy-discovery` skill before filling the brief.
   - `ask` — ask the user whether to run discovery. If yes, run `autobloggy-discovery`. If no, skip and continue.
   - `never` — skip discovery.
3. Read `posts/<slug>/blog_brief.md`.
4. Fill every `[ASK_USER]` marker using the user's answers.
5. Fill every `[AUTO_FILL]` marker from the topic, prepared source manifest, selected preset resources, and any discovery source referenced by the manifest.
6. Keep `blog_brief.md` human-reviewable. Do not paste every prepared source into it.
7. Make the Generation Context complete. The draft agent must be able to start from `blog_brief.md`, follow its file references, and draft without hidden repo knowledge.
8. Ask only the follow-up questions needed to make the brief draftable.
9. Stop before approval unless the user explicitly approves the completed brief. Approval is done with `autobloggy approve-brief --slug <slug>`.

## Do Not

- Generate `strategy.md` or `outline.md`.
- Run deprecated strategy, discovery-decision, outline, or outline-approval commands.
- Treat this skill as the owner of draft generation, verification, or the attempt loop.
- Edit files under `.agents/skills/` or `.claude/skills/`.
