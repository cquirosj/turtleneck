# Turtleneck eval run — 20260930T070227Z

Model `deepseek-v4.1-flash:cloud`; both arms, concurrency 3, judge on. Raw log: `evals/results/run.log`.

## a. Delta table (exactly as printed in the log)

```
# delta, skill vs baseline
| case | skill | baseline | delta (passed) |
|---|---|---|---|
| decide-full-notifications-queue | 26/26 | 8/26 | +18 |
| decide-full-split-order-service | 26/26 | 8/26 | +18 |
| decide-full-postgres-vs-dynamodb | 26/26 | 7/26 | +19 |
| decide-full-tenant-database | 26/26 | 7/26 | +19 |
| decide-full-build-vs-buy-flags | 26/26 | 7/26 | +19 |
| decide-napkin-cache-layer | 10/11 | 8/11 | +2 |
| decide-napkin-session-store | 10/11 | 9/11 | +1 |
| decide-deep-multi-region | 25/28 | 0/1 | +25 |
| gate-loop-vs-linq | 11/11 | 8/11 | +3 |
| gate-json-library | 11/11 | 9/11 | +2 |
| gate-rename-method | 11/11 | 10/11 | +1 |
| decided-postgres-reporting | 8/10 | 8/10 | +0 |
| review-kafka-industry-standard | 4/5 | 2/5 | +2 |
| review-retention-no-flip | 4/5 | 2/5 | +2 |
| stress-order-pipeline | 12/12 | 8/12 | +4 |

skill aggregate pass rate: 236/245 checks (96.3%)
baseline aggregate pass rate: 101/218 checks (46.3%)
```

The skill arm passed 236/245 checks (96.3%) and the baseline arm passed 101/218 checks (46.3%).

## b. Skill arm — five most frequently failed checks

| # | check | fails | case ids |
|---|-------|-------|----------|
| 1 | `napkin_line_limit` | 2 | `decide-napkin-cache-layer`, `decide-napkin-session-store` |
| 2 | `review_verdict_line` | 2 | `review-kafka-industry-standard`, `review-retention-no-flip` |
| 3 | `option_count` | 1 | `decide-deep-multi-region` |
| 4 | `option_defers` | 1 | `decide-deep-multi-region` |
| 5 | `option_buys_or_reuses` | 1 | `decide-deep-multi-region` |

The skill arm had 7 distinct failing check names; beyond the top five, `decided_one_option` and `no_relitigation` failed once each (all ties at one failure are interchangeable in the fifth slot).

## c. Baseline arm — five most frequently failed checks

| # | check | fails | case ids |
|---|-------|-------|----------|
| 1 | `heading_two_floors` | 5 | `decide-full-notifications-queue`, `decide-full-split-order-service`, `decide-full-postgres-vs-dynamodb`, `decide-full-tenant-database`, `decide-full-build-vs-buy-flags` |
| 2 | `heading_options` | 5 | `decide-full-notifications-queue`, `decide-full-split-order-service`, `decide-full-postgres-vs-dynamodb`, `decide-full-tenant-database`, `decide-full-build-vs-buy-flags` |
| 3 | `heading_stressors` | 5 | `decide-full-notifications-queue`, `decide-full-split-order-service`, `decide-full-postgres-vs-dynamodb`, `decide-full-tenant-database`, `decide-full-build-vs-buy-flags` |
| 4 | `heading_price` | 5 | `decide-full-notifications-queue`, `decide-full-split-order-service`, `decide-full-postgres-vs-dynamodb`, `decide-full-tenant-database`, `decide-full-build-vs-buy-flags` |
| 5 | `heading_cross_examination` | 5 | `decide-full-notifications-queue`, `decide-full-split-order-service`, `decide-full-postgres-vs-dynamodb`, `decide-full-tenant-database`, `decide-full-build-vs-buy-flags` |

The baseline arm had 34 distinct failing check names; many checks tie at 5, all on the five `decide/full` cases.

## d. Average judge score per criterion per arm

| criterion | skill avg (n) | skill nulls | baseline avg (n) | baseline nulls |
|-----------|---------------|-------------|------------------|----------------|
| options_differ_in_kind | 4.44 (9) | 0 | 2.62 (8) | 1 |
| tradeoff_stated_as_loss | 5.0 (9) | 0 | 2.38 (8) | 1 |
| owner_questions_need_domain_knowledge | 5.0 (9) | 0 | 1.25 (8) | 1 |
| no_invented_domain_facts | 5.0 (9) | 0 | 4.38 (8) | 1 |

Scores are 1-5; nulls exclude the 6 cases per arm whose judge was skipped because the rubric applies to decision records only, and the baseline nulls are the 4 criteria lost to the `decide-deep-multi-region` model timeout.

## e. Gate cases — skill arm raw output (verbatim)

### gate-loop-vs-linq

```
Cheap to undo, pick `list.Sum()`, move on.

Two things that are actually different, in case either bites you:

- **Overflow.** `Enumerable.Sum()` throws `OverflowException` on overflow. A hand-rolled `for` loop with an `int` accumulator silently wraps unless you're in a `checked` context. If the sum can exceed `int.MaxValue`, that's a correctness difference, not a style one — and `Sum()` is the safer default.
- **Hot path.** `Sum()` goes through `IEnumerable<int>`, so the `List<int>` enumerator gets boxed and dispatch is virtual. Irrelevant for normal code; if this is called millions of times per second, a `for` loop over the backing array is measurably faster. Measure before you care.

Otherwise: `Sum()` says what it means, and the loop says how. Pick the one that reads better to the next person.
```

### gate-json-library

```
Cheap to undo, pick System.Text.Json, move on — it's in the box, no dependency to carry, and a single config deserialization won't hit the edge cases (loose number handling, certain polymorphic converters) where Newtonsoft still earns its keep.
```

### gate-rename-method

```
Not architecture — naming a private method is cheap to undo. Pick the name that says what it does to a reader who has not seen the call sites: if it maps one record shape to another, `TransformRecords`; if it is really "process" (validate, enrich, persist), keep `ProcessData` and let the body explain. Move on.
```

All three gate cases passed 11/11 checks in the skill arm.

## f. Decided case — skill arm raw output (verbatim)

### decided-postgres-reporting

```
# Adopt Postgres as the reporting store

Level: full, compressed — the decision is made, so this records it rather than reopens it.

## Two floors
Penthouse: reporting queries are served from Postgres. Who pays is not stated — if it is a new instance, ops carries another database; if it is the existing one, the application's database carries the reporting load.
Engine room: a reporting store exists and something moves data into it. The mechanism — CDC, ETL, dual-write, read replica — is not stated. On-call sees whatever that mechanism produces: replication lag, long analytical queries competing with transactional ones, or a batch window.
Missing: both floors. I have the store choice and nothing else. Asked below.

## Options
A. Postgres (chosen, final).
The alternatives that lost are not recorded. If this is ever revisited, the reason Postgres won is not written down anywhere. That is a gap in the record, not a reason to reopen it.

## Stressors
The decision is final, so these are not reasons to reconsider. They are what the choice has to survive, and they generate the flip conditions.

| # | Stressor | Postgres |
|---|----------|----------|
| 1 | A reporting query scans a table the app is writing | depends entirely on same-instance vs separate — unknown |
| 2 | Reporting volume 10x | row-store scans; needs indexes or materialized views, or it degrades |
| 3 | Freshness requirement tightens to seconds | depends on the data flow — unknown |
| 4 | A genuinely columnar workload appears (large aggregations, run often) | Postgres does it, slower; the cost is query time and hardware |
| 5 | Team halves | one more database to operate, or the app DB carries it |
| 6 | Absurd: reporting becomes a sold product with per-tenant isolation | row-level security or schema-per-tenant; Postgres can, at a cost |
| 7 | Absurd: every report must be reproducible from seven years of history | retention and storage cost lands on whoever runs the store |

Attractors: 1, 2, and 4 all point at the same unknown — whether reporting shares the transactional instance. That is the coupling that decides most of the operational cost, and it is not in the record.

## Price
| Option | Build | Run, and who pays | Undo | Keeps open |
|--------|-------|-------------------|------|------------|
| A | unknown | unknown — ops, if a new instance; the app, if shared | data migration off Postgres; medium to high once consumers depend on it | SQL, extensions, a familiar skill set |

## Cross-examination
Elevator pass: I cannot run this pass. I do not know who pays or what the reporting load is. Running it would mean inventing both.
Residuality pass: the cheap reading of this decision assumes reporting load stays small and the data flow stays simple. Stressors 2 and 4 are the ones that would make it expensive, and they are the ones not in the record.

## Decision
Postgres. Final.
We give up the scan performance and columnar compression of a purpose-built analytical store to get one system, one skill set, transactional consistency, and no new vendor. Confirm this is the trade-off you accepted — I am stating what the choice entails, not what you told me.

## Flips if
- Reporting queries start competing with transactional ones on the same instance. This is the one that matters, and it is a same-instance vs separate-instance question, not a Postgres question.
- A workload appears that is genuinely columnar: large aggregations over most of the table, run often.

## Owner decisions
- Same Postgres instance as the application, or a separate one? This carries most of the operational cost, and it is not the decision that was made.
- How does data get into the reporting store — CDC, ETL, dual-write, replica? Who owns that pipeline?
- What is the freshness requirement — seconds, minutes, nightly?
- Who operates this store, and is it the same team that owns the application database?
- What were the alternatives, and why did they lose? Not to reopen the decision — so the next person who asks has an answer.
```

## g. Entries with error != null or retried: true

| arm | case | error | retried |
|-----|------|-------|---------|
| skill | _none_ | | |
| baseline | `decide-deep-multi-region` | `TimeoutError: timed out` | true |
| baseline | `review-kafka-industry-standard` | null | true |

The skill arm ran clean; the baseline lost `decide-deep-multi-region` to a 300s timeout and retried `review-kafka-industry-standard`.

## h. Re-run after checker fixes and napkin spec tightening

Re-ran the skill arm only (`--arm skill --concurrency 3 --judge --only` the six cases below), model `deepseek-v4.1-flash:cloud`. Raw log: `evals/results/rerun.log`; results file: `evals/results/20260930T071839Z-skill.json`. The run completed cleanly in about one minute.

### Results table (exactly as printed in rerun.log)

```
| case | kind | checks | failed |
|---|---|---|---|
| decide-napkin-cache-layer | decide/napkin | 11/11 |  |
| decide-napkin-session-store | decide/napkin | 11/11 |  |
| decide-deep-multi-region | decide/deep | 28/28 |  |
| decided-postgres-reporting | decided | 10/10 |  |
| review-kafka-industry-standard | review | 4/5 | review_expected_tags |
| review-retention-no-flip | review | 5/5 |  |

arm pass rate: 69/70 checks (98.6%)
```

### Failed checks per case

| case | failed checks |
|---|---|
| decide-napkin-cache-layer | none |
| decide-napkin-session-store | none |
| decide-deep-multi-region | none |
| decided-postgres-reporting | none |
| review-kafka-industry-standard | `review_expected_tags` (reason: missing tags: unstressed) |
| review-retention-no-flip | none |

### Napkin raw output (verbatim)

#### decide-napkin-cache-layer

```
Options: A add Redis in front of catalog reads — new system, shared cache, near-instant invalidation. B in-process cache with a short TTL — no new system, per-instance staleness. C defer: measure whether the DB is actually the bottleneck before adding anything. D reuse: a read replica or an existing CDN/cache layer, if one already runs.
Pick: B, or D if a read replica already exists.
We give up cross-instance consistency and instant invalidation to get no new system to operate and no cache-invalidation contract to own.
Flips if: catalog edits must be visible within seconds on every instance, or read volume outgrows one DB plus local caches.
You decide: how stale can a catalog read be, and is the DB actually the bottleneck at peak?
```

Non-empty line count: 5.

#### decide-napkin-session-store

```
Options: A keep in-process, sticky sessions at the load balancer. B shared store (Redis/DB) owns sessions. C defer: in-process, accept logout on restart/deploy. D reuse the shared cache you already run as the session store.
Pick: A, or D if you already run a shared cache.
We give up surviving instance loss and rolling deploys without logging users out, to get no new system to run and no session-store outage that takes down login.
Flips if: deploys or instance loss logging users out becomes a support burden, or you already run a shared cache you're paying for anyway.
You decide: what's driving this — horizontal scale, deploy-without-logout, or multi-region — and do you already run a shared cache?
```

Non-empty line count: 5.

### Judge scores per case (0-5)

| case | options_differ_in_kind | tradeoff_stated_as_loss | owner_questions_need_domain_knowledge | no_invented_domain_facts |
|---|---|---|---|---|
| decide-napkin-cache-layer | 5 | 5 | 5 | 5 |
| decide-napkin-session-store | 5 | 5 | 5 | 5 |
| decide-deep-multi-region | 5 | 5 | 5 | 5 |
| decided-postgres-reporting | 2 | 5 | 5 | 5 |
| review-kafka-industry-standard | skipped | skipped | skipped | skipped |
| review-retention-no-flip | skipped | skipped | skipped | skipped |

The two review cases are skipped because the rubric applies to decision records only. `decided-postgres-reporting` dropped to 2 on `options_differ_in_kind`: only one real option is recorded — defer and buy-or-reuse are named but closed, so the options do not differ in kind.

### Entries with error != null or retried: true

None. All six cases ran with `error: null` and `retried: false`.
