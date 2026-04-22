# How to Use Claude Code and NotebookLM for a Digestible Content Infographic Pipeline

Reading backlog is unmanageable, especially when it includes long papers, technical PDFs, and documents that matter but are not central enough to justify a full close read.

The workflow pairs a coding agent with NotebookLM to compress source material into slide decks and infographics tailored to a specific learning style. The goal is not to replace deep reading for core material. The goal is to triage faster, understand more of the backlog, and decide what deserves a deeper pass.

## Problem framing

- Reading backlog keeps growing.
- Long non-core documents are expensive to read end to end.
- Important ideas get delayed because triage takes too long.

## Solution concept

- Use Claude Code to run the automation and structure outputs.
- Use NotebookLM to synthesize source material into digestible learning assets.
- Produce slide decks and infographics matched to how the reader learns best.

## When and why to use it

- Reserve deep reading for material that is central to a project or decision.
- Run this workflow on secondary papers, product docs, and long PDFs first.
- Use the output to decide what deserves full reading later.

## Setup steps

- Install `uv`.
- Install `notebooklm-py`.
- Authenticate.
- Run a smoke test.
- Point Claude Code at the repository and prompt.

## Prompt and style guide

- Tell the agent what to create: decks, infographics, or both.
- Specify how outputs should be structured.
- State the target learning style and level of detail.
- Ask for concise explanations and visual hierarchy.

## Example runs

- Cursor Composer 2
- Meta TRIBE v2
- Claude Mythos card

## Time savings and takeaways

- Rough comparison: about 15 minutes with the workflow versus about 4 hours of conventional reading.
- The workflow helps surface what deserves deeper reading.
- The output is easier to scan, share, and revisit.
