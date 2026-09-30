# Split the order service out of the monolith

Level: full

## Two floors
Penthouse: the order team ships independently and a bad order deploy stops taking down the storefront. The company pays for one more deployable and a wider on-call rotation.
Engine room: order tables and the order HTTP API move to a new service; checkout calls it over the network. On-call sees a new service page and a network hop in the checkout path.
Missing: none.

## Options
A. Extract now: a separate order service with its own database.
B. Module boundary: keep one deployable, publish events at the seam.
C. Defer: keep the monolith, revisit when the order team doubles.
D. Buy or reuse: adopt a vendor order-management product and retire the in-house module.

## Trade-offs
| Dimension | Rating |
|-----------|--------|
| Scalability | High |
| Maintainability | Medium |
| Performance | High |
| Reliability | Medium |

## Stressors
| # | Stressor | A | B | C | D |
|---|----------|---|---|---|---|
| 1 | Order volume 10x | survives | survives | breaks | survives |
| 2 | Shared database schema change | breaks | survives | survives | survives |
| 3 | Team halves | breaks, nobody owns the new service | survives | survives | breaks |
| 4 | Company acquired | breaks | survives | survives | breaks |
| 5 | Absurd: system must run offline for a week | fails | fails | fails | fails |

Attractors: 2 and 4 break A together; the coupling is the shared order tables.
Owner stressors: empty.

## Price
| Option | Build | Run, and who pays | Undo | Keeps open |
|--------|-------|-------------------|------|------------|
| A | months | a service, ops | expensive | independent deploys |
| B | weeks | nothing new | cheap | the split |
| C | nothing | nothing new | cheap | the decision |
| D | a licence | a vendor, finance | expensive | nothing |

## Cross-examination
Elevator pass: stressor 5 cut, nobody upstairs cares about a week offline.
Residuality pass: A's price assumed the order team keeps growing.

## Decision
A. Extract the order service now so the team can ship on its own cadence without waiting for the monolith release train.

## Flips if
- The order team stops growing.
- Checkout latency becomes the top incident source.

## Owner decisions
- Does the order team own the new service in a year?
