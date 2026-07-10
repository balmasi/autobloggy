---
name: substack-seo-geo
description: Pre-review SEO/AEO/GEO and editorial-polish audit of a single Substack post draft. Use during the drafting phase, before requesting human reviewers, to optimize in-post discoverability levers (SEO title, SEO description, headings, keyword targeting, image alt text, internal links) and catch surface defects (vague referents, AI cadence, undefined acronyms, unfinished TBD/TODO markers). Trigger on phrases like "SEO check this draft", "AEO check", "GEO check", "editorial polish check", "polish this draft for review", "self-review my post", "is this draft ready for human review", "audit this draft for SEO", "pre-review audit". For SEC-Marketing-Rule and Georgian-voice compliance review of post content, see substack-compliance. Publication-level discovery and growth audits are out of scope.
---

# Substack SEO and GEO

Self-review tool for a single Substack post draft. Audits in-post craft, AEO/GEO readiness, content quality and editorial polish. Feed it a draft and it flags gaps with concrete fixes — to be run before requesting human reviewers.

Target publication: https://georgianailab.substack.com/

---

## Before You Audit

**Do not interrogate the author with a checklist of clarifying questions.** Infer everything you reasonably can from the draft and the request. Defaults:

- **Scope:** full draft audit across all four priority areas (polish, on-page, content quality, AEO/GEO).
- **Fix mode:** draft the suggested replacement text in each finding so the author can copy-paste — do not just flag.
- **Primary keyword:** infer from the headline, subtitle, H2s and first paragraph. If genuinely ambiguous after reading, name your best inference in the readiness line ("audited against inferred primary keyword: *X* — flag if wrong") and proceed. Do not block on this.
- **Draft stage:** assume pre-review-handoff (the typical trigger for running this skill). The findings are the same regardless of stage.
- **Series context:** infer from internal links and any explicit "part N of" framing. If absent, audit the post as a standalone.

**Only ask the author a question when you literally cannot proceed** — e.g. no draft was attached, or the request references a draft you cannot access. In that case, ask the one specific question that unblocks you, not a list.

**Note for the author:** run `substack-compliance` *after* this skill, not before — polish first, then compliance.

---

## Audit Framework — Priority Order

Four priorities, ordered cheapest-to-fix first. Run them in this order; each one assumes the previous one has been resolved.

### 1. Editorial polish

**What:** Pre-publish mechanical checks — vague referents (`this`/`it`/`they` with unclear antecedents), AI cadence patterns, undefined acronyms, unfinished markers (TBD/TODO), concept-used-before-defined.

**Why it matters:** Polish defects are the most common reviewer comments on internal drafts. Catching them mechanically *before* requesting reviewers means human review can focus on substance, not surface. They are also the cheapest defects to fix — most are single-word or single-sentence edits.

**Source:** Patterns derived from internal-review comment corpus across the Georgian R&D Substack drafts (vague pronouns, AI cadences, jargon, leftover TBDs were the four highest-volume reviewer flags).

### 2. On-page craft

**What:** SEO Title, SEO Description, heading structure, image alt text, internal linking, keyword targeting — the writer-facing levers Substack actually exposes during drafting.

**Why it matters:** These are the controls that determine whether a post is findable in search and whether the SERP click-through is high enough to convert visibility into reads. They are post-specific and have to be set per-draft.

**Source:** Verified against Substack's published post-settings documentation (SEO Title and SEO Description override fields under *Post Settings → SEO*) and standard on-page SEO guidance.

### 3. Content quality

**What:** E-E-A-T signals (Experience, Expertise, Authoritativeness, Trustworthiness), content depth, originality.

**Why it matters:** Hardest to fix mechanically and the slowest-moving lever, but it determines what reviewers and search engines both reward over time. A polished post on a thin idea will not rank or recirculate.

**Source:** Google Search Quality Rater Guidelines (E-E-A-T framework).

### 4. AEO/GEO readiness

**What:** Answer-engine and AI-citation patterns — content shaped so it can be quoted by ChatGPT, Perplexity, Google AI Overviews and similar.

**Why it matters:** AI answer engines are an increasing share of how readers reach long-form technical content. A post that AI engines can extract cleanly (self-contained definitions, named entities, structured claims) gets cited; one that requires context to interpret does not.

**Source:** [`references/aeo-geo-patterns.md`](references/aeo-geo-patterns.md).

---

Editorial polish comes first because surface defects are cheapest to fix and they make the rest of the audit cleaner. On-page craft comes next because it's the per-post layer the author still controls. Content quality and AEO/GEO readiness sit further out because they require structural decisions made earlier in drafting.

---

## On-Page Craft (within a Substack post)

The writer-facing levers Substack actually exposes during drafting. Each subsection below follows the same shape: the Substack mechanic in plain language, then what to audit, then why it matters, then common failure modes.

### SEO Title

**Substack mechanic:** Substack auto-fills the SEO title from the post headline. The writer can override that auto-fill in *Post Settings → SEO* (the "SEO Title" field). The override is what Google shows in search results — the in-publication headline can stay punchy while the SEO title carries the keyword.

**Audit the effective SERP title** — that is the override if one is set, otherwise the headline. Only flag a finding if the effective title fails one of these criteria; do not flag "no override set" as a standalone finding when the headline itself is already serviceable.

- Length: target ~45–50 characters (under ~475 pixels) to display cleanly on **mobile** Google SERPs, and definitely under ~60 characters (~580 pixels) for **desktop**. Google measures by pixel width, not character count, at a ~600px desktop container and a ~500px mobile container. Mobile is the tighter single-line constraint: above ~475px mobile wraps to a second line (up to ~650px before truncating). Desktop truncation starts around ~580px. Bolded keywords add ~15–20% pixel width, so the cutoff lands earlier when the searcher's query matches words in the title. Letter widths vary — "W", "M", "Q" eat space; "i", "l", "t" fit more. Sources: [Screaming Frog page-title pixel-width analysis](https://www.screamingfrog.co.uk/blog/page-title-meta-description-lengths-by-pixel-width/) (empirical data showing shortest truncated title at 61 chars / 432px, longest non-truncated at 74 chars / 506px); [Search Engine Land — title tag length 2025](https://searchengineland.com/title-tag-length-388468). Substack readers skew mobile, so optimize for the mobile threshold and you cover desktop automatically.
- Primary keyword positioned early
- Brand / publication name at the end if space allows
- Not keyword-stuffed (Google may rewrite)

When the effective title fails, the suggested fix is either to revise the headline or to set a `Post Settings → SEO Title` override — call out both options in the Findings block and let the author choose.

**Why it matters:** The SEO title is what determines whether a post shows up for a given search query and how compelling the SERP listing reads. A clever in-publication headline that doesn't include the search term will under-rank. A title that exceeds ~475px on mobile (~45–50 chars) wraps to a second line; one that exceeds ~580px on desktop (~50–60 chars) truncates with an ellipsis, so the reader sees half a sentence. Substack traffic is mobile-heavy — optimizing for the mobile threshold covers both surfaces.

### SEO Description

**Substack mechanic:** Substack uses the post subtitle as the SEO description by default. The writer can override that fallback in *Post Settings → SEO* (the "SEO Description" field) — useful when the subtitle is poetic, vague or written for in-publication tone rather than for search click-through.

**Audit the effective SERP description** — that is the override if one is set, otherwise the subtitle. Only flag a finding if the effective description fails one of these criteria; do not flag "no override set" as a standalone finding when the subtitle itself is already serviceable for SERP use.

- Length 150–160 characters (under 100 is too thin; over 160 truncates)
- Includes the primary keyword
- Carries a clear value proposition for a search reader (not just in-publication tone)

When the effective description fails, the suggested fix is either to revise the subtitle or to set a `Post Settings → SEO Description` override — call out both options in the Findings block and let the author choose. A poetic or vague subtitle is the most common reason to introduce an override.

**Why it matters:** The SEO description is what appears under the title in search results. It's the reader's first read of the post and it determines click-through rate. A subtitle written for the publication doesn't usually serve the same job — search readers need a value proposition, in-publication readers already chose to be there.

### Heading Structure

**Substack mechanic:** Substack renders the post title as H1 automatically — the writer doesn't manually mark it. Inside the post body, the writer chooses H2 and H3 from the editor toolbar. Markdown `##` syntax also produces an H2 if the writer pastes from a markdown source.

**Audit:** Is the body hierarchy clean?

- One H1 only — Substack handles this; the writer should not insert another
- Logical H2 → H3 nesting in the body
- Headings describe content, not styling
- Primary keyword in at least one H2 where natural

**Why it matters:** Search engines and answer engines both use heading hierarchy to understand the document's structure. Skipped levels (H2 → H4) and headings used as styled bold text both confuse extraction. Inside Substack, headings also drive the in-app table of contents on mobile.

**Common issues:**
- Multiple H1s (writer manually adding a second one)
- H2 → H4 skips
- Headings used purely for styling
- Primary keyword absent from every H2

### Content Optimization

**Substack mechanic:** No Substack-specific UI here — this is about how the body of the post is written. Substack does not surface keyword density or readability metrics; the writer makes these calls directly.

**Audit:** Does the body match the search intent it's targeting?

- Primary keyword appears in the first 100 words
- Related keywords used naturally throughout
- Sufficient depth for the topic — comprehensive enough to answer the reader's question
- Answers the reader's actual search intent (not an adjacent question)
- Better than the top-ranking competitor for the same query

**Why it matters:** Search engines now reward depth and intent-match more than keyword density. A post that ranks for a query needs to be the best answer to that query, not just one answer among many. The first 100 words are weighted heavily because they signal what the post is actually about.

**Thin-content flags:**
- Posts with little unique perspective beyond what an LLM would generate
- Restated paper summaries with no original insight
- Notes-length ideas stretched into long-form

### Image Optimization

**Substack mechanic:** Substack's image editor exposes an alt-text field on every uploaded image. There is no separate caption-vs-alt distinction for SEO purposes — alt text is what screen readers and search engines see.

**Audit:** Are images carrying their share of the work?

- Alt text on every image, describing the image (not the post)
- Descriptive file names before upload (Substack preserves the upload filename)
- Reasonable file sizes (large images slow the in-app reading experience)
- Diagrams and screenshots used wherever a quantitative claim could be visualized

**Why it matters:** Alt text serves accessibility, search image indexing and AI extractability all at once. A diagram with no alt text is opaque to half the audience and to every answer engine.

**Common issues:**
- Alt text missing or auto-set to "image"
- Filename like `Screenshot 2024-03-12 at 11.34.png`
- Image larger than 500KB without a reason

### Internal Linking

**Substack mechanic:** Substack supports inline hyperlinks via the editor's link button and via markdown paste. Links to other posts in the same publication and to recommended publications both render as native rich previews if the writer pastes the URL on its own line.

**Audit:** Is the post connected to the rest of the publication and the rest of the topic?

- Links from this post to relevant past posts in the same publication
- Links to recommended publications where natural
- Descriptive anchor text, not "click here"
- No broken internal links

**Why it matters:** Internal linking is how a publication accumulates topical authority over time. A post that lives in isolation contributes less to ranking than the same post linked from and to related posts. Descriptive anchor text also tells search engines what the linked post is about.

**Common issues:**
- New post that doesn't link to any prior post in the publication
- Generic anchor text ("here", "this article")
- Broken link to an unpublished or moved post

### Keyword Targeting

**Substack mechanic:** Substack does not provide a keyword-management UI. Tracking the keyword map across posts is the author's responsibility, typically maintained outside Substack (a doc, a spreadsheet, or in `references/aeo-geo-patterns.md`).

**Audit (per post):**
- Clear primary keyword chosen for this draft
- SEO Title, H1 and body content aligned to that keyword
- Not competing with another post in the same publication for the same query (cannibalization)

**Audit (across the publication):**
- A keyword map exists somewhere outside Substack
- Logical topical clusters that match the publication theme
- No major coverage gaps in the topic the publication claims

**Why it matters:** Two posts targeting the same query will split traffic and confuse search engines about which to rank — this is keyword cannibalization. A clear primary keyword per post and a publication-wide map prevents that.

**Common issues:**
- Same keyword targeted by two different posts unintentionally
- Primary keyword present in title but absent from body
- No site-wide map, so cannibalization is invisible until traffic suffers

### Author Bio and Acknowledgements (end-of-post)

**Substack mechanic:** Substack does not enforce an author bio at the bottom of posts — it surfaces the author byline at the top, and that's it. End-of-post bios and acknowledgements are written into the post body itself by convention.

**Audit:** Is the bio + acknowledgements block present at the end of the post?

- A short author bio paragraph: name, role, organization, what they work on, and series context if applicable
- An acknowledgements paragraph naming the reviewers who gave thoughtful feedback on the piece
- Both sit at the very end, after the main content

**Why it matters:** The bio reinforces E-E-A-T signals (Experience, Expertise, Authoritativeness) — it tells the reader who is making the claims and why their perspective is credible. The acknowledgements section recognises reviewers who improved the post and reinforces that the work was peer-reviewed before publishing. Both also strengthen human-trust signal in an environment where many posts are AI-generated.

**Template (Georgian R&D Substack convention):**

```
{Author Name} is {Role} at Georgian, where {one-sentence description of what they work on}. {Optional: This is part {N} of the "{Series Name}" series.}

Grateful to {Reviewer 1}, {Reviewer 2}, {Reviewer 3} and {Reviewer 4} for their thoughtful feedback on this piece.
```

**Example:**

> Asna Shafiq is AI Technical Lead at Georgian, where she works on evaluation infrastructure and agentic AI systems for growth-stage portfolio companies. This is part 1 of the "Evals for AI Systems" series.
>
> Grateful to Frederik Dudzik, Kshitij Jain, Nima Vahdat and David Poole for their thoughtful feedback on this piece.

**Common issues:**
- Bio missing entirely
- Acknowledgements missing or left as a `TODO` placeholder (the editorial-polish unfinished-marker check should also catch this)
- Oxford comma in the reviewer list — Georgian style prohibits the serial comma (compliance will flag, but easier to catch here)
- Reviewer at a Georgian portfolio company named without disclosure — flag for compliance to handle

---

## Editorial Polish (pre-publish craft checks)

These are the mechanical editorial checks reviewers consistently flag on internal review. They are not regulatory (compliance handles that) and not algorithmic. They are the surface defects that erode reader trust and make the post read as AI-generated. 

### 1. Ambiguous referents

**Audit:** Scan every `this`, `that`, `it`, `they`, `these`, `those` and every thinly-specified noun phrase ("the engine", "this problem", "the entire thing", "everything"). For each, ask: does the immediately preceding sentence (or independent clause within the same sentence) contain an unambiguous singular antecedent?

**Why it matters:** Vague pronouns are the single most common reviewer comment on internal drafts. The reader cannot tell what the word is pointing at, and the sentence underdelivers.

**Agent assist:** For each flagged token, propose the concrete noun phrase to substitute, drawn from the surrounding context.

### 2. AI cadence patterns

**Audit:** Match against a closed list of cadence patterns that signal AI-generated prose:

- "stops being optional" / "isn't optional"
- "earns its keep"
- "exactly the trap"
- "isn't X — it's Y" / "isn't bad luck — it's Y"
- "not just X — Y" / "not X — Y" used for rhetorical pivot rather than information
- "not edge cases — they're routine"
- "isn't a luxury"
- "X means Y. A retry means Z." (parallel-structure filler)
- The em dash overuse pattern documented in `references/ai-writing-detection.md`

**Why it matters:** A post that reads as AI-generated loses human-trust signal regardless of how good the substance is. Reviewers flag these phrasings repeatedly with notes like "ai-generated vibe", "feels quite ai-generated", "i dont like this language. its so AI-written".

**Agent assist:** Flag each match. Suggest deletion or replacement in the author's own voice. Do **not** auto-rewrite — these patterns are sometimes valid when the contrast lands; the author decides.

**Reference:** [`references/ai-writing-detection.md`](references/ai-writing-detection.md) for the full pattern list including em-dash overuse and other research-backed AI tells.

### 3. Undefined acronyms and jargon

**Audit:** On first appearance, flag every all-caps token of length 2–5 letters (RBAC, HBM, IaC, DSL, MQL, KV, GPU). Also flag named-concept jargon used without context (Builder pattern, Gang of Four, Terraform, Cadence). For each: is the term expanded or contextualized on first use?

**Why it matters:** Reader comprehension and AEO/GEO extractability both benefit from self-contained definitions. An acronym that requires the reader to already know it locks out part of the audience.

**Agent assist:** Flag the first use only. Prompt the author: "Define on first use? Audience may already know this." Author decides — sophisticated audiences don't need every term expanded; novices do.

### 4. Unfinished markers

**Audit:** Mechanical scan for any of:
- `TBD`, `TODO`, `[INSERT...]`, `[TKTK]`
- HTML/markdown placeholder syntax (`<TBD ...>`, `<...>`)
- Emoji markers used as TODO flags (`❗`, `⚠️` followed by author name)
- Lone parenthetical numbers `(1)`, `(2)`, `(3)` that aren't part of a list

**Why it matters:** These should never reach publication. They appear in drafts because the author intended to revisit a section and forgot.

**Agent assist:** Flag every match, no exceptions. Refuse to mark the post publish-ready until each is resolved.

### 5. Concept used before defined (experimental)

**Audit:** Parse all defined concepts in the doc — heading text, bolded terms, terms in quotes — and flag any usage of those concepts that occurs *before* their definition.

**Why it matters:** Reviewers consistently report "I had a hard time understanding this essay because order of things is confusing". A concept referenced before it's introduced forces the reader to backfill or skip ahead.

**Agent assist:** Mark each early-use as a candidate reorder. Higher false-positive rate than the other polish checks — author should sanity-check each flag rather than accept blindly.

---

## Content Quality

### E-E-A-T Signals

**Experience**
- First-hand experience demonstrated (built it, deployed it, debugged it)
- Original data, benchmarks or case studies
- Real examples, not hypothetical ones

**Expertise**
- Author credentials visible on the publication About page
- Accurate, detailed, technically precise
- Claims sourced

**Authoritativeness**
- Cited by other publications in the space
- Recognized within the AI/ML community
- Speaking, papers, prior work referenced

**Trustworthiness**
- Accurate information
- Transparent about affiliations and conflicts of interest
- Contact / About page complete

### Content Depth

- Comprehensive coverage of the topic
- Anticipates and answers follow-up questions
- Better than the top-ranking competitor or the most-read post on the same topic
- Updated when the topic moves (model releases, paper retractions, benchmark shifts)

### Engagement Signals (Substack-native)

Per-post metrics worth checking after publish to validate the audit's hypotheses:

- Open rate (email side)
- Read time / scroll depth (in-app side)
- Restacks per post
- Substantive replies per post
- Reply-to-like ratio
- Subscriber growth attributable to this post

---

## Output Format

Three parts, in this order: a one-line readiness verdict, numbered findings grouped by category with What/Why context up front, and a short action summary that references finding numbers only. **Do not produce a narrative report, a full-post rewrite, or a summary table.** The author should be able to skim category by category, understand why each finding matters, and copy-paste each suggested edit.

### 1. Readiness line

A single sentence: ready to hand to reviewers, or not, and the count of blockers / high / medium / low findings. Example:

> Not ready — 2 blockers, 4 high, 6 medium, 3 low. Resolve blockers and high before requesting reviewers.

### 2. Findings

**Group findings by category in this order — each category gets a header followed by a one-line description of what that category covers, so the author knows what kind of fix to expect.** Within each category, sort by severity (Blocker → High → Medium → Low). If a category has zero findings, omit it entirely.

```
### Editorial Polish
*The small wording stuff a human reviewer would circle in red pen — vague "this" or "it" with no clear subject, sentences that sound AI-written, jargon and acronyms used without explaining them, leftover TODOs or `[INSERT...]` placeholders. These are easy to fix and easy to miss on your own re-read.*

{findings here}

### On-Page Craft
*The Substack controls you set per post — SEO title, SEO description, headings, image alt text, internal links, and which keyword the post is targeting. These shape whether your post shows up when someone Googles the topic, and whether they click through once it does.*

{findings here}

### Content Quality
*First-hand experience, real depth, original perspective, and the credibility signals Google groups under E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness). The slowest lever to move, and the one that decides whether the post still gets read in six months.*

{findings here}

### AEO/GEO Readiness
*Whether AI tools — ChatGPT, Perplexity, Google's AI Overviews — can pull clean quotes from your post when someone asks them about the topic. They reward posts that define their terms in-place, structure claims clearly, and name people, companies and tools explicitly instead of leaving the reader to guess.*

{findings here}
```

**Each finding follows this block format** — numbered globally (1, 2, 3, ... across all categories). The category header explains what the category covers; the finding leads with **Why this matters** so the reader does not have to ask "why fix this":

```
**Finding {N} — {short check name}** [{Severity}]
- **Why this matters:** {one line — what breaks for the reader / search engine / answer engine if this is left as-is; cite a source if the rule has a sourced rationale, e.g. SERP pixel-width study}
- **Where:** {section/anchor or control name} — "{~15 words of surrounding context, verbatim}"
- **Issue:** {one sentence on the specific problem in this draft}
- **Current:** "{verbatim text from the draft, or `n/a` for structural findings}"
- **Suggested:** "{verbatim replacement the author can copy-paste, or a drafted version}"
```

For checks where the author needs to make a judgment call (AI cadence pattern that might land, undefined acronym in front of a sophisticated audience, concept-before-defined that may be intentional), present two options under **Suggested**:

```
- **Suggested:**
  - **Option A (keep):** {short rationale for leaving as-is}
  - **Option B (revise):** "{verbatim suggested rewrite}"
```

Do not auto-decide for the author on these.

**One finding per individual occurrence — never aggregate.** If the same check fires in five places (five vague pronouns, five missing alt texts), produce five findings. Each must point at exactly one location the author can act on.

**High-count exception:** if the *same* check fires more than 10 times (e.g. 30 missing image alt texts), collapse to one finding with severity + count in the heading (`Finding 7 — Missing alt text (×30)`), keep the `Why this matters` line once, and list every individual location under a single `Locations:` block (one bullet per occurrence with `Where` + `Current` + `Suggested`). Never collapse different checks into one finding.

**Severity scale:**
- **Blocker** — must fix before publish (unfinished markers, missing bio/acknowledgements, broken internal links).
- **High** — significant impact on discoverability or reader trust (missing SEO overrides, primary-keyword absent from H1/first 100 words, AI-cadence cluster, missing alt text on diagrams).
- **Medium** — worth fixing this pass (single AI cadence, undefined acronym, weak anchor text, missing internal link).
- **Low** — nice to have (image filename, second-pass polish).

**Location format — must be precise enough to act on without re-reading the post:**
- Body edits: section heading + paragraph number + a short verbatim anchor phrase from the sentence (e.g. `§"How retries work", para 2 — "...this is exactly the trap..."`). The anchor phrase is what the author searches for to find the spot.
- Substack controls: name the control (e.g. `Post Settings → SEO Title`, `image #3 (Q3 latency chart) alt text`).
- Whole-document checks: `(document-wide)` is only acceptable for genuinely structural findings (e.g. "no internal links anywhere"). For repeated in-text issues, use the high-count exception above instead.

### 3. Action summary

Three lists at the very end, referencing finding numbers only — no re-prose:

- **Blockers (must fix before publish):** #1, #7
- **Recommended this pass:** #2, #3, #5, #8
- **Optional / future:** #4, #6, #9

Err on the side of flagging more issues rather than fewer.

---

## References

- [AEO and GEO Patterns](references/aeo-geo-patterns.md): Content patterns optimized for answer engines and AI citation. Useful for posts that need to be quoted by ChatGPT, Perplexity or AI Overviews.
- [AI Writing Detection](references/ai-writing-detection.md): Common AI writing patterns to avoid (em dashes, overused phrases, filler words). A post that reads as AI-generated will lose human-trust signal regardless of how good the substance is.
