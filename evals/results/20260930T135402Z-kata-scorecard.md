# Kata quality judge | model: claude-bridge/claude-opus-5-5

results: evals/results/20260930T135156Z-katas-skill.json

| case | lb | brief | opts | stress | coupl | price | flips | owner | facts | cliche | total/50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| kata-goinggoinggone | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | 39 |
| kata-sysopsquad | 4 | 3 | 4 | 3 | 2 | 2 | 3 | 4 | 4 | 4 | 33 |
| kata-makethegrade | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 4 | 5 | 40 |
| kata-girdthegrid | 4 | 4 | 3 | 3 | 4 | 2 | 4 | 4 | 4 | 4 | 36 |
| kata-amisick | 4 | 4 | 4 | 3 | 4 | 3 | 3 | 4 | 3 | 4 | 36 |
| kata-wheresfluffy | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 3 | 4 | 38 |
| mean | 4.0 | 3.8 | 3.8 | 3.5 | 3.7 | 2.7 | 3.7 | 4.0 | 3.7 | 4.2 | 37.0 |

- kata-goinggoinggone: It makes the auctioneer's console the single writer of record and answers stressor 2 with 'local-first'. It never faces the contradiction: when the room loses connectivity, a local-first console can't take proposals from thousands of online bidders, so the online auction freezes or the order forks. That is exactly the dispute scenario the decision exists to prevent.
- kata-sysopsquad: It sets up B as a single runtime that cannot degrade, uses that to justify the obvious intake/routing split, and leaves the more revealing coupling unexplored: consultant availability depends on mobile connectivity (stressor 2).
- kata-makethegrade: The buy option's column is almost all 'assumed' and never gets a residuality pass. So the buy option is barely tested, and the decision limits it to the delivery/grading tier without evidence. Meanwhile stressor 7 (a budget cut breaks B) goes unanswered in the decision beyond staging.
- kata-girdthegrid: The price table gives build costs only as 'months / many months / many months+' on an assumed team size, so the trade-off the decision depends on (C's two-plane cost against B's cost) is never actually priced.
- kata-amisick: It patches option A with an append-only log and snapshots of the history the nurse saw, which makes A a partial clinical record holder, but never re-runs the table. Stressor 8 ('we store little'), stressor 10, the cheap undo and 'we own nothing clinical' are all no longer true for the chosen design.
- kata-wheresfluffy: The chosen option, A plus bought escrow plus deferred social, is never run back through the stressors. The attractor conclusions also rest on C and D 'surviving' by removing required features (rewards) or by leaning on a parent platform the brief never confirms exists.

Lowest mean criteria: price_realistic (2.7), stressors_specific (3.5), coupling_found (3.7)
