# Autobloggy Program

## Roles

- Human: provides the topic or source material, reviews and approves `blog_brief.md`, sets the verify-loop iteration cap, and decides when the post is good enough to stop.
- Agent: follows the stage commands, uses only the skills explicitly named here, and keeps the workflow moving without inventing parallel instructions.

## Instruction Ownership

- `program.md` owns the workflow, stage order, gates, edit boundaries, and named skill invocations.
- `CLAUDE.md` and `AGENTS.md` are bootstrap indexes only.
- Skills are subroutines, not alternate workflow specs.
- Do not infer alternate workflow instructions from `CLAUDE.md`, `AGENTS.md`, or any skill.

## Editable Boundaries

- Before the verify loop, the agent may create or refresh post artifacts only through these commands:
  - `autobloggy prep`
  - `autobloggy approve-brief`
  - `autobloggy generate-draft`
- Human-owned raw inputs live only under `posts/<slug>/inputs/raw/`.
- System-owned normalized sources live only under `posts/<slug>/inputs/prepared/`.
- `posts/<slug>/blog_brief.md` is the only pre-draft approval artifact and the drafting contract.
- Do not write generated files under `posts/<slug>/inputs/raw/`.
- After `generate-draft` has produced the HTML scaffold, the agent may edit `posts/<slug>/draft.html` once via skill `autobloggy-first-draft` to produce a real first draft. After that edit, only the verify loop edits `draft.html`, and only inside `<main>`.
- During the verify loop, the agent may edit only `posts/<slug>/draft.html` inside `<main>`.
- Pipeline state lives in `posts/<slug>/meta.yaml`. CLI commands flip status fields there; the agent does not edit it directly.
- `program.md`, `config.yaml`, `prompts/quality_criteria.md`, and everything under `presets/` are read-only during a run.

## Workflow

1. Prepare post artifacts.
Owner: Agent with human input.
Agent action: Use skill `autobloggy-new-post`. Collect a plain-language direction or source material, briefly ask about preset/intake depth only when needed, and run `autobloggy prep`. The CLI creates `blog_brief.md`, `inputs/prepared/manifest.yaml`, and normalized intake source files. Source files belong in `posts/<slug>/inputs/raw/`.

2. Fill and review the blog brief.
Owner: Human approves; agent assists.
Agent action: Help fill every `[ASK_USER]` and `[AUTO_FILL]` marker in `posts/<slug>/blog_brief.md`. The approved brief must include a concrete angle, evidence plan, full outline, required points, things to avoid, and generation context references. `blog_brief.md` must be sufficient for an isolated draft agent to work from without implicit repo-path knowledge.

3. Approve the brief.
Owner: Human approval, agent executes the command.
Agent action: Run `autobloggy approve-brief --slug <slug>` only after the human has approved `blog_brief.md`. This mechanical gate fails if fill markers remain, the full outline is missing, or required context paths are missing.

4. Generate the draft scaffold.
Owner: Agent.
Agent action: Run `autobloggy generate-draft --slug <slug>` to materialize `posts/<slug>/draft.html` from the selected `html_template`. The CLI fills in `<title>` and the H1 only.

5. Write the first draft.
Owner: Agent.
Agent action: Use skill `autobloggy-first-draft`, with `slop-mop` prevention rules active for public-facing prose. Read `blog_brief.md` first, follow the file references in its Generation Context, and edit `<main>` of `draft.html` directly. Author prose and inline visuals together. Do not assume any other repo structure.

6. Run the verify loop.
Owner: Agent within the user-specified iteration cap.
Agent action: Use skill `autobloggy-draft-loop`. Each cycle: `autobloggy verify --slug <slug>` strips old markers, runs programmatic checks, captures screenshots, and writes `.verify/verify-pack.md`; then dispatch the `autobloggy-verifier` sub-agent to insert LLM-judged markers; then surgically fix every marker. Stop when marker count is zero and a fresh verify run inserts no new markers, or when the iteration cap is hit.

7. Prepare local transcripts when the source material needs it.
Owner: Agent.
Agent action: Use skill `autobloggy-transcribe` only for local transcription input prep. Store original media under `inputs/raw/` and normalized transcript output under `inputs/prepared/`.

8. Unslop the final draft.
Owner: Agent.
Agent action: Use skill `slop-mop` as the final workflow step after the verify loop. Run its detector against `posts/<slug>/draft.html`, then edit only `posts/<slug>/draft.html` inside `<main>` plus title/meta description only if needed. Repeat until the detector is clean or the operator asks to stop.
