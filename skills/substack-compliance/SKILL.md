---
name: substack-compliance
description: Compliance-only review of a blog post draft for SEC Marketing Rule alignment, Georgian portfolio-disclosure rules, and Georgian's substantiation/voice standards. Use only when the user explicitly invokes a compliance signal — SEC, marketing rule, regulatory, compliance, disclosure, portfolio-company mention, substantiation, "fair and balanced", investment-adviser language. Trigger on phrases like "compliance check", "compliance review", "compliance audit", "SEC marketing rule check", "review this post for compliance", "check this draft for compliance", "audit this post for compliance", "is this draft compliant", "portfolio disclosure check", "substantiation check". 
---

# Blog Content Compliance Reviewer

Reviews blog content to ensure adherence to SEC Marketing Rule principles and Georgian's writing standards.

---

## Core Principles

Content from a registered investment adviser must NOT:

1. Include untrue statements of material fact, or omit facts making statements misleading
2. Include material statements of fact that cannot be substantiated upon demand
3. Include information reasonably likely to cause untrue or misleading implications
4. Discuss benefits without fair and balanced treatment of material risks or limitations
5. Contain information that is otherwise materially misleading

---

## Review Categories

### Category A: Language and Tone

**SUPERLATIVES** — Flag and revise
- Bad: "best-in-class", "leading", "superior", "unmatched", "world-class"
- Good: "among the [category]", "competitive", "notable", "deep experience"
- Rationale: Cannot be substantiated

**ABSOLUTE CLAIMS** — Flag and revise
- Bad: "will transform", "ensures success", "always delivers"
- Good: "may transform", "seeks to", "has historically"
- Rationale: Future outcomes cannot be guaranteed

**RHETORICAL ABSOLUTES** — Flag and revise
- Rhetorical Q&A pairs where the answer is a flat "Yes.", "No.", "Never.", or similar absolute
- Ask: is this "never" or "not always"? Could the answer be true in some cases?
- Bad: "Does X solve Y? No." → Good: "Does X solve Y? Not on its own."
- Bad: "Is X the answer? Yes." → Good: "Is X the answer? In many cases, yes."
- Rationale: Punchy rhetorical denials/affirmations are still absolute claims — they state something categorically without qualification, which cannot be substantiated

**PUFFERY** — Flag and revise
- Bad: "unmatched expertise", "revolutionary", "unprecedented"
- Good: "specialized", "innovative", "significant"
- Rationale: Must be substantiable or clearly framed as opinion

**UNHEDGED PREDICTIONS** — Flag and revise
- Bad: "This technology will dominate the market"
- Good: "This technology may gain significant adoption"

**EXTREME QUALIFIERS** — Tone down
- Bad: "massive datasets", "countless applications", "unprecedented growth"
- Good: "large datasets", "numerous applications", "notable growth"

**Required qualifiers to introduce where appropriate:**
- "We believe", "In our view", "Based on our analysis"
- "May", "Could", "Seeks to", "Is designed to"
- "From what we understand", "Subject to further diligence"

**CLARITY** — Ensure all sentences are unambiguous and clearly structured.

**OXFORD COMMA** — Do NOT use the Oxford comma. This is a hard constraint.
- Bad: "engineers, researchers, and CTOs"
- Good: "engineers, researchers and CTOs"
- Rationale: Georgian style guide prohibits the serial comma in all communications

**GRAMMAR & SPELLING** — Review using AP style guide. Flag typos and grammatical errors.

---

### Category B: Forward-Looking Statements

Flag any:
- Predictions presented as certainties
- Claims about future technology capabilities without hedging
- Statements using "will" for future outcomes (vs. "may" or "seeks to")
- Projections about industry trends without qualification

Transform examples:
- Bad: "Future versions will have significant improvements" → Good: "Future versions may have improvements"
- Bad: "Eventually, the company envisions developing a fully trained AI Agent" → Good: "The company is exploring development of AI Agent capabilities"
- Bad: "This will set the merged entity apart" → Good: "We believe this could differentiate the combined company"

---

### Category C: Claims and Substantiation

Flag any claim that:
- Makes specific numerical assertions without source/citation
- Uses statistics or data points without attribution
- States unique or exclusive capabilities without support
- Makes technology capability claims that could be verified as false
- References research or studies without citation

**Trigger list — flag every instance of:**
- A named-person attribution ("as Cornelia Davis argues", "according to Tom Wheeler") with no inline link or footnote
- A numerical or statistical claim, including percentages, dollar amounts, latency numbers, ratios ("4% of the time", "16x lower latency", "$70K per month")
- A decade or year reference used to ground a claim ("In the early 2010s", "for years", "for decades")
- A reference to a named external concept, framework, library or product on first use ("Hamel's eval-skills", "Braintrust's anatomy of a trace", "Gang of Four", "Cadence at Uber") with no link
- A capability claim about a product or system ("particularly well suited for long-running stateful workflows") without architectural justification

For each material claim, ask:
- Is there a citation, source, or basis for this claim?
- If it's our opinion/perspective, is it framed as such?
- Could this claim be challenged or disproven?

**First-person framing is substantiation-positive.** When a paragraph contains material claims AND has zero first-person markers (`I`, `we`, `our`, "from our experience", "in our view", "based on work with our portfolio companies"), the paragraph reads as anonymous reportage and is harder to substantiate. Either add a citation or reframe with first-person hedging — both lower compliance risk.

Transform examples:
- Bad: "Companies invest considerable effort in web scraping" → Good: "From what we understand, companies invest considerable effort in web scraping (subject to further diligence)"
- Bad: "The combined entity will have more access to web data than almost any other company" → Good: "We believe the combined entity could have significant access to web data"
- Bad: "Distributed systems have dealt with this for decades" → Good: cite, or remove the sentence
- Bad: "as Cornelia Davis argues, durable workflows are a primitive" → Good: "as Cornelia Davis argues *(link)*, durable workflows are a primitive"

---

### Category D: Fair and Balanced Presentation

Flag content that:
- Presents benefits without noting limitations or risks
- Uses overly optimistic scenarios without acknowledging challenges
- Omits material considerations affecting the reader's understanding
- Presents a one-sided view of a competitive landscape

**ADVERTORIAL DRIFT** — Flag and revise

Two specific shapes that violate fair-and-balanced presentation by tilting toward marketing copy:

- **Single-product praise without category framing.** Two or more consecutive sentences naming and praising one product without naming alternatives or establishing the category the product sits in. Reviewers describe this as the post reading "like an ad" or "like a testimonial".
  - Bad: extended praise of one vector database with cost numbers and architecture details, no mention of alternatives or category
  - Good: establish the category first ("the tradeoff space for managed vector storage at >10TB scale is X, Y, Z"), then introduce specific products as examples within that category
- **Investor-positioning phrases in body text.** Phrases like "Why Georgian Invested in [Company]" or "[Company] is industry-leading" anchored in the body rather than the footnote.
  - Bad: caption in the post body reads "Why Georgian Invested in Sublime Security"
  - Good: move the link to a footnote; the body captures the technical content of the collaboration

Transform example (one-sided):
- Bad: "This approach eliminates the need for dedicated teams"
- Good: "This approach could reduce the need for dedicated teams, though implementation complexity and reliability considerations remain"

---

### Category E: Illustrative Examples and Scenarios

Flag and revise:
- Speculative scenarios starting with "Imagine..."
- Hypothetical scenarios that are unrealistically favorable
- Detailed fictional use cases presented as typical

Transform examples:
- Bad: "Imagine an e-commerce business that wants to know who else is selling similar 'Band Tees'..."
- Good: "For example, e-commerce businesses may require additional data points about competitor pricing. To obtain that information..."

---

### Category F: Clarity and Precision

Flag and revise:
- Long, complex sentences with multiple clauses
- Tangential examples that dilute the core message
- Repetitive information across paragraphs
- Vague language that could be misinterpreted

Guidelines:
- Break complex ideas into shorter, readable sentences
- Focus on concrete, realistic applications
- Summarise points succinctly; avoid repetition
- Be direct and concise

---

### Category G: Disclosure and Attribution

**PORTFOLIO COMPANY DISCLOSURE** — Hard constraint. Flag every body-text mention.

Every mention of a Georgian portfolio company in the body of the post must carry a disclosure marker (typically `*` or a numbered footnote) and a corresponding footnote: *"[Company] is a Georgian portfolio company."*

- Bad: `Sublime has multiple ways to prevent malicious emails…` (no marker, no footnote)
- Good: `Sublime Security* has multiple ways to prevent malicious emails…` (with `* Sublime Security is a Georgian portfolio company` in the footer)
- Rationale: Georgian disclosure policy. Reviewers (especially compliance) flag this consistently. A missing disclosure is a compliance failure, not a stylistic issue.

**How to apply:**

1. Identify every named company in the body text.
2. Fetch https://georgian.io/portfolio and extract the canonical list of portfolio company names. This is the authoritative source — do not ask the author to confirm portfolio status when the page is reachable.
3. For each named company in the post, check it against that list. Match liberally — common short forms ("Sublime") should match full names ("Sublime Security"). When the match is genuinely ambiguous, flag for the author to confirm.
4. For each match, flag the mention as needing disclosure and propose the `*` marker and footnote text inline.
5. If the fetch fails, fall back to asking the author per company and note the fetch failure in the audit output so it is not mistaken for a clean pass.

**Footnote formatting** — Mention can use `*`, `**`, numbered footnotes, or any consistent convention; what matters is that the reader can find the disclosure within the post.

**Coauthor and collaborator attribution** — When a post is co-written with a portfolio company author or names contributors, the same disclosure rule applies to each named portfolio-company affiliation. 

---

### Category H: Further Reading Section

**FURTHER READING SECTION** — Required at the end of every post.

Every post must end with a curated reading list that gives the reader next steps and provides a permanent home for the external references behind the claims in the body.

**Required structure:**
- Section heading: `Additional Reading` or `Further Reading`
- A one-sentence intro framing the list
- One or more grouped subsections named for the post (e.g. `Historical Precedents`, `Companies Referenced`, `Further Reading`). Groupings should adapt to the content — the goal is that a reader scanning the list can pick the most relevant link, not that every post share the same headers.
- Each entry should include: linked title, author or organization, year where applicable and a short parenthetical noting why it's worth reading.

**Template:**
```markdown
## Additional Reading

If you're interested in this topic, here is a list of readings I find interesting on the topic.

### Historical Precedents
- [name](URL) — authors

### Companies Referenced
- [name](URL)

### Further Reading
- [title](URL) — source, date, etc
```

**Rationale:** The Further Reading section signals the author has surveyed the surrounding literature and gives the post's citations (see Category C) a stable home rather than scattering them inline only. Posts that lack one read as opinion divorced from the field.

**How to apply:**
1. Check for a section titled `Additional Reading`, `Further Reading`, `References` or similar at the end of the post.
2. If absent, flag as a hard issue and refuse to mark the post publish-ready.
3. If present, verify every entry has a working link plus author/org and a short context line. Entries that are bare URLs without context should be flagged for enrichment.
4. Cross-check against Category C: every named external concept, study, paper or framework cited inline should also appear here so the reader can locate the source.
5. Cross-check against Category G: portfolio companies named in the body that have a public primary source (product page, post, repo) should appear under a `Companies Referenced` group when the author is positioning them as an example.

---

## Output Format

Three parts, in this order: a readiness line, findings grouped by category, and a short action summary that references finding numbers only. **Do not produce a full-post tracked-changes rewrite.** The findings list IS the tracked changes — one entry per change, each independently acceptable. The author should be able to skim category headings, jump to occurrences they want to act on, and copy-paste each suggested text.

### 1. Readiness line

A single sentence: ready to publish, or not, and the count of blockers / high / medium / low findings. Example:

> Not ready — 3 blockers (2 missing portfolio disclosures, no Further Reading section), 5 high, 4 medium, 2 low. Resolve blockers before publishing.

**Severity scale:**
- **Blocker** — compliance failure that must be fixed before publish (missing portfolio disclosure, missing Further Reading section, unsubstantiated material claim, absolute future-prediction without hedging, advertorial drift).
- **High** — clear violation of a core principle (superlative, absolute claim, unhedged prediction, missing citation on a named-person attribution or numerical claim, Oxford comma).
- **Medium** — worth fixing this pass (extreme qualifier, puffery, one-sided framing, vague language).
- **Low** — minor polish (sentence-length cleanup, minor repetition).

### 2. Findings

Group by category. Only include categories that have at least one finding. Order categories by the highest severity of their findings (Blocker → High → Medium → Low), breaking ties alphabetically by category letter. Within a category, sort findings by severity descending, then in document order.

Number findings globally across categories (so #1 may be in Category G, #2 in Category H, #3 in Category A, etc.) — the action summary at the end references these numbers.

Each category section opens with two short framing lines — *What this is* and *Why this matters* — that explain the category once for the whole section. Then list every occurrence as its own finding block. **One block per individual occurrence — never aggregate.** If five superlatives appear in the post, produce five blocks. If the Oxford comma fires twelve times, produce twelve blocks. Each block must point at exactly one location the author can act on.

**Category section template:**

```
## Category {letter} — {name}

*What this is:* {one sentence describing what the category covers}
*Why this matters:* {one sentence on the compliance or style stakes — the principle this category protects}

**Finding {N}** [{Severity}]
- **Where:** {section/anchor} — "{~15 words of surrounding context, verbatim}"
- **Current:** "{verbatim from the draft}"
- **Suggestion:** "{verbatim replacement the author can copy-paste}"
- **Rationale:** {one sentence — what specifically is wrong with this occurrence}

**Finding {N+1}** [{Severity}]
- ...
```

**Location format — must be precise enough to act on without re-reading the post:**
- Body edits: section heading + paragraph number + a short verbatim anchor phrase from the sentence (e.g. `§"Why this matters", para 3 — "...engineers, researchers, and CTOs..."`). The anchor phrase is what the author searches for to find the spot.
- End-of-post or structural: `(end of post)` for missing Further Reading; `(document-wide)` only for genuinely structural findings.

**Category-specific additions:**

- **Category G (Portfolio disclosure):** include both the inline marker for the body AND the exact footnote text to add at the bottom of the post.
  ```
  - **Inline marker:** "Sublime Security*" (replace "Sublime")
  - **Footnote to add:** "* Sublime Security is a Georgian portfolio company."
  ```
- **Category H (Further Reading):** if the section is missing entirely, provide a starter scaffold using the template, pre-populated with the inline citations already present in the body.
- **Category C (Substantiation):** when a citation is needed but unknown, write `Suggestion: "{verbatim text} *(citation needed — {what to cite})*"` rather than guessing a source.

### 3. Action summary

Three lists at the very end, referencing finding numbers only — no re-prose:

- **Blockers (must fix before publish):** #1, #2
- **Recommended:** #3, #4, #6, #7
- **Optional:** #5, #8

Err on the side of flagging more issues rather than fewer.
