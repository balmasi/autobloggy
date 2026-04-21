---
name: autobloggy-research
description: Find and register web sources for Autobloggy claims that lack evidence. Use when `claims.yaml` has active claims with empty `source_ids`, or when the claim verifier failed claims for missing or weak support. Produces new `sources.yaml` entries via `autobloggy refresh-sources`.
---

# Autobloggy Research

Use this skill to find web sources for claims that lack evidence, then register them so the claim verifier can re-run.

## Workflow

1. Run `autobloggy research --slug <slug>`. This stages `posts/<slug>/research/questions.yaml` — one entry per active claim with no `source_ids`.
2. Read `brief.md` for audience, voice, and evidence standards before searching. Evidence standards in the brief override the defaults in this skill.
3. For each question, use your web tools (`web_search`, `fetch_url`, or the equivalents in your harness) to find a primary source whose text literally supports the claim wording.
4. Prefer primary sources: original papers, vendor docs, dated official announcements, regulator filings. Use a secondary source only if no primary exists, and say so in the snippet.
5. Copy a short verbatim snippet (≤ 400 chars) from the page that supports the claim. The snippet must appear word-for-word in the page body.
6. Register each source:
   ```
   autobloggy refresh-sources \
     --slug <slug> \
     --source-id <stable-id> \
     --title "<page title>" \
     --kind url \
     --locator "<url>" \
     --snippet "<verbatim excerpt>" \
     --claim-id <claim-id>
   ```
   Pass `--claim-id` multiple times if the same source supports several claims.
7. If two claims need different snippets from the *same* page, register two source entries with distinct `source-id`s (e.g. `openai-gpt5-launch-2025-pricing`, `openai-gpt5-launch-2025-context-window`). `refresh-sources` overwrites by id, so one id = one snippet.
8. Re-run the claim verifier on each touched claim.

## Rules

- Only register sources you have actually read. Never invent a locator.
- Snippets are verbatim excerpts, not paraphrases.
- If three searches don't turn up primary evidence for a claim, stop and flag it for the operator in chat. Do not register a weaker source to close the gap.
- Do not edit `draft.qmd` or `claims.yaml` by hand from this skill. Citation wording belongs to the writer loop; claim-source links are set by `refresh-sources`.
- Stable IDs: kebab-case from publisher + topic + year (e.g. `fda-ai-sciences-guidance-2025`). Keep IDs stable across runs so the registry doesn't fragment.

## Fail Conditions

- Registering a source whose page you did not read (404, paywall, JS-only).
- A snippet that doesn't contain wording supporting the claim.
- Substituting a secondary source when a primary exists.

## File Contracts

- `posts/<slug>/research/questions.yaml`: staged input. Each entry has `claim_id`, `text`, `section`, and optional `hints` (search-query suggestions).
- `sources.yaml`: append-only via `refresh-sources`. Each source has stable `id`, `title`, `kind`, `locator`, and a `snippets` list.
- `claims.yaml`: updated only by `refresh-sources` — it appends the new `source_id` to claim `source_ids` and marks `last_verification.status = needs_rerun`.
