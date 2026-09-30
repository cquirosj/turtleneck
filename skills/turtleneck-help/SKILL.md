---
name: turtleneck-help
description: >
  Quick-reference card for turtleneck levels, skills, and commands. One-shot
  display, not a persistent mode. Trigger: /turtleneck-help, "turtleneck
  help", "what turtleneck commands", "how do I use turtleneck".
---

# Turtleneck Help

Display this card when invoked. One-shot. Do not change level or persist
anything.

## Levels

| Level | Use when |
|-------|----------|
| `napkin` | First cut, or cheap-ish to undo. Ten lines: options, pick, trade-off, one flip, one owner question. |
| `full` | The six rungs, 8 to 12 stressors, both cross-exam passes, one-page record. |
| `deep` | Expensive to undo, or a boundary several teams will live behind. Adds incidence matrix, attractors, contagion. |

No level named: the gate picks napkin for cheap-ish undos and first cuts,
full for expensive undos and multi-team boundaries, and says why. Deep is
always explicit. Switch: `/turtleneck napkin|full|deep`; an explicit level
wins. Off: "stop turtleneck".

## Skills

| Command | Does |
|---------|------|
| `/turtleneck [level]` | Run the protocol on the decision at hand. Output is a decision record. |
| `/turtleneck-review` | Gap list over an existing ADR, design doc, RFC, or PR description. Tags what was skipped. |
| `/turtleneck-stress` | Residuality pass alone: stressors, residues, attractors, boundary candidates. No recommendation. |
| `/turtleneck-help` | This card. |

## The six rungs

1. Ride the elevator: penthouse and engine room, both floors.
2. Open the solution space: three options that differ in kind, plus defer, plus buy.
3. Stress it: 8 to 12 stressors, two absurd, no probabilities.
4. Price the options: build, run and who pays, undo, keeps open.
5. Cross-examine: elevator pass, residuality pass.
6. Decide or defer: "we give up X to get Y", flip conditions, owner decisions.

## With ponytail

If the ponytail skill is installed: turtleneck decides where the boundary
goes, ponytail decides how little code goes inside it. Either way, local
code choices are outside turtleneck's gate.
