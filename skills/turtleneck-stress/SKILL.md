---
name: turtleneck-stress
description: >
  Run the residuality pass alone against an existing design: generate random
  business and technical stressors including absurd ones, record what breaks
  and survives per component, find the stressors that break the same
  components, and propose where a boundary wants to be. For designs that
  already exist and need stress, not a fresh decision. Use when the user
  says "stress this design", "what breaks", "find the hidden coupling",
  "residuality", "what happens when", or invokes /turtleneck-stress.
argument-hint: "[full|deep]"
---

# Turtleneck stress

Rung 3 of the protocol, on its own, against a design that already exists.
Input is a description, a diagram, a repo layout, or a doc. Read it fully.
List the components you see before generating anything.

Procedure and vocabulary in
[references/residuality.md](../turtleneck/references/residuality.md).

## Steps

1. List components as the design names them. Do not rename or regroup yet.
2. Generate stressors: 8 to 12 at full, 20 or more at deep. Spread across
   market, regulation, organization, technology. At least two absurd. No
   probabilities.
3. Per stressor, one line: what breaks, what survives, what you would change.
4. Find attractors: stressors that break the same components. Name the
   coupling each attractor reveals, and say whether it is visible in the
   code or runs through the business environment.
5. At deep: incidence matrix, then contagion trace for the top two stressors
   across the proposed or existing boundaries.
6. Propose boundary changes derived from the residues only. Mark each as
   "from residues" and note if the existing boundary came from the org
   chart instead.
7. Leave a labeled slot: stressors only the owner can add. State that it is
   empty.

## Output

```
Components: <list as named>

| # | Stressor | Breaks | Survives | Change |
|---|----------|--------|----------|--------|
...

Attractors:
- <stressors n, m, k> → <components> : <coupling, visible or hyperliminal>

Boundary candidates (from residues):
- <where, why, what contagion it would stop>

Owner stressors: empty. Add the ones from your market before trusting this.
```

No recommendation. This skill stresses; `/turtleneck` decides.

## Boundaries

Do not soften stressors because they seem unlikely. Do not drop the absurd
ones. Do not propose technology. If the input has no components you can
name, ask for the design rather than inventing one.
