# Writing Guide

The human canon for what counts as slop and how to fix it. Organized by category so new entries slot in cleanly. The detector (`scripts/patterns.yaml`) is a separate artifact; rules can live here without a YAML counterpart and vice versa.

These are defaults. User or publication preferences override.

---

## 1. Prevention Rules

Apply while drafting. These prevent most slop before detection is needed.

- Lead with substance, not setup about the piece itself. (A scene, anecdote, or claim all qualify; "this article will explore..." does not.)
- Name the actor, object, metric, tool, place, or tradeoff.
- Prefer concrete nouns and verbs over impressive adjectives.
- Use active voice unless the actor is genuinely unknown or irrelevant.
- Vary sentence and paragraph length.
- Put the reader in the situation when that helps. Avoid narrator distance.
- Avoid em dashes by default. Keep them only when the user or publication style explicitly asks to retain them.

---

## 2. Throat-Clearing & Meta-Talk

Prose about the prose. Cut, don't rephrase. Most of these tells are long-form-specific (articles, essays, reports); they fire less often in social posts, newsletters, or product copy, but the rewrite move is the same when they do.

- `in this article`, `this post will`, `we will explore`, `we will discuss`
- `it is important to note`, `it is worth mentioning`, `it is crucial to recognize`
- `no discussion would be complete without`
- `in summary`, `in conclusion`, `overall`, `ultimately`, `all in all`
- `without further ado`, `when it comes to`
- Stock openers about the age: `in today's fast-paced world`, `in a world where`, `as businesses increasingly`

**Rewrite move:** delete. If the sentence has a real claim under the throat-clearing, lead with that claim.

---

## 3. Inflated Vocabulary

One vague word can be harmless. Several in a paragraph is slop. Keep a term when it is precise in context (a security tool genuinely is "robust"; a music piece genuinely is a "symphony").

**Buzzwords:** `leverage`, `unlock`, `streamline`, `empower`, `transform`, `optimize`, `accelerate`, `enhance`, `innovative`, `robust`, `actionable`, `synergy`, `paradigm`, `elevate`, `harness`, `foster`.

**Inflated modifiers:** `game-changing`, `cutting-edge`, `world-class`, `best-in-class`, `revolutionary`, `seamless`, `groundbreaking`, `next-generation`, `transformative`, `breathtaking`.

**Grand metaphors:** `tapestry`, `symphony`, `realm`, `journey`, `testament`, `kaleidoscope`, `labyrinth`, `beacon`. Keep when the article is literally about music, travel, law, religion, or another concrete domain where the word is doing real work.

**Empty verbs:** `delve into`, `dive deep into`, `navigate the complexities`, `navigate the landscape`.

**Rewrite move:** name the concrete action, metric, or object the buzzword is standing in for.

---

## 4. Formulaic Structures

Sentence shapes that signal LLM cadence even when the words are fine.

### 4.1 The contrast family

This is the highest-density slop family. Expanded because it shows up constantly.

The shape: set up a wrong/lesser thing, then "correct" it with the real point. LLMs love this because it sounds insightful for free. It almost always reads better with the negation cut and the positive side stated directly.

**Variants:**

- `not X, but Y` — "not a tool, but a platform"
- `not just X, but Y` / `not only X, but also Y` / `not merely X, but Y` / `not simply X, but Y`
- `it's not X. It's Y.` (period-break version, same move)
- `more than just X` — "more than just a database"
- `X isn't about Y. It's about Z.`

**Why it's slop:** the X side usually isn't a real position anyone holds. It's a strawman set up so Y can knock it down. The reader gets no information from "not X" — only from Y.

**When to keep it:** the contrast is the actual point and someone real holds the X position. "Not a rewrite, but a refactor" works if a reader genuinely might assume rewrite.

**Rewrite move:** delete the "not X" half. State Y directly. If Y can't stand alone, the sentence had no claim to begin with.

**Examples (bad → good):**

- "X is not just A, but B." → "X is B." — state B's specifics directly.
- "It's not about A. It's about B." → cut both halves; describe B on its own terms.
- "This isn't A, it's B." → keep only if a reader would plausibly assume A; then the contrast carries real information.

### 4.2 False ranges

`from X to Y` claiming false comprehensiveness — "from strategy to execution", "from startups to Fortune 500s".

**Rewrite move:** name the actual list, or pick the one that matters. "from X to Y" is fine when X and Y are literal endpoints (a date range, a code path).

### 4.3 Vague authority

`experts agree`, `studies show`, `research suggests`, `industry leaders say`. Authority without a source.

**Rewrite move:** name the source and link, or cut the appeal and make the claim on its own merits.

### 4.4 Superficial analysis tags

`highlighting the importance of`, `underscoring the need for`, `showcasing the role of`. Bolts a takeaway onto a fact without doing the analytical work.

**Rewrite move:** state what happened and why it matters in concrete terms. If you can't, the analysis isn't there yet.

### 4.5 Question-led assertions

`The best part?`, `So what does this mean?`, `Why does this matter?` followed by the answer.

**Rewrite move:** answer directly. Keep the question only if it's the reader's actual question.

### 4.6 Three-part lists with equal rhythm

"Faster, cheaper, and more reliable." Tricolons sound composed; LLMs reach for them reflexively.

**Rewrite move:** use two items, or make the third concrete and longer than the first two. Asymmetric lists read human; symmetric ones read generated.

### 4.7 Paragraph-ending aphorism

Closing a paragraph with a quotable line that adds no information. "And that's the real lesson here."

**Rewrite move:** replace with the next useful implication, or end on the previous sentence.

---

## 5. Voice & Rhythm

- **Passive without reason:** "mistakes were made". Name the actor unless it's genuinely unknown.
- **Inanimate agency:** "the data tells us", "the market decided", "the document argues". Name the person, team, or institution actually doing the work.
- **Narrator distance:** describing the situation from outside when putting the reader inside would be sharper.
- **Metronomic rhythm:** every sentence the same length. Split one or combine two.
- **Em dash overuse:** em dashes are normal punctuation; repeated decorative use across a piece is the smell, not any single instance.

---

## 6. AI Response Leakage

Hard cuts. No judgment call needed.

`as an AI language model`, `I cannot browse`, `my training data`, `knowledge cutoff`, `up to my last update`, scaffolding tokens like `turn0search0`.

---

## 7. General Rewrite Moves

The toolkit, in order of frequency:

1. **Delete throat-clearing** instead of rephrasing it.
2. **Name the actor** for passive or inanimate-agent constructions.
3. **Name the concrete thing** behind a buzzword.
4. **Attach a source, metric, example, or decision** to a vague claim.
5. **State the positive side directly** for over-neat contrasts.
6. **Break rhythm** by splitting or combining adjacent sentences.

---

## 8. Do Not

- Rewrite distinctive source language into bland professional prose.
- Remove necessary domain terms just because they appear in a pattern list.
- Add new facts while unslopping.
- Turn every sentence short. Human prose needs rhythm, not uniform bluntness.
