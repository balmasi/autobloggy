# Kickoff Reference

Use this file to structure the intake interview and the final `blog_brief.md`.

## Default Intake Questions

Ask only what is needed:

1. What should this post help the reader understand or decide?
2. Who is the primary reader, and what situation are they in?
3. What source files or examples should shape the post?
4. What must the post include?
5. What claims, tones, examples, or framing should it avoid?
6. Is the default preset/intake depth acceptable, or is there a specific preset, audience, format, or intake depth to select?
7. If a binary source (PDF, DOCX, PPTX, slide image) was passed, ask whether to normalize it with `autobloggy normalize-source` and whether to caption embedded images with a local VLM. Captioning is off by default; only suggest it when the file has meaningful visuals.

## Draftable Brief Checklist

Before the user approves `blog_brief.md`, confirm:

- No `[ASK_USER]` or `[AUTO_FILL]` markers remain.
- `## Generation Context` references brand, writing, format, audience, HTML template, quality criteria, and prepared source manifest files.
- `## Goal` states what the post should accomplish.
- `## Target Reader` is specific enough to guide examples and framing.
- `## Core Thesis` contains one central claim.
- `## Angle` explains why this post is not generic.
- `## Scope` says what is in and out.
- `## Evidence` points to concrete source material.
- `## Full Outline` has publishable `###` section headings.
- `## Required Points` and `## Things To Avoid` are explicit.
