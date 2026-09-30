# Banned moves

The moves a model makes when it is pattern-matching instead of deciding.
Each with the move that replaces it. Used for self-check at rung 5 and by
`/turtleneck-review`, which tags them `cliché:`.

| Banned move | Why it is empty | Better move |
|-------------|-----------------|-------------|
| "It depends." | True of everything, decides nothing. | "It depends on X. If X, then A. If not X, then B. Here is how to find out X." |
| Trade-off table with scalability, maintainability, performance rated high/medium/low. | The ratings are opinions with no stressor behind them. Two readers fill in different numbers. | A stressor table. "Under 10x volume, A survives, B starves the thread pool." |
| Recommending a pattern by name: CQRS, event sourcing, saga, hexagonal. | A pattern is an answer. Without the stressor it answers, it is a vocabulary word. | "Stressor 3 requires replaying state; event sourcing answers that at the price of a projection layer." |
| "Best practice", "industry standard", "clean", "idiomatic" as rationale. | Appeals to an authority that is not in the room. | The stressor or organizational force that the practice answers here. |
| New technology as the fix. | New tech punishes the habit that made the old one painful. | Name the habit. Check the new tech does not let it continue. |
| A known pattern under a new name. | Reinvention hides the existing literature and its known failure modes. | Name the original. State what is different. If nothing is, drop the new name. |
| Three options listed, one explored. | Justification after the fact wearing an options section. | Attack the favorite hardest. Each option gets the same stressor list and the same price columns. |
| "Microservices vs monolith." | A false binary that skips the actual question: where are the boundaries and who owns them. | Options that differ in boundary placement and ownership, deployed however. |
| "Future-proof", "scalable", "flexible" as goals. | Unfalsifiable. No stressor could refute them. | The specific future, the specific load, the specific change. |
| Resilience against every stressor. | Every survived stressor was bought. Nobody stated the price. | Per stressor: does the penthouse care, and what does surviving it cost. |
| "We'll make it configurable." | Decision avoidance sold as flexibility. | Decide. Or name the scenario where the setting is flipped and who flips it. |
| Quoting named architects, real or invented. | Borrowed authority. Often misquoted. Always unfalsifiable. | Make the argument. If it is good, it does not need a name on it. |
| A decision record with no losers. | A description of what was built, not a decision. | Every option that lost, and the stressor or price that killed it. |
| Filling in domain knowledge that was not given. | The most dangerous output: plausible design in a domain nobody in the room understands. | An owner decision. "This needs X. I do not have X. Who does?" |
| "Consider" and "you may want to" as the recommendation. | Hedging that hands the decision back without the analysis that would make it decidable. | Recommend. State the trade-off. State what flips it. |
