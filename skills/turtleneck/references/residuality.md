# The residuality lens

Drawn from Barry O'Reilly's Residuality Theory: Residues: Time, Change, and
Uncertainty in Software Architecture, and The Architect's Paradox. Barry
O'Reilly of Black Tulip Technology, not the author of Unlearn. This file
holds the working procedure, not the theory. Read the books.

## Why random stress

The business environment is not a stable system with knowable
probabilities. The future that arrives is one draw from a space you cannot
enumerate, and you do not get to average over the draws you did not get.
Risk lists fail here because they ask "how likely" and then optimize for the
likely, which is exactly the part of the space that would have been fine
anyway.

Residuality does something different. Take the first design that falls out
of the requirements, the naive architecture. Hit it with many stressors,
chosen without regard to likelihood, including ones that seem absurd. For
each, look at what is left and what you would have to change. Collect the
changes. The component decomposition that emerges from surviving many
unrelated stressors is more likely to survive the stressor nobody listed
than the one derived from requirements alone.

An LLM generating stressors is generating from patterns of past stressors.
That covers the generic space well and the owner's specific market badly.
Always leave a labeled slot for stressors only the owner can add, and treat
their absence as a gap in the analysis, not as completeness.

## Vocabulary

- **Naive architecture**: the first design, derived from requirements
  before any stress. Rung 2 options are naive architectures.
- **Stressor**: anything in the environment that could change or break the
  system. Not a risk. No probability attached. Every stressor is treated as
  if it will happen.
- **Residue**: what remains of the system after a stressor hits. The
  components that survive, the ones that break, and the adjusted structure
  you would build to survive it.
- **Attractor**: a state the business and system fall into under stress.
  Several stressors often lead to the same residue. Those stressors cluster,
  and the cluster tells you where the structure is fragile.
- **Hyperliminal coupling**: coupling between components that is not visible
  in the code, because it runs through the business environment. Two
  components with no dependency on each other both break when a key
  customer leaves. That is coupling. The code will never show it.
- **Incidence matrix**: stressors as rows, components as columns, a mark
  where the stressor impacts the component. Columns that co-vary point at
  hidden coupling. Rows that hit everything point at a missing boundary.
- **Contagion**: how a failure spreads from the component a stressor hits
  to the components coupled to it, visibly or hyperliminally.
- **Criticality**: the region between rigid and chaotic. Enough coupling to
  function, few enough couplings that a stressor does not cascade
  everywhere. Architecture aims for this region, not for minimal coupling.

## Stressor generation

Aim for 8 to 12 at full, 20 or more at deep. Spread across categories.
Include at least two from the last category no matter what.

Market and customers:

- The largest customer leaves. The largest customer triples volume.
- A competitor offers this for free. Pricing moves from per-seat to
  per-transaction.
- The product goes from one region to five with different data residency
  rules.

Regulation and legal:

- Data must be deletable on request within 24 hours.
- An audit requires proof of every state change for seven years.
- A dependency changes its license.

Organization:

- The team halves. The team triples and splits.
- The company is acquired and must integrate with the acquirer's identity,
  billing, and reporting.
- The product is sold off and must run standalone.
- The person who understands this component leaves.

Technology:

- The primary dependency is abandoned. A cloud region goes down for a day.
- Latency to the database doubles. The schema needs a breaking change.
- A downstream consumer starts sending 100x the events.

Absurd:

- The system must run offline for a week.
- Every write must be reversible by a human.
- The business decides to sell this component as a product to competitors.
- The primary data type changes meaning: an "order" becomes a subscription.

Absurd stressors exist because the polite ones only find the couplings you
already suspected.

## Procedure

1. Take each option from rung 2 as a naive architecture.
2. Generate the stressor list once. Use the same list against every option
   so the residues are comparable.
3. For each stressor and each option, write the residue in one line: what
   breaks, what survives, what you would change.
4. Collect the changes per option. Changes that recur across many stressors
   are not optional; they are the structure the environment demands.
5. At deep level, draw the incidence matrix per option. Look for:
   - columns that co-vary: two components that always break together want
     to be one component, or want a deliberate boundary between them and
     everything else
   - rows that hit every column: a stressor no boundary contains, which
     means a boundary is missing
   - columns that nothing hits: a component the environment does not care
     about, and a candidate for buying instead of building
6. Trace contagion for the top two stressors: which failure crosses the
   proposed boundary and which stays behind it. A boundary that contagion
   crosses freely is a line on a diagram, not a boundary.
7. Adjust the option and rerun with a few new random stressors. Stop when
   new stressors stop producing new changes. That is the residual
   architecture.

## Residuality pass, rung 5 checklist

Run this over your own pricing from rung 4:

1. Which cost estimate assumes the environment stays as it is today? Mark it
   as conditional on that.
2. Which option looked cheap because the stressor list was polite? Add the
   stressor that would make it expensive and re-price.
3. What happened to the absurd stressors? If they were dropped for being
   unlikely, that is risk thinking, not residuality. Put at least one back.
4. Is the recommended boundary derived from the residues, or from the org
   chart or the requirements document? Both can be right, but say which.
5. Where is the labeled slot for stressors only the owner can add? Is it
   empty, and did the record say so?

## What this is not

- Not risk management. No likelihood, no impact score, no heat map.
- Not chaos engineering. This is done on paper before anything is built.
  Chaos engineering later confirms or refutes it.
- Not a checklist of -ilities. Scalability, availability, and
  maintainability are summaries of residues, not stressors. Name the
  stressor, and the -ility follows or does not.
- Not a proof. A design that survived thirty stressors is more likely to
  survive the thirty-first. It is not guaranteed to. Say so in the record.
