# Kata quality judge | model: claude-bridge/claude-sonnet-5

results: evals/results/20260930T124104Z-katas-skill.json

| case | lb | brief | opts | stress | coupl | price | flips | owner | facts | cliche | total/50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| kata-goinggoinggone | 4 | 5 | 5 | 5 | 4 | 4 | 5 | 5 | 4 | 5 | 46 |
| kata-sysopsquad | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 5 | 4 | 5 | 46 |
| kata-makethegrade | 5 | 4 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 48 |
| kata-girdthegrid | 5 | 5 | 5 | 5 | 5 | 4 | 4 | 5 | 4 | 5 | 47 |
| kata-amisick | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 5 | 5 | 5 | 47 |
| kata-wheresfluffy | 5 | 5 | 5 | 4 | 5 | 3 | 5 | 5 | 5 | 5 | 47 |
| mean | 4.8 | 4.8 | 5.0 | 4.5 | 4.8 | 3.8 | 4.5 | 5.0 | 4.5 | 5.0 | 46.8 |

- kata-goinggoinggone: Stating in the Decision that the design gives up 'sub-50ms global latency' invents a specific performance figure the brief never mentioned and doesn't flag as an assumption, unlike the disciplined labeling used elsewhere for team size and concurrency.
- kata-sysopsquad: The 7-year regulatory audit stressor is introduced without any signal in the brief that regulation applies here, and while it's correctly demoted to 'a question, not a design driver,' it still occupies a stressor slot that a more domain-grounded pressure (e.g. franchise SLAs) could have filled more usefully.
- kata-makethegrade: The brief's explicit reporting-by-school/teacher/student requirement is acknowledged once in the engine room and then dropped — no stressor or price line tests whether the chosen boundary actually supports that reporting granularity.
- kata-girdthegrid: Four-nines reliability is an explicit brief requirement with direct tenancy implications (blast radius, per-instance vs shared failure domains) yet it's never analyzed or priced -- it rides along inside 'blast radius' stressors instead of being treated as its own driver.
- kata-amisick: Price section stays qualitative ('weeks', 'moderate') and 'who pays' is always just 'ops', so the prices read as plausible-sounding rather than actually priced against the 10-15 engineer anchor it names.
- kata-wheresfluffy: The price table stays purely qualitative (low/medium/high) built on an invented 3-5 engineer team-size anchor the brief never supplies, leaving the actual cost comparison unfalsifiable.

Lowest mean criteria: price_realistic (3.8), stressors_specific (4.5), flips_observable (4.5)
