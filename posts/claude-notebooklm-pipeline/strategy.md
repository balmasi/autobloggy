---
slug: claude-notebooklm-pipeline
status: approved
input: posts/claude-notebooklm-pipeline/inputs/user_provided/input.md
---

# Strategy: Claude Code + NotebookLM Infographic Pipeline

## Core Question

How can a technical practitioner use Claude Code and NotebookLM together to turn a mounting PDF and paper backlog into scannable infographics and slide decks — without replacing deep reading for the material that actually matters?

## Audience

Technical practitioners: developers, researchers, and PMs who work with AI tools daily, are comfortable with CLI setup, and have a growing backlog of papers, product docs, and technical PDFs they want to process faster.

## Reader Outcome

The reader finishes with a working pipeline. They have installed the tools, run a smoke test, and understand how to prompt Claude Code to produce decks and infographics from any source document. They also know when to reach for this workflow versus when to read the original.

## Target Voice

Enthusiastic early adopter. The author has built and used this pipeline themselves and is genuinely excited to share it. The tone is warm and energetic without being breathless. Use concrete details and real examples to back up the enthusiasm. Avoid hype words, but let the excitement come through in specificity and momentum. Think: the person in your Slack who just figured out something that will save the team hours and can't stop talking about it — but they're also technically sharp and show their work.

## Style Guardrails

- Open with the problem, not the solution. Make the reader feel the pain of the backlog before offering relief.
- Lead every section with the most useful idea, not a preamble.
- Use short to medium sentences. Keep paragraphs to one main idea.
- Show, don't just tell: use the three real example runs (Cursor Composer 2, Meta TRIBE v2, Claude Mythos card) as proof, not decoration.
- Be honest about the time savings claim. "About 15 minutes vs. 4 hours" is striking but must be framed carefully — caveat the comparison, don't stake the whole post on it.
- Explain mechanisms, not just steps. Why does NotebookLM work well here? What is Claude Code actually doing?
- No em dashes. No hype intensifiers. No generic AI assistant phrasing.

## Must Cover

- The triage framing: this workflow is for secondary material, not core reading.
- Setup steps: `uv`, `notebooklm-py`, authentication, smoke test, pointing Claude Code at the repo.
- The prompting guide: how to tell the agent what to produce and how to structure outputs to match a learning style.
- All three real example runs with actual outputs: Cursor Composer 2, Meta TRIBE v2, Claude Mythos card.
- Honest framing of time savings — include the caveat alongside the comparison.
- Decision heuristic: when to use this vs. when to just read.

## Must Avoid

- Do not frame this as a replacement for deep reading. Position it explicitly as a triage layer.
- Do not oversell the 15-minute vs. 4-hour time savings without acknowledging it depends on the material and the reader's goals.
- Do not assume the reader has used `notebooklm-py` before. Treat it as new to them.
- Do not let setup steps dominate the post. The framing, rationale, and examples should get at least as much space as the tutorial section.
- Do not use vague, generic AI-assistant phrasing ("this powerful workflow", "seamlessly integrates", "unlock your potential").

## Open Questions Before Approval

- [x] Example run outputs: use placeholder images/captions for all three; real assets to be swapped in before publish.
- [x] `notebooklm-py` version: latest. Auth is done via the built-in CLI tool — call that out in setup steps.
- [ ] Prompt template: author is not sure yet. Draft will include a representative example prompt; author to review and refine before publish.

## Approval Checklist

- [ ] Core question is specific and answerable
- [ ] Audience is concrete, not generic
- [ ] Reader outcome is a real capability, not vague understanding
- [ ] Voice and style guardrails are specific enough to constrain the draft
- [ ] Must-cover points map directly to sections in the planned outline
- [ ] Must-avoid points are clear enough to catch violations on review
- [ ] Open questions are resolved or explicitly deferred
