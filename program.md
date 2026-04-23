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
  - `autobloggy prepare-inputs`
  - `autobloggy generate-outline`
  - `autobloggy generate-draft`
- After the text loop finishes, the agent may prepare or embed visuals only through:
  - `autobloggy prepare-visuals`
  - `autobloggy embed-visuals`
- After visuals are embedded, the agent may render previewable/exportable output only through:
  - `autobloggy export`
- `new-post` owns the default input home: `posts/<slug>/inputs/user_provided/`.
- Human-owned inputs live only under:
  - `posts/<slug>/inputs/user_provided/brief.md`
  - `posts/<slug>/inputs/user_provided/raw/`
- Deterministic derivatives live only under:
  - `posts/<slug>/inputs/extracted/`
  - `posts/<slug>/inputs/prepared/`
- Do not write generated files under `posts/<slug>/inputs/user_provided/raw/`.
- After `generate-draft` has produced the scaffold, the agent may edit `posts/<slug>/draft.qmd` once via skill `autobloggy-first-draft` to turn the scaffold into a real first draft. After that edit, `draft.qmd` becomes read-only again and the attempt loop owns further changes.
- During the attempt loop, the agent may edit only `posts/<slug>/runs/<run-id>/attempts/<attempt-id>/draft.qmd`.
- `program.md`, `config.yaml`, everything under `presets/`, and everything under `shared/` are read-only during a run.
- Do not edit committed `posts/<slug>/strategy.md`, `outline.md`, or `draft.qmd` manually during the attempt loop. Use the CLI stages and `evaluate`.

## Workflow

1. Start a new post.
Owner: Agent with human confirmation.
Agent action: Use skill `autobloggy-new-post`. Collect a plain-language brief, briefly ask whether to use the default preset or create a new preset, and run `autobloggy new-post`. Conversational briefs belong in `posts/<slug>/inputs/user_provided/brief.md`. Source files belong in `posts/<slug>/inputs/user_provided/raw/`.

2. Prepare the deterministic input bundle when raw inputs change.
Owner: Agent.
Agent action: Run `autobloggy prepare-inputs --slug <slug>` whenever the operator adds or changes source material after kickoff. This command owns extraction, inventory, and the canonical bundle under `posts/<slug>/inputs/prepared/`.

3. Review the strategy.
Owner: Human.
Agent action: Help edit `posts/<slug>/strategy.md` until required sections are complete and all unresolved markers are cleared. Wait for explicit human approval.

4. Approve the strategy.
Owner: Human approval, agent executes the command.
Agent action: Run `autobloggy approve-strategy --slug <slug>` only after the human has approved the strategy.

5. Decide on discovery before outlining.
Owner: Human decides explicitly yes or no, agent executes the command.
Agent action: Ask whether to run discovery before generating the outline. Record the explicit answer with `autobloggy decide-discovery --slug <slug> --decision yes|no`. Do not generate the outline until the human has answered.

6. Run discovery if the human chose yes.
Owner: Human decides yes, agent executes.
Agent action: Use skill `autobloggy-discovery` only when the human explicitly chose yes. Write discovery output only under `posts/<slug>/inputs/discovery/`.

7. Generate the outline.
Owner: Agent.
Agent action: Run `autobloggy generate-outline --slug <slug>` only after strategy approval and an explicit discovery decision. If the decision is yes, wait until `posts/<slug>/inputs/discovery/discovery.md` exists. After the CLI command succeeds, read `posts/<slug>/strategy.md`, `posts/<slug>/inputs/prepared/input.md`, and `posts/<slug>/inputs/discovery/discovery.md` (if it exists), then write a complete outline directly into `posts/<slug>/outline.md`. Preserve the existing YAML frontmatter block. Use 4–7 `##`-level section headings with bullets grounded in the source material — no placeholder language. Outline headings must already be publishable, reader-facing section titles, not planning labels like `Hook`, `Context`, `Implications`, `Closing`, or `Body section 1`. Every "Must Cover" item from strategy must appear somewhere in the outline.

8. Review the outline.
Owner: Human.
Agent action: Help edit `posts/<slug>/outline.md` until the section structure is correct. Wait for explicit human approval.

9. Approve the outline.
Owner: Human approval, agent executes the command.
Agent action: Run `autobloggy approve-outline --slug <slug>` only after the human has approved the outline.

10. Generate the first draft.
Owner: Agent.
Agent action: Run `autobloggy generate-draft --slug <slug>` to produce the deterministic scaffold, then use skill `autobloggy-first-draft` to rewrite `posts/<slug>/draft.qmd` into a real first draft using the approved strategy, outline, prepared input bundle, input manifest, and preset writing and brand guides. Do not stage the first attempt until the rewrite is complete.

11. Run the attempt loop.
Owner: Agent.
Agent action: Use skill `autobloggy-draft-loop`. Start the first attempt with `autobloggy stage-attempt --slug <slug>`. After a run exists, continue it with `autobloggy stage-attempt --slug <slug> --run-id <run-id>`. Use `--new-run` only when intentionally starting a fresh run.

12. Tighten prose when the active task is purely editorial.
Owner: Agent.
Agent action: Use skill `autobloggy-copy-edit` only when the active task is prose tightening.

13. Prepare local transcripts when the source material needs it.
Owner: Agent.
Agent action: Use skill `autobloggy-transcribe` only for local transcription input prep.

14. Prepare visual requests.
Owner: Agent.
Agent action: Run `autobloggy prepare-visuals --slug <slug>` only after the draft is ready for visual work. This command refreshes deterministic input prep, scans `draft.qmd` for `<!-- visual: hint -->` markers, and writes `posts/<slug>/visuals/requests.json`.

15. Generate visuals.
Owner: Agent.
Agent action: Use skill `autobloggy-visuals` only after `prepare-visuals` has written the request bundle. The skill may read `posts/<slug>/inputs/prepared/input.md`, `posts/<slug>/inputs/prepared/input_manifest.yaml`, and the preset guides. It may not write under `inputs/user_provided/`, `inputs/extracted/`, or `inputs/prepared/`.

16. Verify generated visuals.
Owner: Agent.
Agent action: Run `autobloggy verify-visuals --slug <slug>` after the generated `visual.html` files exist and before the human approves embed. This command writes deterministic `check-results.json`, `verifier_requests.json`, placeholder verdict JSON files, and `screenshot.png` when a Playwright-backed visual verifier needs pixels. Use skill `autobloggy-visual-verifier` only after `verify-visuals` has written the verifier bundle.

17. Embed approved visuals.
Owner: Human approves, agent executes.
Agent action: After previewing the generated `visual.html` files and their verifier verdicts, run `autobloggy embed-visuals --slug <slug>` to replace the matching markers in `draft.qmd`.

18. Export the post for review or publication.
Owner: Agent on request.
Agent action: Run `autobloggy export --slug <slug> --format html|qmd|pdf|docx` to render a previewable or publishable artifact under `posts/<slug>/export/<format>/`. HTML is the default preview path and renders the iframe-embedded visuals inline via Quarto. PDF and DOCX first rasterize each embedded visual via Playwright and then render through Quarto. QMD writes a copy of the current draft with no rendering. Quarto ships via the `quarto-cli` uv dependency, so invoke through `uv run autobloggy export`. Playwright must be installed for PDF/DOCX.
