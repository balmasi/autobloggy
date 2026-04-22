# Autobloggy Program

## Roles

- Human: provides the topic or source material, chooses between the default preset and a new preset, approves `strategy.md`, approves `outline.md`, and decides when the post is good enough to stop.
- Agent: follows the stage commands, uses only the skills explicitly named here, and keeps the workflow moving without inventing parallel instructions.

## Instruction Ownership

- `program.md` owns the workflow, stage order, gates, edit boundaries, and named skill invocations.
- `CLAUDE.md` and `AGENTS.md` are bootstrap indexes only.
- Skills are subroutines, not alternate workflow specs.
- Do not infer alternate workflow instructions from `CLAUDE.md`, `AGENTS.md`, or any skill.

## Editable Boundaries

- Before the attempt loop, the agent may create or refresh post artifacts only through these commands:
  - `autobloggy new-post`
  - `autobloggy generate-outline`
  - `autobloggy generate-draft`
- `new-post` owns the default input home: `posts/<slug>/inputs/user_provided/`.
- During the attempt loop, the agent may edit only `posts/<slug>/runs/<run-id>/attempts/<attempt-id>/draft.qmd`.
- `program.md`, `config.yaml`, everything under `presets/`, and everything under `shared/` are read-only during a run.
- Do not edit committed `posts/<slug>/strategy.md`, `outline.md`, or `draft.qmd` manually during the attempt loop. Use the CLI stages and `evaluate`.

## Workflow

1. Start a new post.
Owner: Agent with human confirmation.
Agent action: Use skill `autobloggy-new-post`. Collect a plain-language brief, briefly ask whether to use the default preset or create a new preset, and run `autobloggy new-post`. If source files already exist, use `posts/<slug>/inputs/user_provided/` by default.

2. Review the strategy.
Owner: Human.
Agent action: Help edit `posts/<slug>/strategy.md` until required sections are complete and all unresolved markers are cleared. Wait for explicit human approval.

3. Approve the strategy.
Owner: Human approval, agent executes the command.
Agent action: Run `autobloggy approve-strategy --slug <slug>` only after the human has approved the strategy.

4. Decide on discovery before outlining.
Owner: Human decides explicitly yes or no, agent executes the command.
Agent action: Ask whether to run discovery before generating the outline. Record the explicit answer with `autobloggy decide-discovery --slug <slug> --decision yes|no`. Do not generate the outline until the human has answered.

5. Run discovery if the human chose yes.
Owner: Human decides yes, agent executes.
Agent action: Use skill `autobloggy-discovery` only when the human explicitly chose yes. Write discovery output only under `posts/<slug>/inputs/discovery/`.

6. Generate the outline.
Owner: Agent.
Agent action: Run `autobloggy generate-outline --slug <slug>` only after strategy approval and an explicit discovery decision. If the decision is yes, wait until `posts/<slug>/inputs/discovery/discovery.md` exists. After the CLI command succeeds, read `posts/<slug>/strategy.md`, `posts/<slug>/inputs/user_provided/input.md`, and `posts/<slug>/inputs/discovery/discovery.md` (if it exists), then write a complete outline directly into `posts/<slug>/outline.md`. Preserve the existing YAML frontmatter block. Use 4–7 `##`-level section headings with bullets grounded in the source material — no placeholder language. Outline headings must already be publishable, reader-facing section titles, not planning labels like `Hook`, `Context`, `Implications`, `Closing`, or `Body section 1`. Every "Must Cover" item from strategy must appear somewhere in the outline.

7. Review the outline.
Owner: Human.
Agent action: Help edit `posts/<slug>/outline.md` until the section structure is correct. Wait for explicit human approval.

8. Approve the outline.
Owner: Human approval, agent executes the command.
Agent action: Run `autobloggy approve-outline --slug <slug>` only after the human has approved the outline.

9. Generate the first draft.
Owner: Agent.
Agent action: Run `autobloggy generate-draft --slug <slug>`.

10. Run the attempt loop.
Owner: Agent.
Agent action: Use skill `autobloggy-draft-loop`. Start the first attempt with `autobloggy stage-attempt --slug <slug>`. After a run exists, continue it with `autobloggy stage-attempt --slug <slug> --run-id <run-id>`. Use `--new-run` only when intentionally starting a fresh run.

11. Tighten prose when the active task is purely editorial.
Owner: Agent.
Agent action: Use skill `autobloggy-copy-edit` only when the active task is prose tightening.

12. Prepare local transcripts when the source material needs it.
Owner: Agent.
Agent action: Use skill `autobloggy-transcribe` only for local transcription input prep.
