# Example: Make the Grade

An architectural kata by Neal Ford and Ted Neward, worked with the turtleneck
skill at full level. Unedited model output.

- Model: `deepseek-v4.1-flash:cloud`, temperature 0
- Skill commit: `46dd375`
- Judge: `claude-bridge/claude-sonnet-5`, 48/50 on the kata quality rubric
- Strongest line per the judge: Stressors 3 and 12 both break the word 'frozen': the core must be frozen in shape (append-only, versioned), not in content.
- Weakest move per the judge: The brief's explicit reporting-by-school/teacher/student requirement is acknowledged once in the engine room and then dropped — no stressor or price line tests whether the chosen boundary actually supports that reporting granularity.

## The brief

# Make the Grade

A very large and populous state would like a new system to support standardized testing across all public school systems grades 3-12.

Users: 40,000+ students, 2000 graders, 50 administrators.

Requirements:
- Students will only be able to use the application within testing centers around the state, most of these will be in the schools, but not all of them
- Students should be able to take a test, and the results eventually consolidated to a single location representing all of the test scores across the state (by school, teacher, and student).
- Tests will be multiple choice, short answer, and essay.
- The system should have a reporting system to know which students have taken the tests and what score they received.
- Short answer and essay questions will be manually graded by teachers, who will then add the essay grades to the system.

Additional context:
- A change approval processes involving three different government agencies is required for changes to the way student grades are kept to ensure security.
- The state does not own its hosting center, but outsources it to a third party.
- Project must defend its budget each fiscal year.

## The record

# Where to draw the boundary around the grade-of-record, given three-agency change approval

Level: full

## Two floors
Penthouse: the state must run standardized tests for 40,000+ students, consolidate scores by school/teacher/student, and defend the budget every fiscal year. Taxpayers pay to build; the state pays the outsourced host and the ops team ongoing, and re-justifies the whole line each year. The outcome that matters: auditable scores the state can report, without a three-agency approval process blocking every improvement.
Engine room: a grade-of-record store, an ingestion path from testing centers, an auto-grading path for multiple choice, a manual grading workflow for 2000 graders, a consolidation/reporting layer. On-call sees: center connectivity failures during the window, grader queue backlog, consolidation lag, and a schema change that takes months because three agencies must sign it.
Missing: what exactly the three agencies approve (schema? retention? security controls?); number and timing of test windows; essay volume and grading deadline; whether an assessment vendor already exists; team size and the fiscal-year budget number. Asked, not invented.

## Options
A. Thin frozen grade-of-record + free periphery: a small append-only, versioned grade store behind a narrow write API; test delivery, grading workflow, and reporting all live outside it and change freely.
B. Federated capture, central consolidation: each center/district captures locally, the state consolidates asynchronously. Boundary sits at the district.
C. Defer: run one test window on the current process, instrument it, decide the architecture after real volumes and failure modes are known.
D. Buy an assessment platform, build only the state consolidation and grade store.

## Stressors
| # | Stressor | A | B | C | D |
|---|----------|---|---|---|---|
| 1 | All 40,000 students test in the same week | survives if periphery scales; core is append-only | survives, load spread to districts; consolidation lags | survives, no data | survives if vendor capacity holds; vendor is the limit |
| 2 | A testing center loses network mid-test | needs local buffering in periphery; core untouched | survives, that is the point | survives (paper) | assumed: vendor has an offline mode |
| 3 | The three agencies change the grade-keeping rule | core must change — the expensive path, by design; versioned so old data stays valid | same core problem, plus every district updates | no system to change yet | vendor must change their schema; state cannot force it — breaks |
| 4 | Outsourced host goes down a day / contract re-bid | core and periphery both migrate; a project | districts keep running, consolidation pauses | n/a | vendor's hosting; state has no lever |
| 5 | Essay volume 10x; 2000 graders cannot keep up | grading workflow is in periphery, scale it alone | same, plus district queues | existing process, same backlog | vendor's grading module; state cannot change it |
| 6 | A grader account is compromised, grades tampered | append-only, tamper-evident audit in core | many local stores to audit | n/a | vendor's audit; state cannot inspect |
| 7 | Audit: prove every score change for N years | append-only core is the answer | consolidation must preserve district provenance | n/a | vendor's retention; state cannot guarantee |
| 8 | Budget cut; project defunded a fiscal year | periphery pauses, core is small and cheap to keep | districts carry cost, state core cheap | cheapest | vendor license is a fixed annual line — hard to cut |
| 9 | A student's test is interrupted, must resume elsewhere | session state in periphery, not core | local capture makes cross-district resume hard | paper, manual | vendor's session model |
| 10 | Absurd: statewide network outage for a week during the window | fails unless periphery buffers offline | survives at the center | survives (paper) | fails unless vendor offline |
| 11 | Absurd: state sells the platform to other states | periphery reusable, core is state-specific | hard, districts are state-specific | n/a | vendor owns it; state cannot sell |
| 12 | Absurd: a "test" becomes a multi-session adaptive assessment | periphery changes, core stores a score — survives | same | n/a | vendor roadmap decides |

Attractors: 3, 6, 7 hit the grade store in every option — the grade-of-record is the coupling, and it is exactly what the three agencies control. 1, 5, 9, 10 hit the delivery/grading pipeline — the volatile part. The boundary wants to be between the frozen grade store and the volatile pipeline. Stressors 3 and 12 both break the word "frozen": the core must be frozen in *shape* (append-only, versioned), not in *content*.
Owner stressors, to confirm: a state legislator adds a subject or test format mid-year with a statutory deadline; a federal funding condition requires scores in a specific format by a specific date; some testing centers are community sites (libraries) with their own IT, not school-controlled.

## Price
Anchor: brief gives 40,000+ students, 2000 graders, 50 admins, three-agency approval, outsourced hosting, annual budget. Team size not given. `assumed: a state IT team of ~10 with an outsourced host, one main test window per year` — listed under owner decisions.
| Option | Build | Run, and who pays | Undo | Keeps open |
|--------|-------|-------------------|------|------------|
| A | medium; the expensive part is getting the frozen schema right once | host + state team; periphery changes are cheap | core change = three-agency process; periphery cheap | any grading workflow, reporting, or delivery change without touching the core |
| B | high; every center/district needs a local system | distributed ops; districts carry it, state team cannot run hundreds of sites | expensive; decommissioning local systems | offline resilience at the center, district autonomy |
| C | low now | existing process | cheap | the decision itself, at the cost of a year | 
| D | low-medium; integration only | vendor license, fixed annual line the state pays | expensive; vendor lock-in, data migration out | little; you get the vendor's roadmap |

## Cross-examination
Elevator pass: stressor 10 (offline week) — the penthouse does not care enough to pay for full offline; cut to "buffer at the center", optional. Stressor 11 (sell to other states) — speculative, cut unless the state says so. Stressor 2's offline buffering is worth paying for only at centers that actually lose network; asked which.
Residuality pass: A's "frozen core" price assumed we can freeze the schema correctly the first time; stressors 3 and 12 say we cannot, so re-priced the core as "frozen in shape, versioned, three-agency process is the cost of a content change." D's "cheap build" assumed the vendor's model fits the three-agency constraint; stressors 3, 6, 7 show the state cannot get approval over a vendor's roadmap — D is cheap only because the stressor list was polite about governance. B's offline resilience is real, but the run cost of operating hundreds of sites was understated.

## Decision
A, with D applied only to the periphery (test delivery), never to the grade-of-record.
We give up the ability to change the grade schema quickly (three-agency approval) to get a stable, auditable grade-of-record that the volatile parts can change around.
Also accepted: we operate the periphery ourselves rather than buying it, so we carry that ops cost.

## Flips if
- The three agencies' approval scope turns out to cover only retention and security, not the schema — then the core can change freely and A's main cost disappears.
- The state already owns an assessment platform or has a mandatory vendor — then D for the periphery becomes the default.
- Test windows turn out to be continuous year-round rather than one window — then the volume-spike stressor weakens and B's local capture loses its main justification.

## Owner decisions
- What exactly do the three agencies approve — schema, retention, security controls, or all three? This decides how frozen the core really is.
- Is there an existing assessment vendor or platform the state must use?
- How many test windows per year, and are they simultaneous statewide?
- What is the essay volume per window, and the grading deadline?
- Which of the three owner stressors hold, and which are missing?
- Team size and the fiscal-year budget number — the prices above are relative to the stated assumption.
