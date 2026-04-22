---
slug: capacity-utilization-myth-why-teams-at-100-utilization-are-less-productive
title: 'Capacity utilization myth: why teams at 100% utilization are less productive'
input_path: /Users/balmasi/Projects/autobloggy/posts/capacity-utilization-myth-why-teams-at-100-utilization-are-less-productive/inputs/user_provided/input.md
input_root: /Users/balmasi/Projects/autobloggy/posts/capacity-utilization-myth-why-teams-at-100-utilization-are-less-productive/inputs/user_provided
input_type: markdown
preset: georgian
preset_dir: presets/georgian
preset_strategy_template: presets/georgian/strategy_template.md
preset_writing_guide: presets/georgian/writing_guide.md
preset_brand_guide: presets/georgian/brand_guide.md
generated_at: '2026-04-22T04:40:41+00:00'
status: approved
discovery_decision: 'yes'
discovery_decided_at: '2026-04-22T04:41:41+00:00'
approved_at: '2026-04-22T04:47:00+00:00'
---

Capacity utilization myth: why teams at 100% utilization are less productive

## Preset Context

- Preset: `georgian`
- Strategy template: `presets/georgian/strategy_template.md`
- Writing guide: `presets/georgian/writing_guide.md`
- Brand guide: `presets/georgian/brand_guide.md`

## Core Question

Why do teams at 100% utilization deliver slower than teams at 70-85%? How do CTOs measure and fix the hidden costs of overutilization—context-switching, unplanned work, process friction—and what's the concrete playbook for implementing WIP limits to restore predictable delivery and team health?

## Audience

**Primary segment for this post:** Growth-Stage CTOs  
**Specific job they are trying to do:** Manage engineering teams in AI-native companies by understanding the economic and operational tradeoffs of high utilization, and implementing practical work-in-progress (WIP) controls to improve delivery predictability and team capacity.

## Positioning

- Lead with the practitioner angle — what was built, tested, or observed.
- Every claim must be grounded in data, benchmarks, customer language (anonymised), or expert calls.
- Avoid invented category language or slogans unless they appear in approved Georgian materials.
- Use product, company, and tool names exactly as the source material spells them.

## Reader Outcome

By the end of the piece, the reader should:
- understand why exponential wait times dominate at high utilization (the math), what hidden costs compound the problem (context-switching, unplanned work, process friction), and why 70-85% is economically optimal, not 100%
- be able to implement WIP limits immediately (starting rule: team size + 1) and measure success (expect 20-30% lead time improvement within 2-4 sprints)
- trust that the claim is backed by queuing theory (Kingman Formula, Little's Law), real-world case studies (Aerosud 2x throughput, DEV Community 65% lead time), and practitioner research on sustainable team utilization

## Target Voice

Write like a practitioner speaking to other capable operators who want clarity, not category jargon. The tone should be confident, evidence-led, and direct, with clear judgments where the material supports them. Favor plain English, crisp distinctions, and concrete examples over abstract commentary or ecosystem buzzwords.

**Confirmed.** Lead with the math and data that proves the counterintuitive point, then move to the hidden costs and implementation playbook.

## Style Guardrails

- Lead with data and the math (Kingman Formula, Little's Law, multipliers) before generalizing.
- Each section addresses one mechanism: why 100% fails (math), what it costs (hidden costs), how to fix it (WIP limits).
- Ground every claim in a case study, formula, or source—no invented best practices.
- Use real numbers (22-minute wait, 20% context-switch cost, 65% lead time improvement) over abstract language.
- Keep the prose precise, practical, and free of hype. Avoid "transforming" or "unlocking." Use "proves," "delivers," "shows."

## Post Type & Length

**Deep-dive / thesis post: 1,200–2,000 words**

We need to establish the why (queuing theory, the math), show the hidden costs, and provide a practical implementation path. This warrants the full depth.

## Must Cover

- **The mathematical proof:** Queuing theory and why wait times skyrocket exponentially as utilization approaches 100% (the ρ/(1-ρ) ratio, concrete examples at 50%, 80%, 95%)
- **Hidden costs at high utilization:** Delayed delivery, quality erosion, reduced innovation, team burnout—and why these costs exceed the savings from eliminating idle time
- **Practical implementation:** How to shift from measuring utilization (hard and counterintuitive) to limiting work-in-progress (WIP) using Little's Law as the mechanism for improvement
- **Optimal range:** Why 70-85% utilization is the economically sound target, not a ceiling to maximize toward

## Must Avoid

- "AI is transforming X" or any other unearned market claim.
- Abstract advice with no mechanism, example, or operator takeaway.
- Hype, vague confidence, or generic assistant phrasing.
- Opening with industry overview instead of a concrete observation.

## Open Questions Before Approval

- ✓ **Audience segment and job:** Growth-Stage CTOs managing engineering teams in AI-native companies, deciding how to balance team utilization and delivery predictability.
- ✓ **Evidence backbone:** Solid foundation from queuing theory (Kingman Formula, M/M/1, Little's Law), real-world case studies (Aerosud 2x throughput, DEV Community 65% lead time, Elixir Radar 6% flow efficiency), and practitioner research on WIP implementation, work distribution, and utilization targets.
- ✓ **Actionable takeaway:** CTOs will understand how to implement WIP limits (simple rule: WIP = team size + 1, dynamic refinement via CFD charts, service classes for mixed work) and measure success (lead time reduction expected within 2-4 sprints).
- ✓ **Post type and word count:** Deep-dive thesis post, 1,200–2,000 words.

## Approval Checklist

- [x] Audience segment and reader job are specific.
- [x] Positioning is grounded in firsthand evidence, not market commentary. **Research complete.**
- [x] Target voice matches the intended audience and Georgian tone.
- [x] Style guardrails are concrete enough to guide drafting.
- [x] Post type and word count are confirmed.
- [x] Must-cover points capture the non-negotiable substance.
