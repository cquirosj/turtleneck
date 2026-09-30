# Kata quality judge | model: claude-bridge/claude-sonnet-5

results: evals/results/20260930T123655Z-katas-skill.json

| case | lb | brief | opts | stress | coupl | price | flips | owner | facts | cliche | total/50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| kata-goinggoinggone | 5 | 5 | 5 | 4 | 5 | 4 | 3 | 5 | 4 | 5 | 45 |
| kata-sysopsquad | 5 | 5 | 5 | 4 | 5 | 4 | 5 | 5 | 4 | 5 | 47 |
| kata-makethegrade | 5 | 5 | 5 | 4 | 5 | 4 | 5 | 5 | 4 | 5 | 47 |
| kata-girdthegrid | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 5 | 5 | 5 | 47 |
| kata-amisick | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 5 | 3 | 5 | 45 |
| kata-wheresfluffy | 5 | 4 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 48 |
| mean | 5.0 | 4.8 | 5.0 | 4.2 | 5.0 | 4.0 | 4.3 | 5.0 | 4.2 | 5.0 | 46.5 |

- kata-goinggoinggone: The price table gives every option 'unanchored team, weeks-to-months' — honest about missing inputs, but it flattens the comparison the price section is supposed to sharpen.
- kata-sysopsquad: Flipping to B on 'team under ~5' invents a precise headcount threshold in the same document that elsewhere admits team size is unanchored.
- kata-makethegrade: Asserting a specific '7 years' grade-audit retention period and an IEP/504 label as stressor facts when neither figure appears in the brief and both should have been flagged as unconfirmed assumptions like the rest of the owner stressors.
- kata-girdthegrid: Price table stays fully unanchored across all five options with no attempt at even a rough band tied to a stated team-size assumption, so the pricing argument leans on category labels (high/medium/low) rather than anything a client could sanity-check.
- kata-amisick: Asserting 'HIPAA-eligible' as a vendor property in option B when the brief specifies no jurisdiction and nurses are worldwide — an invented regulatory anchor the brief doesn't support.
- kata-wheresfluffy: The price table never anchors to the brief's own scale numbers (dozens of owners, hundreds of spotters, per-city rollout) even roughly — it stays at 'expensive/medium/cheap' throughout, so build/run/undo costs are asserted rather than derived.

Lowest mean criteria: price_realistic (4.0), stressors_specific (4.2), no_invented_facts (4.2)
