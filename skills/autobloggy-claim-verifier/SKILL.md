---
name: autobloggy-claim-verifier
description: Verify Autobloggy claims against nearby draft context and linked sources. Use when reviewing `claims.yaml`, checking whether a claim is supported, or writing binary verifier verdicts for claim support and unsupported superlatives.
---

# Autobloggy Claim Verifier

Use this skill when checking whether Autobloggy claims should pass or fail.

## Scope

- One claim at a time.
- Use the active claim text, its section, the nearby draft paragraph, and linked source snippets.
- Keep the evaluation binary: `pass` or `fail`.

## Workflow

1. Read the claim entry from `claims.yaml`.
2. Find the exact claim text in `draft.qmd`.
3. Review the linked `source_ids` in `sources.yaml`.
4. Decide whether the claim is supported nearby or by explicit evidence.
5. Write a short rationale and the smallest useful evidence list.

## Fail Conditions

- The draft no longer contains the claim text.
- The linked sources do not support the claim.
- The passage uses unsupported superlatives or stronger wording than the evidence.
- The claim depends on information that is not in the draft context or sources.

## Rules

- Prefer primary evidence.
- Do not infer support from topic similarity alone.
- If the source only partly supports the wording, fail and explain the gap.

