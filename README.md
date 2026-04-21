# Autobloggy

Autobloggy is a Codex-first writing harness modeled on the `autoresearch`
backbone: fixed tooling, one human-maintained `program.md`, one main editable
draft artifact, and a keep-or-revert loop.

## Workflow

1. `uv sync`
2. Interview the user until you have a usable starting brief and seed. Put the main seed file and any supporting files under `posts/<slug>/seed/`. The brief must capture audience, reader outcome, target voice, style guardrails, must-cover points, must-avoid points, and evidence standards.
3. `uv run autobloggy prepare --slug example-post --seed posts/example-post/seed --through brief`
4. Review and edit `posts/<slug>/brief.md` until every required prompt is resolved and the approval checklist is complete.
5. `uv run autobloggy approve-brief --slug example-post`
6. `uv run autobloggy prepare --slug example-post --seed posts/example-post/seed --through draft`
7. Review the generated post artifacts under `posts/<slug>/`
8. `uv run autobloggy stage-attempt --slug example-post`
9. Open the candidate workspace under `posts/<slug>/runs/<run-id>/attempts/<attempt-id>/`
10. Let Codex or Claude edit only `draft.qmd` and `claims.yaml`
11. `uv run autobloggy verify --slug example-post --run-id <run-id> --attempt <attempt-id>`
12. Fill in the verdict JSON files under the attempt's `verdicts/` directory as part of the same content iteration loop
13. `uv run autobloggy evaluate --slug example-post --run-id <run-id> --attempt <attempt-id>`
14. Repeat steps 8 through 13 until the post is good enough, runtime is exhausted, or the operator stops the run

## Orchestration Notes

- The orchestrator should not stop after the first draft is generated. Once `brief.md` is approved and `prepare --through draft` has run, the expected next step is to enter attempt mode.
- The normal autonomous flow is: `prepare` -> `approve-brief` -> `prepare --through draft` -> `stage-attempt` -> edit candidate -> `verify` -> fill verdicts -> `evaluate` -> repeat.
- `verify` is not the acceptance gate. It prepares verifier requests and verdict files. The orchestrator should also complete those verdicts as part of the same loop unless the operator explicitly wants to review them manually.
- `evaluate` is the acceptance gate. It combines deterministic checks, verifier verdicts, claim issues, and readability metrics to decide `keep` or `revert`.

## Pipeline Pseudocode

```text
function create_blog_post(slug, seed_input):
    ensure_repo_root()
    seed = resolve_seed_path(seed_input)
    parse_seed(seed)

    if brief does not exist:
        generate brief.md from seed and required brief template
        stop for human review

    if brief.md.status != "approved":
        stop until human runs approve-brief

    generate or refresh:
        outline.md
        claims.yaml
        sources.yaml
        draft.qmd

    run_id = create_or_resume_run(slug)
    accepted_summary = current accepted state for run_id

    loop:
        attempt = copy current draft.qmd and claims.yaml into candidate workspace
        baseline_summary = summarize current post state
        deterministic_checks = run checks on current post state
        claim_issues = find active claims that are missing from draft
          or still marked needs_rerun/fail
        next_task = choose next task in this order:
            1. deterministic blockers
            2. must-have verifier failures
            3. claim issues
            4. readability and specificity improvements
        write prompt-pack.md and next-task.json for the attempt

        human or agent edits only:
            draft.qmd
            claims.yaml

        verify attempt:
            write verifier request bundle
            fill verdict JSON files with pass/fail as part of the same loop

        evaluate attempt:
            summarize blocker count, verifier failures, claim issues,
            readability penalty, and banned patterns
            compare acceptance tuple against accepted_summary

        if candidate is a strict improvement:
            copy attempt draft.qmd and claims.yaml back to posts/<slug>/
            update accepted_summary
            append "keep" to results.tsv
        else:
            discard candidate changes
            append "revert" to results.tsv

        if post is good enough, runtime is exhausted, or operator stops:
            break
```

## Commands

- `prepare`: staged generation of `brief.md`, `outline.md`, `claims.yaml`,
  `sources.yaml`, and `draft.qmd` from a PPTX or Markdown seed. `--seed` may
  point to a supported file or to a directory such as `posts/<slug>/seed/`.
  When a directory is passed, Autobloggy looks first for `seed.md`,
  `seed.markdown`, `seed.qmd`, `seed.txt`, or `seed.pptx`, then falls back to a
  single supported seed file in that tree. Defaults to `--through brief`.
- `approve-brief`: marks `brief.md` as human-approved so downstream generation
  can continue, but only after required brief fields and approval checklist items
  are resolved
- `stage-attempt`: creates a candidate workspace and a prompt pack for the next
  scoped edit. This is the normal entry point into the iterative keep-or-revert
  loop after the first draft exists.
- `check`: runs deterministic checks and writes a JSON summary
- `verify`: creates verifier request payloads and JSON verdict templates. The
  main content loop should then fill those verdicts before evaluation.
- `evaluate`: applies keep-or-revert logic and appends `results.tsv`. This is
  the acceptance gate for a candidate attempt.
- `refresh-sources`: adds a new source to `sources.yaml` and invalidates linked
  claims

## Repo Layout

- `program.md`: human-maintained constitution and edit boundaries
- `config.yaml`: machine settings and thresholds
- `prompts/`: short task prompts
- `skills/`: reusable operator guidance
- `shared/`: banned phrasing and style rules
- `docs/prd/`: future-phase product specs
- `posts/<slug>/`: committed per-post state
- `posts/<slug>/seed/`: the canonical home for the seed file and supporting
  seed materials such as slides, images, and recordings
- `posts/<slug>/runs/`: ignored per-run state
