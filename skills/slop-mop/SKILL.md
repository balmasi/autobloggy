---
name: slop-mop
description: Prevent, detect, and remove AI-sounding prose in public-facing writing. Use when drafting, editing, reviewing, or finalizing blog posts, articles, essays, newsletters, landing-page copy, social posts, documentation meant for readers, or any prose that should not sound generic or machine-written.
context: fork
---

# Slop Mop

Use this skill for public-facing prose in any project. It is not Autobloggy-specific.

## Modes

- **Prevention:** apply the writing rules before producing prose.
- **Detection:** run `scripts/detect_slop.py` on the file or pasted text.
- **Cleanup:** rewrite only the offending sentence, paragraph, or section. Preserve the thesis, facts, claims, and author intent.

## Quick Start

```bash
python3 skills/slop-mop/scripts/detect_slop.py path/to/file.md
python3 skills/slop-mop/scripts/detect_slop.py path/to/file.html --json
python3 skills/slop-mop/tests/run_tests.py
```

If this skill is installed somewhere else, run the script from that skill directory instead.

For pattern details and rewrite guidance, read `references/prose-patterns.md` only when needed.

## Prevention Rules

- Lead with the claim, not a setup about the piece.
- Name the actor, object, metric, tool, place, or tradeoff.
- Prefer concrete nouns and verbs over impressive adjectives.
- Use active voice unless the actor is genuinely unknown or irrelevant.
- Vary sentence and paragraph length.
- Avoid false balance: do not write `not X, but Y` when `Y` can stand alone.
- Avoid narrator distance. Put the reader in the situation when that helps.
- Cut quotable one-liners that sound composed for a slide.
- Avoid em dashes unless the publication style explicitly wants them.

## Detection Workflow

1. Run `scripts/detect_slop.py` on the draft. It has no third-party dependencies.
2. Treat findings as candidates, not truth. Domain terms and brand language can be legitimate.
3. Fix direct rule hits first, then rhythm and structure issues.
4. Re-run the script. A clean pass means no scripted findings; still do a manual skim.

To extend detection, edit `scripts/patterns.yaml`:

- Add one `patterns` entry with a stable rule id.
- Use plain strings for exact phrases. Prefix a pattern with `re:` only when it needs regex behavior.
- Use a YAML list when one rule has several distinct phrases or pattern families.

## Cleanup Workflow

1. For each finding, rewrite the smallest span that solves it.
2. Replace generic claims with source-grounded specifics.
3. Delete throat-clearing instead of rephrasing it.
4. Preserve useful terminology; remove only generic, unsupported, or formulaic usage.
5. Stop when the prose is direct and specific. Do not polish away voice.

## Do Not

- Rewrite distinctive source language into bland professional prose.
- Remove necessary domain terms just because they appear in a pattern list.
- Add new facts while unslopping.
- Turn every sentence short. Human prose needs rhythm, not uniform bluntness.
