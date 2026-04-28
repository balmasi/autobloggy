---
name: autobloggy-discovery
description: Competitive discovery sweep for an Autobloggy post. Produces a prepared discovery source for blog_brief.md.
context: fork
---

# Autobloggy Discovery

Run this skill only when `program.md` calls for discovery during intake or when the user explicitly requests a discovery sweep before approving `blog_brief.md`.

It searches for substantive existing content on the post topic and produces a normalized prepared source. The brief can then cite that prepared source like any other source.

## When to use

Use when:

- The intake depth's discovery policy is `required`.
- The intake depth's discovery policy is `ask` and the user says yes.
- The user asks for a discovery sweep, competitive research, or to see what is already published.

Skip if:

- The user declines.
- `posts/<slug>/inputs/prepared/discovery/source.md` already exists and the user does not want a refresh.

## Inputs required

Before running, you must have:

- `slug`
- A 2-4 sentence topic description from `blog_brief.md` or the intake source.

## Instructions

1. Confirm the slug and topic with the caller. If either is missing, ask before proceeding.
2. Derive 5 search queries from the topic:
   - `main` - the core topic as a reader would naturally search for it
   - `technical` - implementation, mechanism, or how-it-works angle
   - `practitioner` - lessons learned, real-world usage, case studies
   - `alternative` - counterarguments, downsides, criticism, skepticism
   - `frame` - a fresh or contrarian take on the topic
3. Spawn research sub-agents in parallel only when the caller has authorized sub-agent use in the current environment. Otherwise do the research directly.
4. Write thread notes under `posts/<slug>/inputs/prepared/discovery/threads/`.
5. Synthesize into `posts/<slug>/inputs/prepared/discovery/source.md`. Every claim, statistic, or insight must carry an inline markdown link: `[Author/Publication](URL)`. If a URL is missing, omit the claim.
6. Ensure `posts/<slug>/inputs/prepared/manifest.yaml` contains or is updated with a discovery source entry:

```yaml
- id: discovery
  kind: discovery
  description: Synthesized external discovery for the post.
  normalized: inputs/prepared/discovery/source.md
  origins:
    - inputs/prepared/discovery/threads/main.md
```

7. Report back with the strongest differentiating angles for `blog_brief.md`.

## Sub-agent Brief

Pass this prompt to each research sub-agent, with placeholders filled in:

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
4. For each source, extract the core thesis, specific insights, data points, examples, gaps, and weaknesses.

## Output

Write a Markdown file to this exact path: {output_path}

For each source, start with `**URL:** <full URL>` immediately after the source heading. Every insight or claim must be attributable to a specific URL you actually fetched.
```
