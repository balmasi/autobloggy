# Autobloggy Quality Criteria

This file defines reusable editorial and visual quality criteria for draft generation and verification. It intentionally does not define verifier marker mechanics.

## Prose Criteria

### `presentable_headings`

Every `<h2>` and `<h3>` inside `<main>` should read as a publishable, reader-facing section title. Planning labels such as "Hook", "Opening", "Context", "Implications", "Closing", or "Body section 1" fail.

### `intro_exists`

The first paragraph after the H1 should introduce the post's thesis or core question in plain language. The post should not jump straight into a section, restate the title, or warm up with industry-overview boilerplate.

### `conclusion_exists`

The post should end with a clear synthesis, takeaway, or decision rule that does more than restate the intro.

### `opening_clarity`

The opening three sentences should name the problem or conclusion. Avoid definitions the reader already knows, vague throat-clearing, and broad market overviews.

### `paragraph_focus`

Each paragraph should carry one main idea. Paragraphs fail when they run together unrelated ideas or bury the lede.

### `voice`

Prose should sound like a sharp practitioner: specific, grounded, and opinionated when the material earns it. Avoid company-speak, generic assistant phrasing, and marketing polish without substance.

### `overstatement`

Claims about capability, certainty, speed, or impact must be scoped to what the source supports. Words like "revolutionary", "seamlessly", "10x", "always", or "never" need evidence, a number, or a mechanism.

### `specificity`

Substantive claims should use concrete examples, numbers, mechanisms, or timeframes. Vague verbs such as "leverages", "drives", and "enables" fail when no mechanism follows.

### `so_what`

Each paragraph should answer the reader's "so what?" within itself or in the next paragraph by naming a consequence, decision, or action.

### `filler_hype`

Avoid filler transitions, empty intensifiers, and hype words such as "Now that we've covered X", "very", "extremely", "truly", "world-class", and "best-in-class".

### `portfolio_company_disclosure`

Portfolio company logos or names need the disclosure language required by the selected brand guide.

### `research_citation`

Every research-backed claim, data point, case study, or metric needs a linked source, footnote with URL, or full citation with URL. Naming an organization without a link is not enough.

### `performance_metrics_disclosure`

Portfolio performance metrics and forward-looking statements require the signoff path specified by the selected brand guide.

## Visual Criteria

### `visual_relevance`

Each visual's main idea should match the surrounding section's core claim.

### `text_visual_alignment`

Visual labels, numbers, sequence, and framing should match the surrounding prose. Visuals should not contradict, overstate, or introduce unsupported specificity.

### `source_attribution`

Factual or data-backed visuals should include a `<figcaption>` or visible source note.

### `layout_integrity`

At 360 px, 768 px, and 1280 px, all text and content should be visible with no clipping, truncation, horizontal page scroll, or right-edge overflow.

### `brand_consistency`

Visuals should use the brand color tokens and font stacks defined in the selected brand guide and HTML template.

### `composition_clarity`

Visual layouts should have clear hierarchy, readable spacing, and an obvious focal point. Narrow viewports need genuine recomposition, not a shrunken desktop.

### `alt_text_quality`

Each substantive `<img>` or `<svg>` should have `alt` or `aria-label` text that describes the informational purpose.

### `needs_visual`

Use a visual when a section's argument would land harder with a concrete comparison, framework, process, chart, or source-grounded exhibit.
