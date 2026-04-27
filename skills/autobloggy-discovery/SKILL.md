---
name: autobloggy-discovery
description: Competitive discovery sweep for an Autobloggy post. Spawns parallel research sub-agents to find top existing content, then synthesizes findings into discovery.md to inform the outline.
context: fork
---

# Autobloggy Discovery

Run this skill only for the optional discovery subroutine named by `program.md`.
It searches for substantive existing content on the post topic, extracts what is
worth knowing, and produces a synthesis file that sharpens the outline.

## When to use

Use when:

- Starting a new Autobloggy post and the user wants to know what is already published on the topic before writing the outline
- The user asks for a "discovery sweep", "competitive research", or "see what's out there"
- Refreshing discovery for an existing post when the user explicitly requests it

Skip if:

- The user declines
- `posts/<slug>/inputs/discovery/discovery.md` already exists and the user does not want a refresh

## Inputs required

Before running, you must have:

- `slug` - the post slug
- `topic` - a 2-4 sentence description of the topic, angle, audience, and core question, taken from the approved `strategy.md`

## Instructions

1. Confirm the slug and topic with the caller. If either is missing, ask before proceeding.
2. Derive 5 search queries from the topic - one per angle:
   - `main` - the core topic as a reader would naturally search for it
   - `technical` - implementation, mechanism, or how-it-works angle
   - `practitioner` - lessons learned, real-world usage, case studies
   - `alternative` - counterarguments, downsides, criticism, skepticism
   - `frame` - a fresh or contrarian take on the topic
3. Spawn 5 research sub-agents in parallel, one per query. For each agent, fill in:
   - `{topic}` - the 2-4 sentence topic description
   - `{query}` - the specific query for that angle
   - `{output_path}` - `posts/<slug>/inputs/discovery/<n>-<angle>.md`
4. Wait for all sub-agents to complete. Partial results are acceptable - use whatever was written.
5. Read all files written to `posts/<slug>/inputs/discovery/`. Count the total sources found across all files.
6. Synthesize into `posts/<slug>/inputs/discovery/discovery.md`. Every claim, statistic, or insight in the synthesis **must** carry an inline markdown link: `[Author/Publication](URL)`. The Sources section at the bottom must list each source as a markdown hyperlink. No bare source names — if a URL is missing, omit the claim.
7. Report back with the strongest differentiating angles for the outline.

## Sub-agent Brief

Pass this prompt verbatim to each sub-agent, with the three placeholders filled in:

```text
You are a research agent with one job: find substantive existing content on a given topic, extract what is valuable, and write a structured summary to a file. You have no other context or task.

## Topic
{topic}

## Search Query
{query}

## Instructions

1. Use web search with the query above.
2. From the results, pick the 2-3 most substantive hits. Prefer long-form articles, technical guides, practitioner posts, and pieces that make a specific argument. Skip thin listicles, news roundups, and SEO-farmed content with no real claims.
3. Read the full content of each chosen URL.
4. For each source, extract:
   - The core thesis or argument
   - 3-5 specific insights, frameworks, or claims worth knowing about
   - Any distinctive data points, examples, or case studies
   - Gaps, weaknesses, or angles the author missed or got wrong

## Output

Write a Markdown file to this exact path: {output_path}

For each source, start with `**URL:** <full URL>` immediately after the source heading — this is required so the synthesis step can inline links. Every insight or claim must be attributable to a specific URL you actually fetched.
```
