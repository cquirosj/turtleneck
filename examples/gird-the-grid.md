# Example: Gird the Grid

An architectural kata by Neal Ford and Ted Neward, worked with the turtleneck
skill at full level. Unedited model output.

- Model: `deepseek-v4.1-flash:cloud`, temperature 0
- Skill commit: `4e08ce6` (the skill text as committed there; the record was generated from that text just before the commit)
- Judge: `claude-bridge/claude-sonnet-5`, 47/50 on the kata quality rubric
- Strongest line per the judge: The coupling is operational data to the tenant boundary, not to the application.
- Weakest move per the judge: Four-nines reliability is an explicit brief requirement with direct tenancy implications (blast radius, per-instance vs shared failure domains) yet it's never analyzed or priced -- it rides along inside 'blast radius' stressors instead of being treated as its own driver.

## The brief

# Gird the Grid

A company who builds management software for electrical grids needs to update their outdated software solution, and plan to sell their offering as a platform.

Users: small to medium size market electic market companies, able to accommodate electrical grids from 100,000-1,900,000 electrical customers

Requirements:
- configurable for specific grid company characteristics (state, tax rates, etc.)
- state-of-the-art user experience
- dashboards with analytics reports with near-real time data from the grid
- excellent reporting capabilities
- sophisticated analytics-based engine to determine best throughput/money
- administer through either desktop or mobile devices
- security penetration attempt reporting

Additional context:
- Four nines (99.99) reliability
- turn-key deployment on remote sites
- security is a first-class concern
- company wants to shift from managing electrical grids to becoming a software reseller

## The record

# Choose the tenancy and deployment model for the grid platform

Level: full

## Two floors
Penthouse: the company stops selling grid operations and starts selling software. Revenue becomes per-tenant subscription; the cost that decides whether that is profitable is the cost to onboard a new grid company and the cost to run each one. The reseller pays to build and operate; the grid companies pay to subscribe. Ongoing cost is either N deployments or one shared platform — that choice is the whole margin.
Engine room: today's solution is (assumed) single-tenant and bespoke per customer. Becoming a platform means adding tenant isolation, a per-tenant config layer (state, tax rates, grid characteristics), telemetry ingestion, an analytics/optimization tier, and deployment automation. On-call either watches N sites with per-tenant version drift, or one cluster with a shared blast radius.
Missing: the current architecture, the current customer count, the team size, and — the load-bearing one — whether target grid companies will accept their operational data leaving their premises. Asked, not invented.

## Options
A. Per-tenant instance + shared control plane: each grid company gets its own data plane, provisioned and updated by a control plane; config and analytics shared.
B. Multi-tenant SaaS: one shared runtime, tenant isolation in the data layer, config-driven per tenant.
C. Defer: productize only the config layer and deployment automation on the current single-tenant codebase; keep bespoke; revisit tenancy when a customer demands it.
D. Buy or reuse: adopt an existing grid-domain platform (ADMS/DERMS vendor) or a multi-tenant SaaS framework plus a grid data model, and resell on top.

## Stressors
| # | Stressor | A | B | C | D |
|---|----------|---|---|---|---|
| 1 | A 1.9M-customer grid and a 100k-customer grid sign the same quarter | survives, two sized instances | survives, noisy-neighbor risk | survives, two bespoke builds | survives if vendor tiers allow |
| 2 | A state regulator demands operational data never leave the state | survives, instance in-state | breaks unless per-region sharding | survives | depends on vendor regions |
| 3 | A customer is acquired by a company already on a competitor's platform | export one instance | export one tenant | bespoke, painful | vendor migration path |
| 4 | One customer demands a feature only they need, or they leave | fork the instance | config flag or shared roadmap | already bespoke | vendor roadmap, you wait |
| 5 | One tenant's telemetry goes 10x during a storm | contained to that instance | shared tier starves others | contained | vendor tier limits |
| 6 | A penetration succeeds against one tenant; report must show blast radius | one instance | shared blast radius, isolation hard to prove | one instance | vendor's problem, your reputation |
| 7 | The company is acquired and must fold into the acquirer's suite | instances portable | platform portable | bespoke, hard | vendor lock |
| 8 | The team halves | N instances, no ops — trap | one platform, survivable | survivable | vendor carries ops |
| 9 | The analytics/optimization engine dependency is abandoned | swap per instance | swap once | swap per build | vendor's engine, you are stuck |
| 10 | Absurd: a remote site must run fully offline for a week | survives, local instance | breaks | survives | breaks |
| 11 | Absurd: the platform is sold to the customers' competitors, who are also tenants | survives, isolation | breaks, shared data plane is a trust problem | survives | vendor decides |
| 12 | Absurd: a "grid company" tenant becomes a cooperative of thousands of microgrids | new instance per co-op | schema breaks, tenant model wrong | bespoke | vendor schema |

Attractors: 2, 6, 10, 11 all break B's shared data plane and never A's. The coupling is operational data to the tenant boundary, not to the application. 5 and 8 break A's operations model. That cluster is the boundary: data plane per tenant, control and analytics shared.
Owner stressors, to confirm: a public utility commission mandates OT data be segregated from IT and never traverse the public internet; grid companies share interconnection and mutual-aid data, so one tenant's data is another tenant's input; a tenant's regulator requires on-premise data custody.

## Price
Anchor: assumed: a product team of 15–25 engineers, 5–15 existing grid-company customers, one cloud region today. The brief gives no team size, budget, or customer count; the assumption is listed under owner decisions.
| Option | Build | Run, and who pays | Undo | Keeps open |
|--------|-------|-------------------|------|------------|
| A | high: control plane, provisioning, update orchestration, config layer | N instances, ops carries it, cost scales with tenants | medium: re-do the data layer to centralize later | per-tenant residency, air-gap, per-tenant versioning |
| B | high: isolation, shared schema, migrate existing customers | one platform, ops carries it, sublinear cost | expensive: un-multi-tenanting is very hard | fast onboarding, low per-tenant cost; closes off air-gap and on-prem |
| C | low: config layer + deploy automation on current code | same as today, ops carries it | cheap | the tenancy decision itself |
| D | medium: integration + data-model mapping | vendor carries part, you carry integration | expensive: vendor lock | speed to market; closes off differentiation on the bought layer |

## Cross-examination
Elevator pass: stressor 10 (offline a week) is gold-plating unless a target customer is air-gapped — marked optional, not a driver. Stressor 5 matters only because the brief's own range reaches 1.9M customers, so it stays. Stressor 12 looks absurd but is the energy transition; it is the one that kills B's tenant schema, so it stays.
Residuality pass: B's "cheap to run" assumed every tenant accepts shared infrastructure; stressors 2 and 6 and the OT/IT owner-stressor make it the most expensive to change. A's "turn-key remote" was priced as free; stressor 8 makes N instances with no ops team a trap, so A is only viable with the control plane, not without it. C's "cheap" assumed current customers do not want the platform features; stressor 4 makes bespoke the most expensive path. Re-priced A as "high build, and the control plane is not optional."

## Decision
A. Per-tenant data plane with a shared control plane, config layer, and analytics tier.
We give up the sublinear run cost and instant onboarding of full multi-tenant SaaS to get per-tenant data residency, air-gap capability, and blast-radius isolation that the grid and OT domain appears to demand.
Also accepted: a control plane to build and operate, and per-tenant version drift to manage.

## Flips if
- No target customer actually requires data residency, on-premise, or air-gap — then B's economics win and the control plane is waste.
- Tenant count grows past what a small team can operate per-instance — then centralize the data plane.
- A large tenant demands the analytics engine run only on their data — then the shared analytics tier splits too.

## Owner decisions
- Do target grid companies require operational data to stay on-premise, in-jurisdiction, or air-gapped? This single answer decides A vs B.
- How many existing customers, and what is the team size? The prices above are unanchored without them.
- What does "turn-key deployment on remote sites" mean — customer-operated or vendor-operated?
- Is the analytics/optimization engine a build or a buy, and does it need per-tenant training data?
- Which of the three owner stressors hold, and which are missing?
