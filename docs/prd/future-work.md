# Future Work

## Visual Loop

- Generate visual strategies from accepted claims and outline sections.
- Create diagram or image assets with a separate accept-or-retry loop.
- Run deterministic asset checks and image-understanding verifiers before
  linking accepted assets into `draft.qmd`.

## Render And Export

- Add Quarto/Pandoc-backed HTML and PDF rendering once the text loop is stable.
- Add CMS payload export after the citation and asset contracts settle.

## Portfolio Memory

- Add cross-post memory under `portfolio/` derived from accepted run logs.
- Keep v1 focused on one post at a time.


---

# Wishlist

- better unified abstraction for verifiers (llm) and checks (programmatic), or multi-agent verifiers (e.g. subagent swarm - such as those that might be used to verify claims/prevent hallucinations)

- simplify the revision pipeline, so that it just gets all the changes at once.