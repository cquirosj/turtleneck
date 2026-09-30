# Kata quality judge | model: claude-bridge/claude-opus-5-5

results: evals/results/20260930T131057Z-katas-skill.json

| case | lb | brief | opts | stress | coupl | price | flips | owner | facts | cliche | total/50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| kata-goinggoinggone | 5 | 5 | 5 | 5 | 5 | 4 | 4 | 5 | 4 | 4 | 46 |
| kata-sysopsquad | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | 39 |
| kata-makethegrade | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 5 | 4 | 5 | 46 |
| kata-girdthegrid | 5 | 4 | 5 | 4 | 5 | 4 | 4 | 5 | 4 | 4 | 44 |
| kata-amisick | 5 | 4 | 5 | 4 | 5 | 3 | 4 | 5 | 4 | 4 | 43 |
| kata-wheresfluffy | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 44 |
| mean | 4.8 | 4.5 | 4.8 | 4.2 | 4.8 | 3.7 | 4.0 | 4.7 | 4.0 | 4.2 | 43.7 |

- kata-goinggoinggone: Stressor 7 (floor versus online tie, loser sues) breaks the chosen option. That is the most lawsuit-prone point for a company that just settled a fraud suit. The record accepts it as a 'recorded human ruling' and never tests whether that ruling holds up in the court scenario from stressor 4. Meanwhile the D column leans on 'assumed' and 'vendor's rules', so buying is rejected on one contract assumption.
- kata-sysopsquad: It pushes mobile offline capability to 'its own record' even though 'consultants should only need a mobile device' is an explicit requirement and stressor 7 breaks every option the same way, so the choice most likely to cost field-visit revenue is left undecided.
- kata-makethegrade: It recommends B outright even though its own residuality pass says B is just A with extra moving parts if the agencies reject the ledger-only boundary; agency acceptance should have been a precondition gate, for example through the D pilot, rather than a flip condition discovered afterward.
- kata-girdthegrid: It chooses C even though its own table says C breaks when the team halves, and edge-first starts out as B, which the table says breaks on the 72h CVE and 10x volume stressors. It accepts all of this with only a vague team-size flip instead of a mitigation.
- kata-amisick: B was 'refined' so that conversation text sits inside the boundary, which puts most of the product inside it, but it was never re-priced. The 'few weeks against A' trade-off and the cost of routing content-based prioritization through the boundary are still stated as if the original, narrower B applied.
- kata-wheresfluffy: It picks B while admitting B breaks under stressor 2 (the owner never confirms and the finder goes unpaid). It offers reputation as the only remedy, prices B at an optimistic 'about a week', and the flip toward D has no threshold, so no one can tell when B has failed.

Lowest mean criteria: price_realistic (3.7), flips_observable (4.0), no_invented_facts (4.0)
