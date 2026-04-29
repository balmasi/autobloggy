# Writing Guide

The human canon for what counts as slop and how to fix it. Organized by category so new entries slot in cleanly. The detector (`scripts/patterns.yaml`) is a separate artifact; rules can live here without a YAML counterpart and vice versa.

These are defaults. User or publication preferences override.

---

## What slop is

> Slop is prose that feels mass-produced because it substitutes polish, balance, and generic significance for specific observation, accountable claims, and a recognizable point of view.

A human can write slop. A model can produce good prose. The reader's objection is rarely "a model wrote this" — it is "this is generic filler that wasted my time." Optimize for being worth reading, not for being undetectable.

Key signal is *posture* — safe, symmetrical, abstract, over-explanatory writing that avoids specific risk.

---

## Cluster, don't convict

A single tell is not proof. Treat findings by tier and escalate when families combine.

**Tier 1 — high confidence (act on a single hit):**
process artifacts (`turn0search0`, `oaicite`, `utm_source=chatgpt`), assistant voice leakage (`as an AI language model`, `knowledge cutoff`), fake or broken citations.

**Tier 2 — paragraph signal (act when present):**
balanced-contrast family, superficial analysis tags, vague authority, brochure voice, dense buzzword clusters.

**Tier 3 — style signal (act only in clusters):**
em dashes, rule of three, smooth transitions, tidy conclusions, abstractness with no image, polished grammar alone.

**Escalate** when 4+ Tier-2/3 hits land in one paragraph, or when 2+ distinct families appear together. A single em dash, a single triad, a single buzzword — none of these are slop on their own.

**Never treat as standalone proof:** em dashes, rule of three, a single vocabulary word, polished grammar, title-case headings.

---

## 1. Prevention Rules

Apply while drafting. These prevent most slop before detection is needed.

- Lead with substance, not setup about the piece itself. (A scene, anecdote, or claim all qualify; "this article will explore..." does not.)
- Name the actor, object, metric, tool, place, or tradeoff.
- Prefer concrete nouns and verbs over impressive adjectives.
- Use active voice unless the actor is genuinely unknown or irrelevant.
- Vary sentence and paragraph length.
- Put the reader in the situation when that helps. Avoid narrator distance.
- Take a hard stance. Hedged answers ("it depends on context", "a balanced approach") are slop's natural mode.
- Make the reader picture something. If a paragraph contains no person, object, place, number, or quote, rewrite it.
- Avoid em dashes by default. Keep them only when the user or publication style explicitly asks to retain them.

---

## 2. Throat-Clearing & Meta-Talk

Prose about the prose. Cut, don't rephrase. Most are long-form-specific (articles, essays, reports) and fire less in social or product copy.

- `in this article`, `this post will`, `we will explore`, `we will discuss`
- `it is important to note`, `it is worth mentioning`, `it is crucial to recognize`
- `no discussion would be complete without`
- `in summary`, `in conclusion`, `overall`, `ultimately`, `all in all`
- `without further ado`, `when it comes to`
- Stock openers about the age: `in today's fast-paced world`, `in a world where`, `as businesses increasingly`

**Rewrite move:** delete. If the sentence has a real claim under the throat-clearing, lead with that claim.

---

## 3. Inflated Vocabulary

One vague word can be harmless. A cluster in one paragraph is slop. Keep a term when it's precise in context (a security tool genuinely is "robust"; a music piece genuinely is a "symphony"). Academic studies show measurable post-2022 spikes in many of these words; clusters are the reliable signal, not any single occurrence.

**Buzzwords:** `leverage`, `unlock`, `streamline`, `empower`, `transform`, `optimize`, `accelerate`, `enhance`, `innovative`, `robust`, `actionable`, `synergy`, `paradigm`, `elevate`, `harness`, `foster`.

**Academic polish:** `delve`, `intricate`, `intricacies`, `nuanced`, `meticulous`, `underscore`, `showcase`, `garner`, `surpass`, `pivotal`, `advancements`.

**Inflated modifiers:** `game-changing`, `cutting-edge`, `world-class`, `best-in-class`, `revolutionary`, `seamless`, `groundbreaking`, `next-generation`, `transformative`, `breathtaking`.

**Grand metaphors:** `tapestry`, `symphony`, `realm`, `journey`, `testament`, `kaleidoscope`, `labyrinth`, `beacon`. Keep when the article is literally about music, travel, law, religion, or another concrete domain.

**Empty verbs:** `delve into`, `dive deep into`, `navigate the complexities`, `navigate the landscape`.

**Rewrite move:** name the concrete action, metric, or object the buzzword stands in for.

---

## 4. Brochure / Promotional Voice

A distinct smell: praise without observation. Common in travel, real-estate, corporate, and "about" copy. The model substitutes generic positive importance for specific facts.

**Phrases:** `stands as a testament to`, `plays a crucial role`, `rich cultural heritage`, `diverse array`, `lasting impact`, `a significant contribution`, `widely renowned`.

**Adjectives:** `nestled`, `vibrant`, `breathtaking`, `boasts`, `renowned`, `bustling`.

**Rewrite move:** replace praise with one observed detail — a number, a name, a quote, a moment. If you can't, the praise was empty.

---

## 5. Formulaic Structures

Sentence shapes that signal LLM cadence even when the words are fine.

### 5.1 The contrast family

The highest-density slop family. Expanded because it shows up constantly.

The shape: set up a wrong/lesser thing, then "correct" it with the real point. LLMs reach for it because it sounds insightful for free. It almost always reads better with the negation cut.

**Variants:**

- `not X, but Y` — "not a tool, but a platform"
- `not just X, but Y` / `not only X, but also Y` / `not merely X, but Y` / `not simply X, but Y`
- `it's not X. It's Y.` (period-break version, same move)
- `not for X, but for Y`
- `more than just X` — "more than just a database"
- `X isn't about Y. It's about Z.`

**Why it's slop:** the X side usually isn't a position anyone holds. It's a strawman set up so Y can knock it down. The reader gets no information from "not X" — only from Y.

**When to keep it:** the contrast is the actual point and someone real holds the X position. "Not a rewrite, but a refactor" works if a reader genuinely might assume rewrite.

**Rewrite move:** delete the "not X" half. State Y directly. If Y can't stand alone, the sentence had no claim.

**Examples (bad → good):**

- "X is not just A, but B." → "X is B." — state B's specifics directly.
- "It's not about A. It's about B." → cut both halves; describe B on its own terms.
- "This isn't A, it's B." → keep only if a reader would plausibly assume A; then the contrast carries real information.

### 5.2 False ranges

`from X to Y` claiming false comprehensiveness — "from strategy to execution", "from startups to Fortune 500s".

**Rewrite move:** name the actual list, or pick the one that matters. `from X to Y` is fine when X and Y are literal endpoints (a date range, a code path).

### 5.3 Vague authority

`experts agree`, `studies show`, `research suggests`, `industry leaders say`, `widely recognized`, `many believe`. Authority without a source.

**Rewrite move:** name the source and link, or cut the appeal and make the claim on its own merits.

### 5.4 Superficial analysis tags

`highlighting the importance of`, `underscoring the need for`, `demonstrating the value of`, `showcasing the potential of`, `reflecting broader trends`, `this illustrates how`, `this serves as a reminder that`. Bolts a takeaway onto a fact without doing the analytical work.

**Rewrite move:** state what happened and why it matters in concrete terms. If you can't, the analysis isn't there yet.

### 5.5 Question-led assertions

`The best part?`, `So what does this mean?`, `Why does this matter?` followed by the answer.

**Rewrite move:** answer directly. Keep the question only if it's the reader's actual question.

### 5.6 Rule of three

Three-part lists with equal rhythm. "Faster, cheaper, and more reliable." Tricolons sound composed; LLMs reach for them reflexively. Humans use threes constantly — this is only slop when the triads are repeated, abstract, symmetrical, and interchangeable across the piece.

**Rewrite move:** use two items, or make the third concrete and longer than the first two. Asymmetric lists read human.

### 5.7 Tidy conclusions & smooth transitions

Every paragraph has a transition. Every section resolves. Every conclusion sums up and adds a moral.

`Ultimately,`, `In conclusion,`, `At the end of the day,`, `Moving forward,`, `As we continue to...`, `The future of X will depend on...`.

**Rewrite move:** end on the previous sentence, or replace the closer with the next concrete implication.

### 5.8 Hedged, noncommittal stance

The complaint isn't that the prose is wrong — it's too careful. It sees both sides, refuses a hard claim, and ends by saying the answer depends on context.

`It depends on several factors`, `Both approaches have advantages and drawbacks`, `There is no one-size-fits-all answer`, `A balanced approach is essential`, `It is important to consider the broader context`.

**Rewrite move:** pick a side. If you genuinely can't, name *which* factor decides it and give the rule.

### 5.9 Paragraph-ending aphorism

Closing a paragraph with a quotable line that adds no information. "And that's the real lesson here."

**Rewrite move:** replace with the next useful implication, or end on the previous sentence.

---

## 6. Voice & Rhythm

- **Passive without reason:** "mistakes were made". Name the actor unless it's genuinely unknown.
- **Inanimate agency:** "the data tells us", "the market decided", "the document argues". Name the person, team, or institution doing the work.
- **Narrator distance:** describing from outside when putting the reader inside would be sharper.
- **Abstractness with no image:** every noun is a topic word (`complexity`, `innovation`, `identity`, `impact`, `transformation`) — no scene, person, object, number, or quote anchors the paragraph. Diagnostic: can the reader picture anything specific?
- **Metronomic rhythm:** every sentence the same length. Split one or combine two.
- **Em dash overuse:** em dashes are normal punctuation; repeated decorative use across a piece is the smell, not any single instance.

---

## 7. Formatting Tells

Layout reads before prose does. These signal generated output even when the words are fine.

- Title-case headings in contexts that normally use sentence case.
- Bolded key phrases scattered through ordinary prose.
- Generic bullet lists with same-length items where prose would serve.
- Numbered frameworks where no framework is needed.
- The intro / definition / benefits / challenges / future scaffold.
- Tables used to pad thin material.
- Markdown artifacts in non-Markdown contexts.
- Emoji as section markers.

**Rewrite move:** strip the scaffolding. Keep formatting only where it earns its place.

---

## 8. AI Leakage & Process Artifacts

Hard cuts. No judgment call needed. Single-hit Tier-1 confidence.

**Assistant voice:** `as an AI language model`, `I cannot browse`, `my training data`, `knowledge cutoff`, `up to my last update`, `Certainly,`, `Sure, I can help`, `Here is your...`, `Let me know if you want...`.

**Process artifacts:** `turn0search0`, `contentReference`, `oaicite`, `oai_citation`, `attached_file`, `grok_card`, `utm_source=chatgpt`, `utm_source=openai`.

**Citation hygiene:** fake DOIs, fake ISBNs, broken external links, named references that aren't used, citations that don't support the sentence they follow.

---

## 9. General Rewrite Moves

The toolkit, in order of frequency:

1. **Delete throat-clearing** instead of rephrasing it.
2. **Name the actor** for passive or inanimate-agent constructions.
3. **Name the concrete thing** behind a buzzword.
4. **Attach a source, metric, example, or decision** to a vague claim.
5. **State the positive side directly** for over-neat contrasts.
6. **Pick a side** when the prose hedges.
7. **Make it tangible** — a person, object, number, or quote — when the paragraph is all topic words.
8. **Break rhythm** by splitting or combining adjacent sentences.

---

## 10. Do Not

- Rewrite distinctive source language into bland professional prose.
- Remove necessary domain terms just because they appear in a pattern list.
- Add new facts while unslopping.
- Turn every sentence short. Human prose needs rhythm, not uniform bluntness.
- Treat a single tell as proof of AI authorship. Lightly edited AI prose, polished human prose, and non-native English writing all evade these heuristics. The patterns judge *quality*, not *provenance*.
