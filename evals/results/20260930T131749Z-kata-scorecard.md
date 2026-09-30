# Kata quality judge | model: claude-bridge/claude-sonnet-5

results: evals/results/20260930T131057Z-katas-skill.json

| case | lb | brief | opts | stress | coupl | price | flips | owner | facts | cliche | total/50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| kata-goinggoinggone | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 50 |
| kata-sysopsquad | 4 | 4 | 5 | 4 | 5 | 3 | 4 | 5 | 4 | 4 | 42 |
| kata-makethegrade | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 49 |
| kata-girdthegrid | 5 | 5 | 5 | 4 | 5 | 4 | 5 | 5 | 4 | 5 | 47 |
| kata-amisick | 4 | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 48 |
| kata-wheresfluffy | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 49 |
| mean | 4.7 | 4.8 | 5.0 | 4.7 | 5.0 | 4.0 | 4.8 | 5.0 | 4.7 | 4.8 | 47.5 |

- kata-goinggoinggone: Option D is stress-tested more shallowly than A - several of its cells resolve to 'vendor's rules' or 'assumed: survives' without pushing on what that assumption costs, so the comparison ends up structurally favoring A by giving it the only rigorous treatment.
- kata-sysopsquad: The price table stays entirely qualitative ('fewest months', 'the most') despite pinning a concrete team size, so the build/run/undo comparison can't actually be checked for plausibility.
- kata-makethegrade: The price table stays entirely relative (1x, 1.3x baselines) with no absolute dollar or team-month anchor, so the claimed cost differences between B and the alternatives can't actually be checked against the stated 6–8 person team.
- kata-girdthegrid: Declaring historian/identity/SIEM as bought 'in every option' without marking it assumed, when nothing in the brief establishes that these will be third-party rather than built, given the company's stated ambition to own more of the stack as a platform reseller.
- kata-amisick: Option E (buy/reuse) leans on an unverified assumption ('the company's own niche-product chassis... assumed: one exists') and is never pressure-tested as hard as B, making the buy option feel like a formality rather than a real contender.
- kata-wheresfluffy: Dismissing stressor 4 (cross-border second city) by leaning on the brief's word choice ('cities, not countries') is a technicality that lets a real regulatory/currency risk off the hook too easily, and it undercuts the otherwise careful separation of assumption from fact.

Lowest mean criteria: price_realistic (4.0), load_bearing (4.7), stressors_specific (4.7)
