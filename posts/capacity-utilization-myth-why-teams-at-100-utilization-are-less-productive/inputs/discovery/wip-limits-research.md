# Kanban WIP Limits: Research Summary

## Overview

This research examines real-world implementations of Work-in-Progress (WIP) limits in engineering teams, focusing on the mechanisms by which constraining concurrent work improves delivery velocity, team health, and quality outcomes. Three substantive sources provide case studies, quantitative results, and implementation frameworks.

---

## Source 1: Medium Case Study—Elixir Radar Project

**Author:** Lucas Colucci  
**URL:** https://medium.com/@lucasrcolucci/case-study-of-a-wip-limit-implementation-why-when-and-how-to-use-wip-limits-6eed10f92209

### Core Thesis

WIP limits are essential for Kanban flow optimization, but no universal formula exists for determining optimal limits. Implementation requires empirical measurement, team-specific experimentation, and iterative refinement.

### Key Insights & Frameworks

1. **Lead Time Visibility Through Queues**  
   The team discovered that tasks were "staying too much time on queues"—a bottleneck invisible through simple board observation. This reveals a critical blindness in unmetered workflows: process delays accumulate in wait states, not execution.

2. **Two Calibration Strategies**  
   - **Floor approach:** Start with deliberately restrictive limits (e.g., 1 per person), incrementally increase as pain emerges  
   - **Ceiling approach:** Begin with generous limits, gradually tighten until the constraint becomes visible  
   Both strategies acknowledge that optimal WIP is context-dependent and requires teams to "feel the pain" of miscalibration before adjusting.

3. **Cumulative Flow Diagrams as Primary Diagnostic**  
   CFD charts revealed exactly where work was stalling (e.g., "Ready to UX" queue). This enabled precision debugging—not all queues are equally expensive; the team could target specific bottleneck stages for WIP reduction.

### Case Study Details: Progressive Implementation

The Elixir Radar project refined WIP limits across multiple iterations:

| Stage | Initial Limit | Rationale | Refinement |
|-------|---|---|---|
| UX Column | 1 | Match headcount | Stable |
| Dev Column | 1 | Match headcount | Stable |
| Queue (Ready to UX) | 2 | Parallel processing capacity | **Reduced to 1** after bottleneck shift observed |
| Queue (Ready to Dev) | 2 | Parallel processing capacity | Stable |
| Input Column | 2 | Weekly team throughput | Stable |

### Quantitative Results

- **6% flow efficiency improvement** (ratio of touch time to total lead time)
- Measurable reduction in queue wait times (validated on CFD charts)
- Elimination of unnecessary refining ceremonies—demand-driven scheduling replaced time-boxed ceremonies
- Enhanced task prioritization for multi-project team members (fewer context-switch penalties)

### Implementation Challenges & Gaps

- **No predetermined formula:** Organizations cannot math their way to optimal WIP; empiricism is non-negotiable.
- **J-curve unpredictability:** Improvement visibility is non-linear; teams may not see benefits until several weeks of calibration.
- **Late-stage adoption risk:** WIP discipline is harder to impose on teams already habituated to multitasking and high concurrency.

---

## Source 2: DEV Community Case Study—Service Classes & Multi-Service Workflow

**Author:** zerocodilla  
**URL:** https://dev.to/zerocodilla/may-kanban-be-with-you-practical-case-study-3bjd

### Core Thesis

Kanban adaptation requires addressing team-specific pain points through incremental improvements rather than rigid framework adoption. WIP limits combined with service classes enable self-directed task selection, eliminate estimation overhead, and fundamentally shift organizational responsiveness.

### Key Insights & Frameworks

1. **Service Classes as WIP Steering Mechanism**  
   The team established five priority tiers—"Expedite," "Fixed Date," "Standard," "Bugs," "Intangible"—enabling developers to self-select appropriate work without managerial intervention. Each service class carries implicit urgency signals that replace meeting-based prioritization. This decouples WIP limit enforcement from blocking decisions.

2. **Stage-Specific WIP Caps Prevent Systemic Bottlenecks**  
   Rather than uniform limits across all columns, the team applied differentiated caps:
   - Kick-off: 2 items (intake gating)
   - Review: 3 items (parallel review capacity)
   - Ready: 6 items (downstream buffer before active work)
   
   This stagewise approach allows high WIP in preparatory phases while protecting execution and review stages from overload.

3. **Backlog Refining as a Gated Upstream Process**  
   The team inherited an 800+ task backlog—a pathology that no WIP limit alone can solve. By implementing structured intake (Kick-off stage with limit of 2), they could maintain a refined backlog of ~75 tasks, reducing cognitive load and improving decision quality downstream.

4. **Decoupling Release Cadence from Iteration Length**  
   Multiple service classes shifted from three-week iterations to on-demand releases (Expedite) or five-day releases (Fixed Date). This indicates that WIP limits + service classes enable true continuous delivery rather than batch-release cycles.

### Quantitative Results

- **Lead time improvement: 65%** (12 weeks → 4 weeks)  
  This metric is particularly powerful because it captures end-to-end delivery time, not just task completion rate.
  
- **Backlog reduction: 91%** (800+ tasks → 75 tasks)  
  Demonstrates that WIP discipline forces ruthless prioritization upstream, eliminating waste in the planning phase.
  
- **Specific service improvement: 86%** (for one licensing request category)  
  Shows that service classes can drive dramatic improvements in category-specific responsiveness.

- **Coordination cost reduction**  
  The team eliminated multi-person decision committees and replaced them with demand-driven, service-class-based selection. This directly reduces overhead that inflates lead time.

### Implementation Challenges & Gaps

- **Framework overwhelm risk:** The author initially found STATIK (Systems Thinking Approach to Kanban) framework "overwhelming and impractical." This suggests that practitioners need lightweight, incremental starting points rather than comprehensive frameworks.
- **Backlog debt:** High WIP historically masks backlog bloat. Teams need explicit intake gates (not just execution limits) to prevent hidden capacity loss.
- **Stakeholder misalignment:** An 8-person decision committee was a governance failure, not a WIP problem. WIP limits require organizational will to enforce prioritization.

---

## Source 3: BusinessMap Guide—Comparative Case Studies & Implementation Approaches

**URL:** https://businessmap.io/kanban-resources/getting-started/what-is-wip

### Core Thesis

WIP limits restrict maximum concurrent work items per workflow stage, enforcing a pull-based discipline that improves quality and delivery performance. Five distinct implementation approaches exist, each suited to different organizational structures and team compositions.

### Key Insights & Frameworks

1. **Five Distinct WIP Implementation Methods**

   | Method | Mechanism | Typical Application |
   |--------|-----------|---------------------|
   | Per-person limits | Based on individual weekly throughput | Small teams, distributed work |
   | Team-based limits | Aggregate historical throughput | Homogeneous teams with shared backlog |
   | CONWIP (Constant WIP) | Total limit across all sub-columns in a stage | Mature Kanban with detailed stage breakdown |
   | Activity-based limits | Applied by work type (bugs vs. features vs. requests) | Mixed-severity work environments |
   | Upstream limits | Controls new work entering system | Intake-heavy organizations with stakeholder overload |

2. **Recommended Starting Rule: Team Size + 1**  
   WIP limit = (number of team members) + 1  
   This simple heuristic provides a baseline that accounts for minor idle time while preventing extreme multitasking. It's a ceiling approach designed to be refined downward through observation.

3. **The WIP Limits Paradox**  
   - **Too high:** Multitasking penalties, missed deadlines, cognitive overload (100% utilization trap)  
   - **Too low:** Team idleness when work stalls (artificial bottlenecks), demotivation  
   
   Optimal WIP is the intersection where throughput is maximized without imposing idle periods or unsustainable utilization. This is inherently dynamic and requires continuous KPI monitoring.

4. **Bottleneck Revelation as Primary Benefit**  
   Unlike metrics-based process improvement, WIP limits expose bottlenecks automatically. When work accumulates at a stage, the constraint becomes undeniable. This transparency is more powerful than periodic reporting because it creates synchronous, team-level awareness of process failures.

### Quantitative Results: Named Case Studies

**Aerosud IT Team:**  
- Baseline: 60 tickets/week  
- Implementation: Per-person WIP limits  
- Result: **Doubled throughput to 120 tickets/week in three days**  
- Implication: 100% utilization was masking severe multitasking penalties and context-switching overhead. The constraint removal (WIP limits preventing overload) immediately unlocked 2x capacity.

**Flapper Engineering:**  
- Approach: Strategic WIP management at 80 items/week  
- Result: Described as "leaner, faster, and more efficient workflow"  
- Context: High-volume item processing improved through capacity discipline.

### Implementation Challenges & Gaps

- **WIP Limits Paradox requires active governance:** Simply setting limits is insufficient; teams must monitor KPIs (throughput, lead time, cycle time) continuously and adjust limits quarterly or when process changes occur.
- **Hidden costs of high utilization not quantified:** While Aerosud's 2x improvement is striking, the research doesn't separate efficiency gains from quality improvements or burnout reduction—each likely contributed.
- **Applicability varies by work distribution:** Per-person limits work well for homogeneous work; activity-based limits are necessary when bug fixes, features, and requests have different lead times and team assignments.

---

## Synthesis: Critical Findings for CTOs

### 1. **100% Utilization is a Visible Pathology**  
The Aerosud case (60→120 tickets/week in three days) directly demonstrates that teams reporting 100% utilization are actually constrained by WIP limits, not capacity scarcity. The hidden costs—multitasking, context switching, cognitive load—compound to reduce effective output. WIP limits convert this invisible waste into visible process constraints that can be addressed.

### 2. **Lead Time is the Right Metric, Not Throughput**  
While throughput (tickets/week) is easy to measure, the 65% lead time improvement in the DEV Community case shows that what matters to customers and stakeholders is *how long delivery takes*, not how many items the team processes. WIP limits improve lead time by reducing queue wait time (the dominant lead time component in high-concurrency workflows).

### 3. **WIP Limits Require Organizational Discipline, Not Just Engineering Practice**  
- The DEV Community team inherited an 800+ task backlog, which no WIP limit could fix alone.  
- The Elixir Radar team needed CFD charts and weekly reviews to calibrate limits correctly.  
- Both teams required explicit decision-making about intake gates and service class prioritization.  

WIP limits are a governance tool, not just a Kanban mechanism.

### 4. **Optimal WIP is Team- and Context-Specific; No Formula Exists**  
Despite Little's Law and queuing theory, real implementations show that calibration requires experimentation:  
- Start with (team size + 1) as a ceiling.  
- Use floor approach if you suspect high utilization (start low, increase gradually).  
- Use ceiling approach if you suspect high idle time (start high, decrease gradually).  
- Monitor CFD charts weekly for 4-8 weeks before finalizing limits.  
- Expect limits to drift as team composition and work mix change.

### 5. **Service Classes Enable WIP Limits to Work Across Mixed-Priority Work**  
The five-tier service class system (Expedite, Fixed Date, Standard, Bugs, Intangible) allows different WIP limits per priority level without explicit manager intervention. This is especially powerful for AI-native teams managing interrupt-driven work (support, debugging) alongside planned features.

### 6. **Throughput Gains Are Real, But Come with Caveats**  
- **Documented 2x improvement** (Aerosud): Suggests 50% of effort was context-switching and multitasking overhead.  
- **Documented 65% lead time improvement** (DEV Community): More realistic; reflects 6% flow efficiency gain + 59% from reduced queue wait.  
- **Documented 6% flow efficiency gain** (Elixir Radar): Conservative; reflects true touch-time optimization.  

The range (6–100% improvement) depends heavily on baseline utilization and work type. Teams starting from 100% utilization will see larger gains; teams at 70–80% utilization will see modest gains.

### 7. **Burnout and Quality Improvements Are Not Quantified in These Studies**  
All three sources focus on throughput and lead time. The business impact of reduced burnout (lower turnover, higher code quality, fewer production incidents) is claimed but not measured. For CTOs managing AI-native teams, this gap is significant—these teams are likely to experience higher context-switching penalties because of interrupt-driven AI-assistance use cases.

---

## Recommendations for Immediate Implementation

1. **Baseline current utilization:** Survey team members on multitasking frequency and time spent in meetings vs. focused work.
2. **Start with (team size + 1) WIP limit** across your primary execution column (e.g., "In Development").
3. **Implement CFD charting:** Track lead time, cycle time, and queue depth weekly for 8 weeks.
4. **Add service classes** for interrupt-driven work (e.g., "Production Issue," "AI Assistance Request").
5. **Measure lead time before and after**, not just throughput. Lead time is the metric stakeholders actually care about.
6. **Review limits quarterly** or after team size changes. Optimal WIP drifts over time.

---

## References

- Colucci, L. (n.d.). "Case Study of a WIP Limit Implementation: Why, When and How to use WIP Limits." *Medium*. https://medium.com/@lucasrcolucci/case-study-of-a-wip-limit-implementation-why-when-and-how-to-use-wip-limits-6eed10f92209

- zerocodilla (n.d.). "May Kanban Be With You: Practical Case Study." *DEV Community*. https://dev.to/zerocodilla/may-kanban-be-with-you-practical-case-study-3bjd

- BusinessMap (n.d.). "WIP Limits in Kanban: Optimize Flow & Boost Team Throughput." *BusinessMap*. https://businessmap.io/kanban-resources/getting-started/what-is-wip
