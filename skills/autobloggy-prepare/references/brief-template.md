# Brief Template Reference

Use this file to structure the user interview and the final `brief.md`.

## Required Questions

Ask until you can answer each item concretely:

1. Who is the primary reader, and what job are they trying to do?
2. What should the reader understand, decide, or do differently after reading?
3. What voice should the post use? What existing writing should it feel like or avoid?
4. What are the non-negotiable points, examples, or claims the post must cover?
5. What should the post avoid in tone, framing, or argument?
6. What evidence standard applies? Are primary sources required? Are anecdotes acceptable?

If you are operating as an agent:

- In Claude, prefer `AskUserTool` when it is available.
- In Codex, prefer `request_user_input` when it is available.
- If those tools are unavailable, ask the questions directly in chat before approving the brief.

## Required Brief Sections

Every `brief.md` must include these sections before approval:

- `Core Question`
- `Audience`
- `Reader Outcome`
- `Target Voice`
- `Style Guardrails`
- `Must Cover`
- `Must Avoid`
- `Evidence Standards`
- `Open Questions Before Approval`
- `Approval Checklist`

The generated brief may start with defaults, but approval should be blocked until the user-specific items are resolved.

## Default Voice Starting Point

Use this when the user has not given a better voice spec yet, then confirm or replace it:

Write like a sharp practitioner explaining a hard-earned lesson to other capable builders and operators. The tone should be clear, grounded, and confident, with a slight edge of skepticism toward hype, vague claims, and cargo-cult best practices. Keep the prose conversational and business-aware, but technically credible. Favor plain English, concrete examples, operational implications, and crisp judgments. Aim for practical expert over research paper and working system insight over thought leadership.

## Style Guardrails Starting Point

- Use short to medium sentences.
- Lead with the real problem or mistaken assumption.
- Explain through mechanisms, tradeoffs, and consequences.
- Keep abstractions tied to implementation, decisions, or outcomes.
- Sound opinionated when the evidence earns it, and precise when nuance matters.
- Make every paragraph useful to a capable reader.
