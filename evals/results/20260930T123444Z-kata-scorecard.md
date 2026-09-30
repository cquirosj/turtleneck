# Kata quality judge | model: claude-bridge/claude-sonnet-5

results: evals/results/20260930T122949Z-katas-skill.json

| case | lb | brief | opts | stress | coupl | price | flips | owner | facts | cliche | total/50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| kata-goinggoinggone | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 3 | 5 | 47 |
| kata-sysopsquad | 4 | 5 | 5 | 4 | 4 | 3 | 5 | 5 | 4 | 5 | 44 |
| kata-makethegrade | 5 | 5 | 5 | 4 | 5 | 4 | 5 | 5 | 3 | 5 | 46 |
| kata-girdthegrid | 5 | 4 | 4 | 4 | 5 | 3 | 4 | 5 | 3 | 5 | 42 |
| kata-amisick | 5 | 5 | 5 | 4 | 5 | 3 | 5 | 4 | 5 | 5 | 46 |
| kata-wheresfluffy | 5 | 5 | 5 | 4 | 5 | 4 | 5 | 5 | 4 | 5 | 47 |
| mean | 4.8 | 4.8 | 4.8 | 4.2 | 4.8 | 3.5 | 4.8 | 4.8 | 3.7 | 5.0 | 45.3 |

- kata-goinggoinggone: Slipping specific, brief-unstated numbers (GDPR 24h, 7-year regulatory retention) into the stressor table as if factual, without the hedge given to the explicitly labeled 'Absurd' rows.
- kata-sysopsquad: Flags 'Owner stressors: empty' as a gap in the retail/electronics-specific and regulatory pressures but never pushes to fill it with brief-grounded speculation, leaving the stressor set skewed toward generic infra failure modes.
- kata-makethegrade: Stress scenarios lean on invented specifics (9-month approval, one-hour enrollment spike, 40% budget cut) presented as table facts rather than explicitly marked assumptions until the Flips section.
- kata-girdthegrid: Treating the SCADA-runs-the-grid claim as an established fact to dismiss stressor 11, when the brief never confirms a separate SCADA system exists — the one place an assumption slipped past the 'asked, not invented' discipline the rest of the record holds to.
- kata-amisick: The price table's build/run estimates ('weeks', 'quarters') aren't anchored to any team size or budget from the brief, so 'plausible for the stated team and scale' is asserted rather than shown.
- kata-wheresfluffy: Leaves the owner-stressor row empty and calls it a gap rather than doing the work to fill even one plausible owner-only stressor (e.g. a pet-store partner's contractual data demands), which is the exact kind of stressor this record says the model can't originate.

Lowest mean criteria: price_realistic (3.5), no_invented_facts (3.7), stressors_specific (4.2)
