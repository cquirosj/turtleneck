# Kata quality judge | model: claude-bridge/claude-opus-5-5

results: evals/results/20260930T124104Z-katas-skill.json

| case | lb | brief | opts | stress | coupl | price | flips | owner | facts | cliche | total/50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| kata-goinggoinggone | 4 | 4 | 4 | 4 | 3 | 2 | 3 | 4 | 4 | 4 | 36 |
| kata-sysopsquad | 4 | 4 | 4 | 3 | 4 | 2 | 3 | 4 | 4 | 5 | 37 |
| kata-makethegrade | 5 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 4 | 5 | 41 |
| kata-girdthegrid | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 4 | 4 | 4 | 38 |
| kata-amisick | 4 | 4 | 4 | 3 | 3 | 3 | 3 | 4 | 4 | 4 | 36 |
| kata-wheresfluffy | 3 | 3 | 4 | 2 | 3 | 3 | 4 | 4 | 4 | 4 | 34 |
| mean | 4.0 | 3.8 | 4.0 | 3.3 | 3.5 | 2.7 | 3.3 | 4.0 | 4.0 | 4.3 | 37.0 |

- kata-goinggoinggone: It names the room-to-online seam as 'the boundary that wants a deliberate design', then cuts stressor 10 in the elevator pass and accepts venue connectivity as a single point of failure. It never decides how room bids get into the authority log or how they are ordered against online bids, even though 'mixed live and online' is where the 'as if in the room' promise either holds or fails.
- kata-sysopsquad: Cross-examination keeps stressor 10 as the one that says the mobile client needs offline capture, then the decision drops it entirely. It also calls 10 absurd when the table marks 11 and 12 as absurd, and it recommends an 'append-only' ticket store without squaring that with tickets whose state changes.
- kata-makethegrade: The Decision contradicts itself: it applies D (buy) to the periphery for test delivery, then says 'we operate the periphery ourselves rather than buying it,' so a reader can't tell who owns delivery or what it costs.
- kata-girdthegrid: It raises the owner stressor that 'one tenant's data is another tenant's input' (interconnection and mutual aid), which directly undercuts a per-tenant data plane, then never tests the decision against it. It also never tests the choice against four nines.
- kata-amisick: Stressor 7 says B 'captures what was seen', which means copying patient history into a company-owned record, contradicting the decision's 'history stays read-through' and possibly overturning the lawyers' 'not a medical record' ruling, and neither conflict is noticed.
- kata-wheresfluffy: It says the whole record hinges on the unanswered franchise-vs-community question, then commits to B anyway, and it pushes the reward/escrow trust boundary (the domain's real money and fraud risk) into a separate record while filling the stressor table with generic tenancy scenarios.

Lowest mean criteria: price_realistic (2.7), stressors_specific (3.3), flips_observable (3.3)
