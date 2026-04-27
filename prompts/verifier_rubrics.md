# Autobloggy Verifier Rubrics

This file is the single source of truth for what "good" looks like. It is shipped to:

1. The writer LLM at `generate-draft` time, so the v0 draft satisfies these rubrics from the start.
2. The `autobloggy-verifier` sub-agent each iteration of the draft loop, so it can decide where to insert `<!-- fb[rule_id]: rationale -->` markers.

The verifier inserts a marker per offending location; the fix pass removes the marker as part of resolving the issue. Empty-check is `grep -c '<!-- fb\['` over `draft.html` returning 0.

---

## How to insert markers

- Format: `<!-- fb[rule_id]: short rationale -->`
- Inline span issue: place the comment immediately after the offending span (inside the same parent element).
- Heading issue: place the comment inside the heading element, just before the closing tag.
- Document-level finding without a natural anchor: place at the top of `<main>`, before the first child.
- Visual issue: place the comment next to the offending visual node (`<svg>`, `<canvas>`, `<img>`, `<figure>`).
- Use only the `rule_id` values defined below. One marker per offense — do not stack duplicates on the same span.
- Special markers:
  - `<!-- fb[needs_visual]: hint -->` — a section would benefit from a visual the writer didn't include. The fix pass authors the visual inline.
  - `<!-- fb[document]: rationale -->` — for whole-document findings without a natural anchor.

---

## Programmatic rules (inserted by Python before the LLM verifier runs)

These already arrive in the draft when the verifier reads it. Do not re-mark the same offenses; you may add semantic context if useful but the programmatic insertions are authoritative.

| `rule_id` | What it flags |
|-----------|---------------|
| `one_h1` | More than one H1 inside `<main>`. |
| `heading_order` | Heading level jumps by more than one (e.g. H2 → H4). |
| `code_fences_tagged` | `<pre><code>` blocks missing a `language-*` class. |
| `image_caption_alt` | `<img>` missing meaningful `alt`, or `<figure>` missing `<figcaption>`. |

---

## LLM-judged prose rules

Apply each rule to the whole draft inside `<main>`. Insert one marker per offense at the closest anchor.

### `presentable_headings`

Pass: every `<h2>`/`<h3>` inside `<main>` reads as a publishable, reader-facing section title.
Fail: a heading is a planning label like "Hook", "Opening", "Context", "Implications", "Closing", "Body section 1", etc. Mark the offending heading.

### `intro_exists`

Pass: the first paragraph of `<main>` (after the H1) introduces the post's thesis or core question in plain language.
Fail: the post jumps straight into a section, restates the title, or warms up with industry-overview boilerplate. Mark with `fb[document]` at the top of `<main>` if there is no natural span; otherwise mark the first paragraph.

### `conclusion_exists`

Pass: the post ends with a clear synthesis, takeaway, or decision rule that does more than restate the intro.
Fail: post ends mid-section, ends with restatement, or has no closing thought. Mark on the final heading or as `fb[document]`.

### `opening_clarity`

Pass: the opening (first 3 sentences inside `<main>`) names the problem or conclusion.
Fail: opening is a definition the reader knows, an industry overview, or a vague throat-clear. Mark on the first paragraph.

### `paragraph_focus`

Pass: each paragraph carries one main idea.
Fail: paragraph runs together two unrelated ideas, or buries the lede. Mark on the offending `<p>`.

### `voice`

Pass: prose sounds like a sharp practitioner. Specific, grounded, opinionated when the material earns it.
Fail: company-speak ("we are excited to announce"), generic assistant phrasing ("it's worth noting", "in conclusion", "let's dive in"), or marketing polish without substance. Mark the offending span.

### `overstatement`

Pass: claims about capability, certainty, speed, or impact are scoped to what the source supports.
Fail: words like "revolutionary", "seamlessly", "10x", "always", "never" without a number or mechanism behind them. Mark the offending span.

### `specificity`

Pass: vague verbs replaced with concrete examples, numbers, or timeframes where the section is making a substantive claim.
Fail: "leverages", "drives", "enables" with no mechanism or example downstream. Mark the offending sentence.

### `so_what`

Pass: each paragraph answers the reader's "so what?" within itself or in the next paragraph.
Fail: a paragraph describes a thing without naming consequence, decision, or action. Mark the paragraph.

### `filler_hype`

Pass: no filler transitions, empty intensifiers, or hype words.
Fail: "Now that we've covered X, let's turn to Y", "very", "extremely", "truly", "world-class", "best-in-class". Mark the span.

### `portfolio_company_disclosure`

Pass: portfolio company logos / names either don't appear, or appear with the disclosure language from the brand guide.
Fail: portfolio company name or logo present without disclosure. Mark with `fb[document]`.

### `research_citation`

Pass: every claim backed by research, data, analysis, case studies, or metrics has a linked source (inline link, footnote with URL, or full citation with URL). Naming an organization without a link does not count.
Fail: a research-backed claim has no link. Mark the span.

### `performance_metrics_disclosure`

Pass: no portfolio performance metrics or forward-looking statements present.
Fail: such metrics or statements appear and would need Marketing sign-off. Mark with `fb[document]`.

---

## LLM-judged visual rules (apply to inline `<svg>`, `<canvas>+<script>`, `<img>`, `<figure>`)

These are evaluated against the whole-page screenshots at 360 px / 768 px / 1280 px shipped in the verify-pack.

### `visual_relevance`

Pass: the visual's main idea matches the surrounding section's core claim.
Fail: visual answers a different question, introduces a competing takeaway, or feels generic. Mark on the visual node.

### `text_visual_alignment`

Pass: visual labels, numbers, sequence, and framing match the surrounding prose.
Fail: visual contradicts, overstates, or introduces unsupported specificity. Mark on the visual node.

### `source_attribution`

Pass: factual or data-backed visuals have a `<figcaption>` or visible source note.
Fail: visual derives from a source but omits a caption, note, or source cue. Mark on the visual node.

### `layout_integrity`

Pass: at every screenshot width, all text is fully visible — no clipping, no horizontal page scroll, no overflow.
Fail: at any width, text or content is clipped, truncated, or runs off the right edge. Mark on the offending visual or as `fb[document]` for layout-of-the-whole-post issues.

### `brand_consistency`

Pass: visuals use only the brand colour tokens and font stacks defined in the preset's brand guide.
Fail: off-brand colours, fonts, or decorative treatment. Mark on the visual node.

### `composition_clarity`

Pass: at every width, layout has clear hierarchy, readable spacing, and an obvious focal point. Narrow view is a genuine re-composition (stacked cards, simplified chart) — not a shrunken desktop.
Fail: cluttered, unbalanced, microscopic type at narrow widths, horizontally-scrolling wide tables. Mark on the visual node.

### `alt_text_quality`

Pass: each `<img>` / `<svg>` carries an `alt` or `aria-label` describing the informational purpose.
Fail: missing, empty, vague, or decorative-only labelling for substantive visuals. Mark on the visual node.

### `needs_visual`

Insert `<!-- fb[needs_visual]: <hint> -->` when a section's argument would land harder with an inline visual the writer didn't provide. Hint should describe the visual concretely (pattern, what to compare, what to label). The fix pass authors the visual inline using the brand tokens already declared in the draft's `<head>`.

---

## Stop condition

The fix pass MUST reduce marker count to zero. Verify with:

```bash
grep -c '<!-- fb\[' posts/<slug>/draft.html
```

When this returns `0` and the next `autobloggy verify` run inserts no new markers, the loop is done.
