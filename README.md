# Autobloggy

Autobloggy is a Codex-first writing harness modeled on the `autoresearch`
backbone: fixed tooling, one human-maintained `program.md`, one main editable
draft artifact, and a keep-or-revert loop.

## Workflow

1. `uv sync`
2. Interview the user until you have a usable starting strategy and user-provided input set. First confirm the actual topic and canonical input source with the user. Do not assume that an open tab, active file, example post, or anything under `tests/fixtures/` is the intended source unless the user explicitly says so. Put the main input file and any supporting files under `posts/<slug>/inputs/user_provided/`. The strategy must capture audience, reader outcome, target voice, style guardrails, must-cover points, and must-avoid points.
3. `uv run autobloggy prepare --slug example-post --input posts/example-post/inputs/user_provided --through strategy`
4. Review and edit `posts/<slug>/strategy.md` until every required prompt is resolved and the approval checklist is complete.
5. `uv run autobloggy approve-strategy --slug example-post`
6. `uv run autobloggy prepare --slug example-post --input posts/example-post/inputs/user_provided --through draft`
7. Review the generated post artifacts under `posts/<slug>/`
8. `uv run autobloggy stage-attempt --slug example-post`
9. Open the candidate workspace under `posts/<slug>/runs/<run-id>/attempts/<attempt-id>/`
10. Let Codex or Claude edit only `draft.qmd`
11. `uv run autobloggy verify --slug example-post --run-id <run-id> --attempt <attempt-id>`
12. Fill in the verdict JSON files under the attempt's `verdicts/` directory as part of the same content iteration loop
13. `uv run autobloggy evaluate --slug example-post --run-id <run-id> --attempt <attempt-id>`
14. Repeat steps 8 through 13 until the post is good enough, runtime is exhausted, or the operator stops the run

## Orchestration Notes

- The orchestrator should not stop after the first draft is generated. Once `strategy.md` is approved and `prepare --through draft` has run, the expected next step is to enter attempt mode.
- The normal autonomous flow is: `prepare` -> `approve-strategy` -> `prepare --through draft` -> `stage-attempt` -> edit candidate -> `verify` -> fill verdicts -> `evaluate` -> repeat.
- `verify` is not the acceptance gate. It prepares verifier requests and verdict files. The orchestrator should also complete those verdicts as part of the same loop unless the operator explicitly wants to review them manually.
- `evaluate` is the acceptance gate. It combines deterministic checks, verifier verdicts, and readability metrics to decide `keep` or `revert`.

## Pipeline Pseudocode

```text
function create_blog_post(slug, input_candidate):
    ensure_repo_root()
    input_path = resolve_input_path(input_candidate)
    parse_input(input_path)

    if strategy does not exist:
        generate strategy.md from the user-provided input and required strategy template
        stop for human review

    if strategy.md.status != "approved":
        stop until human runs approve-strategy

    generate or refresh:
        outline.md
        draft.qmd

    run_id = create_or_resume_run(slug)
    accepted_summary = current accepted state for run_id

    loop:
        attempt = copy current draft.qmd into candidate workspace
        baseline_summary = summarize current post state
        deterministic_checks = run checks on current post state
        next_task = choose next task in this order:
            1. deterministic blockers
            2. must-have verifier failures
            3. readability and specificity improvements
        write prompt-pack.md and next-task.json for the attempt

        human or agent edits only: draft.qmd

        verify attempt:
            write verifier request bundle
            fill verdict JSON files with pass/fail as part of the same loop

        evaluate attempt:
            summarize blocker count, verifier failures, readability penalty,
            and banned patterns
            compare acceptance tuple against accepted_summary

        if candidate is a strict improvement:
            copy attempt draft.qmd back to posts/<slug>/
            update accepted_summary
            append "keep" to results.tsv
        else:
            discard candidate changes
            append "revert" to results.tsv

        if post is good enough, runtime is exhausted, or operator stops:
            break
```

## Commands

- `prepare`: staged generation of `strategy.md`, `outline.md`, and `draft.qmd`
  from a PPTX or Markdown input. `--input` may
  point to a supported file or to a directory such as `posts/<slug>/inputs/user_provided/`.
  When a directory is passed, Autobloggy looks first for `input.md`,
  `input.markdown`, `input.qmd`, `input.txt`, or `input.pptx`, then falls back to a
  single supported input file in that tree. Confirm with the user which file or directory is canonical before you run it. Defaults to `--through strategy`.
- `approve-strategy`: marks `strategy.md` as human-approved so downstream generation
  can continue, but only after required strategy fields and approval checklist items
  are resolved
- `stage-attempt`: creates a candidate workspace and a prompt pack for the next
  scoped edit. This is the normal entry point into the iterative keep-or-revert
  loop after the first draft exists.
- `check`: runs deterministic checks and writes a JSON summary
- `verify`: creates verifier request payloads and JSON verdict templates. The
  main content loop should then fill those verdicts before evaluation.
- `evaluate`: applies keep-or-revert logic and appends `results.tsv`. This is
  the acceptance gate for a candidate attempt.

## Repo Layout

- `program.md`: human-maintained constitution and edit boundaries
- `config.yaml`: machine settings and thresholds
- `prompts/`: short task prompts
- `skills/`: reusable operator guidance
- `shared/`: banned phrasing and style rules
- `docs/prd/`: future-phase product specs
- `posts/<slug>/`: committed per-post state
- `posts/<slug>/inputs/user_provided/`: the canonical home for the main input file and supporting
  user-provided materials such as slides, images, and recordings
- `posts/<slug>/runs/`: ignored per-run state
