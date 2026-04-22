# Outline: Claude Code + NotebookLM Infographic Pipeline

---

## 1. The reading backlog problem (and why your current approach won't fix it)

- The pile grows faster than you can clear it — papers, docs, PDFs that matter but aren't central enough to justify hours
- Reading everything produces worse decisions than reading selectively (cognitive fatigue → decision quality drops)
- The real problem isn't volume; it's the absence of a fast triage layer between "arrived in inbox" and "read end to end"
- What this workflow is for: secondary material, not core reading — state this upfront

---

## 2. The triage decision: full read, visual summary, or skip?

- Introduce the per-document decision rule: how to decide which of three paths a document takes
- When to run the pipeline vs. when to just read:
  - Run it on: long papers where you need the argument but not every detail; reference docs; PDFs from adjacent fields
  - Just read: short posts, core project material, anything where you need to engage with the author's specific phrasing
- The output from the pipeline is the decision aid, not the destination — frame it explicitly

---

## 3. How the pipeline works: two tools, one natural-language interface

- NotebookLM: the grounded retrieval and synthesis layer — why it doesn't just hallucinate (source anchoring), what Studio produces
- notebooklm-py: the programmatic access layer — the CLI that exposes what the web UI withholds (PPTX download is the hook)
- Claude Code: the orchestration layer — natural language drives the whole thing after skill install
- Why this combination works better than pasting PDFs into Claude directly: cheaper, grounded, faster for large docs
- Visual diagram of the three-layer architecture (placeholder)

---

## 4. Setup: from zero to first infographic in 15 minutes

- Install `uv` (one command)
- Install notebooklm-py: `pip install "notebooklm-py[browser]"` + Playwright
- Authenticate: `notebooklm login` — browser-based, credentials stored locally, no repeat prompts
- Run a smoke test: create a notebook, add a short PDF, generate one infographic
- The magic step: `notebooklm skill install` — what it does (drops SKILL.md into ~/.claude/skills/notebooklm), why it matters (Claude Code learns the command vocabulary)

---

## 5. Prompting Claude Code: what to ask for and how to ask it

- The basic prompt pattern: document path → desired outputs → style/detail level
- Specifying output format: infographic (portrait/landscape/square, concise/standard/detailed), slide deck (detailed vs. presenter, PDF vs. PPTX)
- Specifying learning style: how to instruct the agent to tailor visual hierarchy and density to how you actually absorb information
- Representative example prompt (placeholder — to be refined before publish)
- What the nine generation types are and when each is useful (brief taxonomy)

---

## 6. Three real runs

### Run 1: Cursor Composer 2
- What the document was, why it was triage-worthy
- What was generated, how long it took
- Output placeholder (image/screenshot)
- What the output surfaced — and whether it earned a full read

### Run 2: Meta TRIBE v2
- Same structure

### Run 3: Claude Mythos card
- Same structure

---

## 7. What you're actually getting — and what you're not

- What the outputs are good for: quick argument extraction, sharable visual summaries, deciding what to read next
- The hallucination caveat: 13% rate, lower than general LLMs but real — a one-minute verification step before acting on any claim
- Citation gap in visual outputs: NotebookLM doesn't include sources in infographics or slide decks — how to add a provenance step in the Claude Code workflow
- Document type matters: technical academic PDFs are harder to parse than narrative text; expect more variance
- This is a triage tool, not a replacement for deep reading — restate plainly

---

## 8. Time savings and what to do with them

- Rough comparison: ~15 minutes with the workflow vs. ~3–4 hours of conventional close reading (for secondary material — caveat this clearly)
- The real value: surfacing what deserves deeper reading, not skipping it
- What to do with the cleared time: direct it at the material that actually earns the full pass
- The output is easier to scan, share, and revisit — compounding value over time
