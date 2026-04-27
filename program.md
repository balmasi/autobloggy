# Autobloggy Program

## Roles

- Human: provides the topic or source material, chooses between the default preset and a new preset, helps shape `strategy.md`, approves `outline.md`, sets the verify-loop iteration cap, and decides when the post is good enough to stop.
- Agent: follows the stage commands, uses only the skills explicitly named here, and keeps the workflow moving without inventing parallel instructions.

## Instruction Ownership

- `program.md` owns the workflow, stage order, gates, edit boundaries, and named skill invocations.
- `CLAUDE.md` and `AGENTS.md` are bootstrap indexes only.
- Skills are subroutines, not alternate workflow specs.
- Do not infer alternate workflow instructions from `CLAUDE.md`, `AGENTS.md`, or any skill.

## Editable Boundaries

- Before the verify loop, the agent may create or refresh post artifacts only through these commands:
  - `autobloggy new-post`
  - `autobloggy prepare-inputs`
  - `autobloggy generate-strategy`
  - `autobloggy generate-outline`
  - `autobloggy generate-draft`
- `new-post` owns the default input home: `posts/<slug>/inputs/user_provided/`.
- Human-owned inputs live only under:
  - `posts/<slug>/inputs/user_provided/brief.md`
  - `posts/<slug>/inputs/user_provided/raw/`
- The deterministic LLM-facing bundle lives only under:
  - `posts/<slug>/inputs/prepared/`
- Do not write generated files under `posts/<slug>/inputs/user_provided/raw/`.
- After `generate-draft` has produced the HTML scaffold, the agent may edit `posts/<slug>/draft.html` once via skill `autobloggy-first-draft` to produce a real first draft (prose AND inline visuals together). After that edit, only the verify loop edits `draft.html`, and only inside `<main>`.
- During the verify loop, the agent may edit only `posts/<slug>/draft.html` (inside `<main>`).
- Pipeline state lives in `posts/<slug>/meta.yaml`. CLI commands flip status fields there; the agent does not edit it directly.
- `program.md`, `config.yaml`, and everything under `presets/` are read-only during a run.
- Do not edit `posts/<slug>/strategy.md` or `outline.md` once the verify loop has started.

## Workflow

1. Start a new post.
Owner: Agent with human confirmation.
Agent action: Use skill `autobloggy-new-post`. Collect a plain-language brief, briefly ask whether to use the default preset or create a new preset, and run `autobloggy new-post`. Conversational briefs belong in `posts/<slug>/inputs/user_provided/brief.md`. Source files belong in `posts/<slug>/inputs/user_provided/raw/`.

2. Prepare the deterministic input bundle when raw inputs change.
Owner: Agent.
Agent action: Run `autobloggy prepare-inputs --slug <slug>` whenever the operator adds or changes source material after kickoff. This command owns the canonical bundle under `posts/<slug>/inputs/prepared/`.

3. Generate the strategy.
Owner: Agent.
Agent action: Run `autobloggy generate-strategy --slug <slug>` to apply the preset's strategy template to the prepared inputs and write `posts/<slug>/strategy.md`.

4. Review the strategy.
Owner: Human; agent assists.
Agent action: Help edit `posts/<slug>/strategy.md` until required sections are complete and all unresolved markers are cleared. There is no CLI approval gate for strategy — human review is the gate.

5. Decide on discovery before outlining.
Owner: Human decides explicitly yes or no, agent executes the command.
Agent action: Ask whether to run discovery before generating the outline. Record the explicit answer with `autobloggy decide-discovery --slug <slug> --decision yes|no`. Do not generate the outline until the human has answered.

6. Run discovery if the human chose yes.
Owner: Human decides yes, agent executes.
Agent action: Use skill `autobloggy-discovery` only when the human explicitly chose yes. Write discovery output only under `posts/<slug>/inputs/discovery/`.

7. Generate the outline.
Owner: Agent.
Agent action: Run `autobloggy generate-outline --slug <slug>` only after the human is satisfied with the strategy and an explicit discovery decision is recorded. The CLI writes a stub outline at `posts/<slug>/outline.md`. Then read `posts/<slug>/strategy.md`, `posts/<slug>/inputs/prepared/input.md`, and `posts/<slug>/inputs/discovery/discovery.md` (if it exists), and rewrite the outline with 4–7 `##`-level section headings grounded in the source material. Outline headings must already be publishable, reader-facing section titles, not planning labels like `Hook`, `Context`, `Implications`, or `Section 1`. Every "Must Cover" item from strategy must appear somewhere in the outline.

8. Review the outline.
Owner: Human.
Agent action: Help edit `posts/<slug>/outline.md` until the section structure is correct. Wait for explicit human approval.

9. Approve the outline.
Owner: Human approval, agent executes the command.
Agent action: Run `autobloggy approve-outline --slug <slug>` only after the human has approved the outline. This flips `status` to `outline_approved` in `meta.yaml`.

10. Generate the draft scaffold.
Owner: Agent.
Agent action: Run `autobloggy generate-draft --slug <slug>` to materialize `posts/<slug>/draft.html` from the active preset's `template.html`. The CLI fills in `<title>` and the H1 only.

11. Write the first draft (prose + inline visuals).
Owner: Agent.
Agent action: Use skill `autobloggy-first-draft`, with `slop-mop` prevention rules active for public-facing prose. Edit `<main>` of `posts/<slug>/draft.html` directly using the approved strategy, outline, prepared input bundle, preset writing/brand guides, and `prompts/verifier_rubrics.md`. Author inline visuals (`<svg>`, `<canvas>`, `<img>`) inside `<main>` as part of v0.

12. Run the verify loop.
Owner: Agent within the user-specified iteration cap.
Agent action: Use skill `autobloggy-draft-loop`. Each cycle: `autobloggy verify --slug <slug>` (programmatic markers + screenshots + verify-pack), then dispatch the `autobloggy-verifier` sub-agent (fresh context) to insert LLM-judged markers, then surgically fix every marker. The fix pass owns prose AND inline visual edits — `<!-- fb[needs_visual]: hint -->` markers are resolved by authoring the visual inline (`<svg>`, `<canvas>`, `<figure>`+`<img>`) using the brand tokens already declared in the draft's `<head>`. Visual feedback markers on existing visuals are resolved by editing the visual in place. Stop when marker count is zero and a fresh verify run inserts no new markers, or when the user-specified iteration cap is hit.

13. Prepare local transcripts when the source material needs it.
Owner: Agent.
Agent action: Use skill `autobloggy-transcribe` only for local transcription input prep.

14. Unslop the final draft.
Owner: Agent.
Agent action: Use skill `slop-mop` as the final workflow step after the verify loop. Run its detector against `posts/<slug>/draft.html`, then edit only `posts/<slug>/draft.html` inside `<main>` (plus title/meta description only if needed) to remove AI-sounding filler, formulaic structures, and generic business language. Repeat the skill's detect/fix pass until the detector is clean or the operator asks to stop.
