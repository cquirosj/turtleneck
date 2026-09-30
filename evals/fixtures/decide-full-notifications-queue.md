# Send order confirmations through a queue instead of a synchronous call

Level: full

## Two floors
Penthouse: checkout must not fail because the email provider is slow. Ops pays for one more system to run; product pays with confirmations that may arrive minutes late.
Engine room: the checkout handler stops calling the email API inline and publishes an event; a consumer sends the email. On-call gains a queue depth to watch and a dead-letter path to drain.
Missing: how late is too late for a confirmation. Asked.

## Options
A. Queue and consumer: publish an event, a separate process sends.
B. Inline with timeout and retry: keep the call, bound it, retry in the background.
C. Defer: keep inline, add a circuit breaker, revisit when provider incidents exceed one a month.
D. Buy or reuse: the existing outbox table used for invoices, with a second message type.

## Stressors
| # | Stressor | A | B | C | D |
|---|----------|---|---|---|---|
| 1 | Email provider down 6h | survives, queue grows | checkout survives, retries pile up | checkout survives, no emails | survives |
| 2 | Checkout volume 10x on launch | survives if the consumer scales | thread pool starves | breaker trips constantly | survives, poller is the limit |
| 3 | Legal: confirmation required within 60s | breaks unless monitored | survives | survives | breaks, poller interval is 5 min |
| 4 | Provider changes API | consumer only | checkout code changes | checkout code changes | consumer only |
| 5 | Team halves | one more system, nobody owns it | nothing new | nothing new | already owned |
| 6 | Company acquired, must use acquirer mail platform | consumer only | checkout code changes | checkout code changes | consumer only |
| 7 | Confirmations must be reversible by a human | needs audit store | needs audit store | needs audit store | outbox already is one |
| 8 | Absurd: system must run offline for a week | queue fills, disk | fails | fails | outbox fills, disk |
| 9 | Absurd: confirmations become a paid feature | consumer decides | checkout decides | checkout decides | consumer decides |

Attractors: 4, 6, 9 break checkout in B and C and never in A and D. The coupling is checkout to the mail provider, not checkout to the email itself.
Owner stressors: empty.

## Price
| Option | Build | Run, and who pays | Undo | Keeps open |
|--------|-------|-------------------|------|------------|
| A | days | a broker, ops | medium, consumers exist | any number of consumers |
| B | hours | nothing new | cheap | nothing |
| C | hours | nothing new | cheap | the decision itself |
| D | a day | nothing new, outbox exists | cheap | a second consumer, slowly |

## Cross-examination
Elevator pass: stressor 8 survived by nobody who matters, cut from the decision. A broker for one message type is an option premium with no named exercise.
Residuality pass: B's cheap assumed the provider stays the provider; stressors 4 and 6 make it the most expensive to change. D's five-minute poll was priced as free and stressor 3 makes it a legal breach. Re-priced D as a day plus tightening the poll.

## Decision
D. Reuse the outbox with a tighter poll interval.
We give up the sub-second delivery A would allow to get no new system and the same operational model as invoices.
Also accepted: a second message type in a table designed for one.

## Flips if
- The confirmation latency limit turns out to be under the achievable poll interval.
- A third message type wants the outbox; A's broker premium then has a named exercise.
- A launch with 10x volume is scheduled.

## Owner decisions
- How late is too late for a confirmation? Legal or product.
- Is the outbox owned by the same team as checkout in a year?
- Which stressors from your market are missing from the table?
