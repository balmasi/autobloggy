---
query: "notebooklm-py python API automation slide deck generation Claude Code"
fetched_at: 2026-04-21T00:00:00Z
---

## Source 1: notebooklm-py — GitHub (teng-lin/notebooklm-py) + PyPI reference
**URL:** https://github.com/teng-lin/notebooklm-py

**Core argument:** notebooklm-py is an unofficial Python library and CLI that exposes Google NotebookLM's undocumented RPC APIs programmatically, unlocking capabilities (PPTX download, batch export, mind map JSON, CSV tables, individual slide revision) that the web UI deliberately withholds from users.

**Key insights:**
- Installation has two tiers: `pip install notebooklm-py` for CLI-only use, and `pip install "notebooklm-py[browser]"` plus `playwright install chromium` for first-time Google auth via `notebooklm login`. After login, credentials are stored locally and no further browser interaction is needed.
- The slide deck command (`notebooklm generate slide-deck`) produces output in either "detailed" or "presenter" format with adjustable length; it can be downloaded as a true editable PPTX (`notebooklm download slide-deck --format pptx`) — this is explicitly called out as a capability the web UI does not offer.
- Infographic generation supports three orientations (portrait, landscape, square) and three detail levels (concise, standard, detailed); output is a PNG (`notebooklm download infographic ./infographic.png`).
- The agentic skill layer (`notebooklm skill install`) drops a SKILL.md into `~/.claude/skills/notebooklm`, teaching Claude Code the full command vocabulary so users can drive the pipeline in natural language rather than memorising CLI flags.
- The async Python API (`NotebookLMClient.from_storage()`) mirrors the CLI 1:1 and is the right surface for scripted batch pipelines: create notebook → add PDF source with `wait=True` → generate artifact → poll `wait_for_completion` → download. This is the path for integrating notebooklm-py into larger Claude Code agent workflows.

**Distinctive data or examples:**
- Latest release 0.3.4, dated March 12, 2026; Python ≥3.10 required; MIT licence.
- Nine generation types are supported: audio overview (4 formats, 3 lengths, 50+ languages), video (3 formats, 9 visual styles), slide deck (PDF/PPTX), infographic (PNG), quiz (JSON/Markdown/HTML), flashcards (JSON/Markdown/HTML), report (Markdown), data table (CSV), mind map (JSON). This breadth means a single ingested PDF can fan out into a full content suite from one Claude Code session.
- `notebooklm source add-research "query"` triggers NotebookLM's internal web research and auto-imports results — meaning the pipeline is not limited to locally provided PDFs.
- `notebooklm agent show claude` prints a bundled guidance document so Claude Code understands which commands are available and in what order to run them.

**Gaps and weaknesses:**
- The library is explicitly unofficial and built on undocumented Google RPC APIs; any Google-side change can silently break it, making it unsuitable as a production dependency.
- Rate limits exist and are opaque: issue #42 in the repo is titled "Slide generation failed: GENERATION_FAILED - Rate limit or quota exceeded", with no documented thresholds.
- The Python async API for slide-deck and infographic download (`download_slide_deck`, `download_infographic`) is not shown in PyPI docs with the same completeness as audio/quiz — practitioners may need to inspect source or rely on CLI wrappers.
- There is no discussion of how to handle multi-document notebooks at scale (e.g., 20 PDFs uploaded in bulk) or how source ingestion latency affects end-to-end pipeline timing.
- No mention of error handling patterns or retry logic for the `wait_for_completion` polling loop.

---

## Source 2: "How to use NotebookLM with Claude Code: 5 demos + 50 use cases with prompts" (aiblewmymind.substack.com)
**URL:** https://aiblewmymind.substack.com/p/notebooklm-claude-code-use-cases

**Core argument:** Pairing NotebookLM with Claude Code via notebooklm-py turns research materials into polished, multi-format deliverables at scale — the combination is more powerful than either tool alone because NotebookLM grounds outputs in real sources while Claude Code automates the downstream formatting, delivery, and chaining steps.

**Key insights:**
- The cost-efficiency argument is concrete: instead of pasting entire documents into Claude's context window (expensive tokens, truncation risk), Claude Code queries NotebookLM's already-indexed sources with targeted questions. NotebookLM acts as a cheap, grounded retrieval layer; Claude Code handles synthesis and formatting.
- The three-step install sequence is reproducible in 5-10 minutes: (1) `pip install "notebooklm-py[browser]"` + Playwright, (2) `notebooklm login`, (3) `notebooklm skill install`. After this, Claude Code can drive the entire pipeline via natural language.
- Five demonstrated use cases move beyond the obvious: competitive intelligence (sources → debate podcast + SWOT PDF + PowerPoint + Gmail draft, all from one prompt); content mining (10+ notebooks → 45 ready-to-post articles in a spreadsheet); interview prep (podcast back-catalogue → printable prep sheet + Notion page); social media scaling (blog post → vertical Instagram Reel with AI video + subtitles); EdTech (course materials → interactive Vercel app with mind maps, flashcards, quizzes, progress tracking).
- The triage framing is implicit but present: Claude Code queries NotebookLM first, then decides what to generate, rather than generating everything blindly. This is the natural insertion point for a "should I read this fully?" decision layer.
- Source grounding is positioned as the key hallucination-prevention mechanism — Claude Code outputs are anchored to actual research materials, not trained priors.

**Distinctive data or examples:**
- Content mining use case produces 45 articles from 10+ notebooks — a concrete throughput figure that illustrates batch scale.
- The Vercel deployment use case shows the pipeline extending beyond document summarisation into interactive application generation, suggesting the output surface is not limited to static files.
- Article notes that casual exploration and real-time source conversation remain better in NotebookLM's web UI — a honest demarcation of where automation adds versus removes value.

**Gaps and weaknesses:**
- The five detailed video demos and the "50 more use cases" section are paywalled; the free tier provides high-level descriptions only, making it hard to verify exact prompt patterns.
- No discussion of failure modes: what happens when NotebookLM's generation fails mid-pipeline, how Claude Code should recover, or how to handle notebooks that produce low-quality outputs.
- The triage angle (deciding what deserves a full read vs. a visual summary) is never made explicit — it is implied by the automation framing but not developed as a standalone workflow.
- No benchmarks or time comparisons between manual web UI workflows and the automated pipeline.

---

## Source 3: "How I Connected NotebookLM to Claude and Changed How I Do Research Forever" (aimaker.substack.com)
**URL:** https://aimaker.substack.com/p/notebooklm-mcp-claude-setup-guide-research-workflow

**Core argument:** Connecting NotebookLM to Claude via MCP eliminates the context-switching friction that breaks research-to-creation momentum — users can access all nine NotebookLM studio features directly from Claude's interface without manual tab-switching.

**Key insights:**
- The problem statement is the sharpest framing available: the manual workflow requires "run deep research in NotebookLM → extract insights → switch to Claude for writing → backtrack to verify sources." Each switch costs cognitive context. The integration collapses this into a single interface.
- The "autonomous research synthesis" use case is significant for triage: Claude can independently query multiple NotebookLM sources while the user is doing something else, then surface a structured summary for a go/no-go decision — this is the reading-backlog triage pattern in concrete form.
- Slide deck generation from 50+ sources is cited as a specific capability: "automatic generation of context-aware slide decks from 50+ sources without manual slide prompting." This is the most direct claim that the pipeline scales to large document collections.
- The author frames setup as achievable in 10-15 minutes and suggests using Claude Code to automate the installation itself — a meta-point that the tool is self-bootstrapping for technical users.
- "NotebookLM's research intelligence with Claude's unlimited creation capabilities" — the author's framing positions NotebookLM as the retrieval/grounding layer and Claude as the unbounded generation layer, which maps directly to the triage + output workflow.

**Distinctive data or examples:**
- Claim that slide decks can be generated from 50+ sources in a single automated pipeline — no manual prompting per slide required.
- Nine NotebookLM studio features accessible via MCP integration: audio overviews, mind maps, flashcards, quizzes, slide decks (plus video, infographic, data table, report).

**Gaps and weaknesses:**
- Full technical setup steps are paywalled; the free excerpt describes the outcome but not the exact MCP server configuration, making it non-reproducible from this source alone.
- The article conflates MCP integration with notebooklm-py CLI integration — these are potentially different authentication and invocation paths, and the distinction matters for practitioners choosing which to implement.
- "50+ sources" claim for slide deck generation lacks qualification: source type, size, language, and whether NotebookLM's own 50-source notebook limit applies are all unaddressed.
- No discussion of output quality variance — whether a 50-source slide deck is coherent or a noisy amalgam is left entirely to the reader's imagination.
- The reading-backlog triage framing is implicit; the author never explicitly addresses how to use the pipeline to decide what warrants a full read versus a skimmable visual output.
