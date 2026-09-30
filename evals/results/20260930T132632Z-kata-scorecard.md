# Kata quality judge | model: claude-bridge/claude-opus-5-5

results: evals/results/20260930T131809Z-katas-skill.json

| case | lb | brief | opts | stress | coupl | price | flips | owner | facts | cliche | total/50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| kata-goinggoinggone | 5 | 4 | 4 | 4 | 3 | 3 | 4 | 4 | 4 | 4 | 39 |
| kata-sysopsquad | 3 | 3 | 3 | 3 | 2 | 3 | 4 | 3 | 4 | 3 | 31 |
| kata-makethegrade | 4 | 4 | 4 | 4 | 4 | 2 | 4 | 4 | 3 | 4 | 37 |
| kata-girdthegrid | 4 | 3 | 4 | 4 | 3 | 3 | 3 | 4 | 4 | 3 | 35 |
| kata-amisick | 3 | 3 | 3 | 3 | 4 | 2 | 3 | 4 | 4 | 3 | 32 |
| kata-wheresfluffy | 4 | 4 | 4 | 3 | 4 | 3 | 3 | 4 | 3 | 4 | 36 |
| mean | 3.8 | 3.5 | 3.7 | 3.5 | 3.3 | 2.7 | 3.5 | 3.8 | 3.7 | 3.5 | 35.0 |

- kata-goinggoinggone: It chooses A even though its own stressors 6 and 8 break A hard. The 'adapter contract' hybrid never says who holds authority when the room is cut off from the ledger, which is exactly the 'room says sold, screen says otherwise' failure the record itself called on-call's nightmare.
- kata-sysopsquad: It extracts routing as its own event-driven service while consultant skill, location and availability data stay in the shared monolith datastore, then claims routing is contained under region outage and overload. A service split alone gives neither: a region outage takes both down unless there are multiple regions, and routing still depends on the monolith's data.
- kata-makethegrade: It prices B as cheaper to run than A while ignoring the cost of durable local capture infrastructure at every center, and it props up that ranking by claiming A 'breaks' at a 40,000-student peak.
- kata-girdthegrid: It admits the first owner question could reshape everything, yet still commits to the default hybrid answer and calls it 'not a guess, a residue'. It also never checks C against the brief's own requirements: near-real-time dashboards across edge sites, mobile administration, and where penetration-attempt reporting lives when the edge is offline.
- kata-amisick: It buries the real load-bearing decision (conversation-data ownership, and buying CCaaS vs building chat) in the attractors section and makes monolith vs microservices the headline, priced only in low/medium/high against an assumed team size.
- kata-wheresfluffy: Picking C quietly drops an explicit brief requirement ('rewards brokered/managed by the service') and oversells it as 'zero regulatory exposure'. It also never makes the adjudication capability it derived into a v1 boundary with an owner; it only keeps a data model.

Lowest mean criteria: price_realistic (2.7), coupling_found (3.3), uses_brief (3.5)
