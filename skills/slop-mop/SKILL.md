---
name: slop-mop
description: Prevent, detect, and remove AI-sounding prose in public-facing writing. Use when drafting, editing, reviewing, or finalizing blog posts, articles, essays, newsletters, landing-page copy, social posts, documentation meant for readers, or any prose that should not sound generic or machine-written.
context: fork
---

# Slop Mop

Public-facing prose, any project. Not Autobloggy-specific.

## Modes

- **Prevention** — apply the rules in `references/writing-guide.md` while drafting.
- **Detection** — run `scripts/detect_slop.py` on the file or pasted text.
- **Cleanup** — rewrite the smallest span that fixes a finding. Preserve thesis, facts, and author voice.

## Quick Start

```bash
python3 skills/slop-mop/scripts/detect_slop.py path/to/file.md
python3 skills/slop-mop/scripts/detect_slop.py path/to/file.html --json
python3 skills/slop-mop/tests/run_tests.py
```

If installed elsewhere, run from that skill directory.

For the rules, patterns, and rewrite moves, read `references/writing-guide.md`.

## Tone

If the user hasn't specified a tone or reference voice, ask before drafting or rewriting.

## Detection Workflow

1. Run `scripts/detect_slop.py`. No third-party deps.
2. Treat findings as candidates. Domain terms and brand language can be legitimate.
3. Fix direct rule hits first; then rhythm and structure.
4. Re-run. A clean pass means no scripted findings — still skim manually.

## Cleanup Workflow

1. For each finding, rewrite the smallest span that solves it.
2. Replace generic claims with source-grounded specifics.
3. Delete throat-clearing instead of rephrasing it.
4. Stop when prose is direct and specific. Do not polish away voice.

## Extending Detection

Edit `scripts/patterns.yaml`:

- One `patterns` entry per rule, with a stable id.
- Plain strings for exact phrases. Prefix `re:` only when regex behavior is needed.
- A YAML list when one rule has several distinct phrases or pattern families.

`patterns.yaml` and `writing-guide.md` evolve independently. The guide is the human canon; the YAML is the machine detector. A rule can live in one without the other.
