# Speed-Boost Opportunities

Audit of the Autobloggy pipeline for wall-clock and cost reductions. Grounded in the current code at the time of writing; verify before acting.

## 1. Parallelize the 10-verifier verdict step (biggest win)

**Where:** `skills/autobloggy-draft-loop/SKILL.md` step 7 + `src/autobloggy/verifiers.py:10-21`

Every loop iteration, the agent hand-fills 10 verdict JSON files — each one an LLM judgment over a small excerpt. Today's skill just says "fill every verdict JSON file" with no parallelism guidance, so a model tends to do them serially. Each verifier is fully independent (separate prompt, separate excerpt, scope=`draft`).

**Change:** Rewrite step 7 to dispatch all 10 verdicts as parallel sub-agents (one Agent call per tool message with 10 blocks) OR — better — add an `autobloggy verify --execute` path that fans them out via the Anthropic SDK with prompt caching on the draft body. Collapses ~10× sequential calls into 1× wall-clock.

## 2. Replace 3 of the 10 verifiers with deterministic checks

**Where:** `prompts/verifiers/{overstatement,filler_hype,voice}.md` + `shared/banned_patterns.yaml`

These three verifier prompts are *one-sentence* pattern checks ("avoid filler transitions, empty intensifiers, and hype"), and `banned_patterns.yaml` + em-dash scanning already do the same job deterministically. The prompts don't need judgment; they need a wordlist.

**Change:** Extend `banned_patterns.yaml` with the standard hype/filler/company-speak lexicon ("actually," "simply," "powerful," "robust," "unlock," "in today's landscape," etc.) and delete those three verifiers from `VERIFIER_SPECS`. Keeps the semantic ones (`paragraph_focus`, `so_what`, `specificity`, `opening_clarity`, disclosure checks) where judgment actually matters.

**Quality risk:** Low if the banned list is curated well. The current LLM prompts are already rule-shaped — you're not losing nuance, you're removing a round-trip.

## 3. Cache verdicts by excerpt hash across attempts

**Where:** `src/autobloggy/verifiers.py:53-68`

`build_verifier_requests` recomputes 3 excerpts per attempt: `opening` (first 3 sentences), `focus` (first 3 paragraphs), `whole` (first 1600 chars). Most loop iterations touch one section — the other excerpts are byte-identical across attempts, but verdicts get regenerated from scratch.

**Change:** Hash each excerpt; if the previous attempt's excerpt hash matches and that verdict passed, copy the JSON forward instead of re-requesting. Easy win since `create_attempt` already has access to the prior attempt dir. Typical loop: cuts 5–8 of 10 verdicts per iteration.

## 4. Pin skill agents to Haiku/Sonnet instead of the default

**Where:** `skills/*/agents/openai.yaml` (and `.agents/` mirrors)

Discovery sub-agents, copy-edit, and verdict-filling are bounded extraction/judgment tasks, not creative generation. If they're running on Opus by default, you're paying 3–5× latency for no quality gain. Draft generation and outline synthesis are where Opus earns its keep.

**Change:** In the agent YAMLs, explicitly set:

- `autobloggy-discovery` sub-agents → Haiku 4.5 (web fetch + extract)
- `autobloggy-copy-edit` → Sonnet 4.6
- Verdict-filling (whether via skill or SDK) → Haiku 4.5
- Keep Opus 4.7 only for `generate-outline` and the main `stage-attempt` edit.

## 5. Fan out discovery's synthesis, not just the research

**Where:** `skills/autobloggy-discovery/SKILL.md` steps 3–6

Research is already parallel (5 angles). But step 6 ("synthesize into `discovery.md`") is a single serial call reading all 5 files. On top of that, outline generation (program.md step 6) is a separate serial call that re-reads the same inputs. That's two full reads of the same material back-to-back.

**Change:** Have the discovery synthesis emit the outline candidate directly (or at least the "differentiating angles" section of it) so `generate-outline` only has to merge strategy + discovery synthesis, not re-derive angles from raw source files. Saves one full-context pass and tightens the handoff.

## Recommended sequencing

Start with #2 (smallest diff, immediate cost drop) and #4 (config-only), then tackle #1+#3 together since they share the verifier refactor. #5 is a larger structural change — defer until the verify phase is already fast.
