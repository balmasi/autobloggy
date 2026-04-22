# Research Summary: Capacity Utilization, Team Productivity, and AI-Native Engineering Teams

**Query:** capacity utilization team productivity software engineering delivery  
**Date:** 2026-04-22  
**Target Audience:** Growth-stage engineering CTOs managing AI-native teams

---

## Executive Summary

Three substantive sources reveal a consistent finding: **100% capacity utilization is a productivity myth that drives burnout, quality issues, and slower delivery**. The optimal target is 70–80% utilization, and work-in-progress (WIP) limits are a practical intervention for teams currently overloaded. Key hidden costs include unplanned work (30–50% of time), context-switching overhead (20% productivity loss per switch), and invisible process delays (waiting on reviews, unclear requirements).

---

## Source 1: Jellyfish – Engineering Capacity Planning

**URL:** https://jellyfish.co/blog/engineering-capacity-planning/

### Core Thesis
Systematic capacity planning is essential for preventing project delays, reducing burnout, and improving team productivity. Reactive resource management leads to missed commitments and reputation damage.

### Key Insights

1. **Non-Coding Activities Are Invisible in Most Plans**  
   Engineers cannot spend 100% of time coding. Capacity models must account for meetings, code reviews, and administrative tasks. Teams that "block out operational time" are more realistic about available bandwidth.

2. **Developer Experience Drives Productivity**  
   "When engineers have a good developer experience, meaning they feel their time is valued and their workload is manageable, it fosters a more positive and productive work environment." Capacity planning is not just about throughput—it signals respect for team health.

3. **Consequences of Misalignment Are Concrete**  
   - Project delays and missed deadlines
   - Strain on existing resources leading to burnout
   - Reputation damage when commitments aren't met

4. **Critical Metrics for Visibility**  
   - Resource utilization rates (to avoid under/over-allocation)
   - Cycle time and sprint velocity (for performance tracking)
   - Skill inventory across the team (to identify bottlenecks)

5. **Burnout Prevention Through Realism**  
   Capacity planning prevents overwork by distributing realistic workload and supporting "team health and morale" through explicit slack.

### Distinctive Value
This source emphasizes the *cultural* and *emotional* dimensions of capacity planning—how it signals respect and impacts team health—which appeals to CTOs thinking about retention.

### Gaps or Weaknesses
- Does not deeply explore the specific mechanisms of how unplanned work disrupts planned capacity
- Limited on WIP limits or Kanban-style interventions
- No data on the financial cost of burnout-driven attrition

---

## Source 2: Milestone – Engineering Capacity Planning Explained (2026)

**URL:** https://mstone.ai/blog/engineering-capacity-planning-explained/

### Core Thesis
Most engineering teams fundamentally misunderstand capacity planning by pursuing unsustainable 100% utilization rates. Organizations planning for 70–80% capacity while accounting for context-switching, unplanned work, and collaboration overhead deliver better results and prevent burnout.

### Key Insights

1. **The 70–80% Rule Is Real Data**  
   "Teams running at 70–80% capacity often outperform those pushed to 100%, delivering more reliable estimates and maintaining higher quality." This contradicts the intuition that full utilization = maximum output.

2. **Context-Switching Cost: 20% Productivity Loss Per Switch**  
   Engineers lose up to 20% productivity when switching between tasks. Yet most capacity plans ignore this reality, assuming continuous coding focus. For an AI-native team multitasking between model training, code, and manual verification, this cost is likely *higher*.

3. **Hidden Unplanned Work: 30–50% of Engineering Time**  
   Organizations allocate only planned feature work but encounter:
   - Production incidents
   - Critical bugs
   - Technical debt paydown
   - Unbudgeted urgent requests
   
   Despite allocating 30–50% of time to these, teams rarely model them in capacity planning.

4. **Recommended Work Distribution Model**  
   - 50–60% planned features
   - 15–20% bug fixes
   - 10–15% unplanned support
   - 10% learning and growth
   - 5–10% buffer/slack

   This is a practical allocation framework CTOs can use immediately to reset expectations.

5. **WIP Limits as a Direct Countermeasure**  
   Kanban-inspired work-in-progress restrictions reduce multitasking and context-switching while improving completion rates and predictability. This is the actionable intervention for overloaded teams.

### Distinctive Value
This source provides **concrete numbers, a specific work distribution model, and names WIP limits as the solution**. It directly addresses the "how do we fix 100% utilization?" question.

### Gaps or Weaknesses
- Does not deeply explore how to *measure* unplanned work in practice (what systems capture it?)
- Limited on how WIP limits interact with collaborative or interrupt-driven work
- No case study or empirical validation of the 70–80% rule in the source itself

---

## Source 3: Worklytics – How to Measure and Improve Software Engineering Productivity

**URL:** https://www.worklytics.co/blog/how-to-measure-and-improve-software-engineering-productivity/

### Core Thesis
Engineering productivity directly impacts business performance. Organizations measuring and optimizing across multiple dimensions—delivery speed, code quality, collaboration, reliability, and developer experience—unlock significant competitive advantages. High-performing teams "generate revenue growth four to five times faster than competitors."

### Key Insights

1. **Developers Lose 40–60% of Productive Time to Process Friction**  
   Invisible delays include:
   - Waiting on code reviews
   - Environment setup delays
   - Unclear requirements
   - Context switching
   - Excessive meetings
   - Manual processes
   
   This is more severe than the 20% context-switching cost; it captures systemic workflow problems.

2. **Single Interruption: 20–30 Minutes Recovery Time**  
   A single interruption (Slack, ping, request) requires "20 to 30 minutes of recovery time." Frequent context switching can "double or triple delivery time for even simple tasks." For AI-native teams doing long-running experiments, this is catastrophic.

3. **The Measurement Gap in Software**  
   Software development has been "perennially undermeasured" compared to other business functions, lacking standardized performance indicators. Many organizations don't even know where time goes.

4. **Bottlenecks Are Often Process, Not Capacity**  
   "Tasks require only four hours of actual work but sit queued for four days," indicating process rather than capacity problems. Fixing the bottleneck is cheaper than adding headcount.

5. **Financial Impact: 4–5x Revenue Growth in High-Performing Teams**  
   High-performing engineering teams generate revenue growth four to five times faster than competitors, alongside stronger innovation and shareholder returns.

6. **Persistent After-Hours Work Signals Burnout Risk**  
   Measuring after-hours work activity (PRs reviewed at midnight, commits at 2am) is an early warning system for burnout. This is a leading indicator of team health.

### Distinctive Value
This source bridges **productivity measurement to business impact** and names specific, observable metrics (PR cycle time, focus time, after-hours activity). It reframes the capacity problem as a *process optimization* problem, not a "work harder" problem.

### Gaps or Weaknesses
- Does not provide detailed implementation guidance for measuring focus time or interruptions
- The 40–60% figure is striking but not attributed to a specific study
- Does not address WIP limits or interventions specific to capacity constraints

---

## Cross-Source Synthesis

### Consistent Claims
1. **100% utilization is unsustainable.** All three sources converge on 70–80% as optimal.
2. **Hidden costs are massive:** 20–60% of time is lost to context-switching, unplanned work, and process friction.
3. **Burnout is predictable and measurable.** Poor capacity planning and after-hours activity are leading indicators.
4. **Process optimization beats headcount.** Fixing bottlenecks (reviews, unclear requirements) often delivers faster results than hiring.

### Data Points Summary
| Metric | Source | Finding |
|--------|--------|---------|
| Optimal utilization | Milestone | 70–80% (outperforms 100%) |
| Context-switching cost | Milestone | 20% productivity loss per switch |
| Unplanned work | Milestone | 30–50% of engineering time |
| Interruption recovery | Worklytics | 20–30 minutes per interruption |
| Productive time lost | Worklytics | 40–60% to friction (reviews, setup, unclear requirements) |
| Revenue multiplier | Worklytics | 4–5x faster growth in high-performing teams |

### Recommended Work Distribution (from Milestone)
- 50–60% planned features
- 15–20% bug fixes
- 10–15% unplanned support
- 10% learning and growth
- 5–10% buffer

---

## Critical Angles for AI-Native Engineering Teams

These sources were written for general software engineering but have specific implications for AI-native teams:

### 1. Context-Switching Is Amplified
AI projects involve rapid experimentation, model training, and manual verification. Context-switching between a training run (2-hour wait) and code review can fragment focus severely. The 20% cost is a floor, not a ceiling.

### 2. Unplanned Work Is Higher
Production incidents in AI systems (model drift, unexpected output, compliance failures) may be harder to predict than in traditional software. The 30–50% unplanned work estimate may understate reality.

### 3. WIP Limits May Require Rethinking
Traditional WIP limits (e.g., max 3 tasks in progress) assume fast feedback loops. AI projects with multi-day training runs need different WIP strategies—perhaps limiting *human* work-in-progress while experiments run asynchronously.

### 4. Burnout Risk Is High
"Rapid iteration," "move fast," and "experiment constantly" can mask 100% utilization. AI teams may feel productive (running lots of experiments) while burning out (no time for reflection, integration, or technical debt).

### 5. After-Hours Activity Is a Leading Indicator
Monitoring for late-night commits, reviews, and Slack activity is especially critical for AI teams working across time zones or managing long-running jobs.

---

## Gaps and Weaknesses Across Sources

1. **No WIP Limit Implementation Details**  
   Milestone names WIP limits as a solution but doesn't explain how to implement them in a CI/CD or experiment-driven context.

2. **Limited Empirical Validation**  
   The 70–80% rule and 40–60% productivity loss figures are cited as facts but lack attribution to peer-reviewed research or large-scale studies.

3. **Measurement Infrastructure Underspecified**  
   Worklytics emphasizes measuring focus time and after-hours activity but doesn't detail how to capture these without surveillance tools.

4. **No AI-Specific Adaptation**  
   All sources assume traditional feature-flag and sprint-based development. AI-native workflows (experimentation, model training, async verification) are not addressed.

5. **Missing CTO Playbook**  
   None of the sources provide a step-by-step path for a CTO to assess current utilization, communicate the problem to leadership, and implement WIP limits in a growth-stage org.

---

## Recommendations for Further Research

To deepen this topic for a CTO audience, seek:

1. **Case studies** of organizations that dropped from 90%+ to 70–80% utilization and measured the impact (velocity, quality, retention, revenue).
2. **Adaptation guides** for WIP limits in async, experiment-driven, or AI-native teams.
3. **Measurement tooling** comparisons (how to track focus time, interruptions, and after-hours activity without invasive surveillance).
4. **Economic models** showing the cost of burnout-driven attrition vs. the cost of planned slack.
5. **AI-native workflow case studies** (e.g., how high-performing ML teams at scale structure their work, WIP limits, and capacity).

---

## Sources Cited

- [Jellyfish: Engineering Capacity Planning](https://jellyfish.co/blog/engineering-capacity-planning/)
- [Milestone: Engineering Capacity Planning Explained (2026)](https://mstone.ai/blog/engineering-capacity-planning-explained/)
- [Worklytics: How to Measure and Improve Software Engineering Productivity](https://www.worklytics.co/blog/how-to-measure-and-improve-software-engineering-productivity/)
