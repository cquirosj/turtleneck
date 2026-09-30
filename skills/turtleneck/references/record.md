# Decision record

One page. Every section present, even when the content is "none". A missing
section is a skipped rung.

## Template

```markdown
# <Decision, as a verb phrase>

Level: napkin | full | deep

## Two floors
Penthouse: <outcome, who pays now and ongoing, in one or two sentences>
Engine room: <what changes, what on-call sees, migration path, one to three sentences>
Missing: <what could not be stated and was asked instead, or "none">

## Options
A. <name>: <one line, how it differs in kind from the others>
B. <name>: ...
C. Defer: <what we would do instead and what ends the deferral>
D. Buy or reuse: <what exists, or why nothing fits>

## Stressors
| # | Stressor | A | B | C | D |
|---|----------|---|---|---|---|
| 1 | <stressor> | <breaks: x, y> | <survives> | ... | ... |
...
Attractors: <stressors that break the same components, and the coupling that reveals>
Owner stressors: <slot for stressors only the owner can add; state "empty" if empty>

## Price
| Option | Build | Run, and who pays | Undo | Keeps open |
|--------|-------|-------------------|------|------------|
| A | ... | ... | ... | ... |

## Cross-examination
Elevator pass: <what was cut as gold-plating and why>
Residuality pass: <which price was conditional on a known future, which stressor was politely omitted>

## Decision
<Option or "defer until <trigger>">
We give up <X> to get <Y>.
Also accepted: <second-order trade-off if any>

## Flips if
- <observable fact that would change the recommendation>
- ...

## Owner decisions
- <question that needs domain knowledge the record does not have>
- ...
```

At napkin level, ten lines and nothing else. No title, no level line, no
headings, no gate commentary:

```markdown
Options: A <one line>. B <one line>. C defer: <one line>. D buy/reuse: <one line>.
Pick: <option>.
We give up <X> to get <Y>.
Flips if: <one observable fact>.
You decide: <one question that needs domain knowledge>?
```

At deep level: add the incidence matrix per option and a contagion trace for
the top two stressors under Stressors.

## Worked example, full level

# Send order confirmations through a queue instead of a synchronous call

Level: full

## Two floors
Penthouse: checkout must not fail because the email provider is slow. Ops
pays for one more system to run. Product pays with confirmations that may
arrive minutes late.
Engine room: the checkout handler stops calling the email API inline and
publishes an event; a new consumer sends the email. On-call gains a queue
depth to watch and a dead-letter path to drain. Both paths exist during
migration.
Missing: how late is too late for a confirmation. Asked.

## Options
A. Queue and consumer: publish an event, separate process sends.
B. Inline with timeout and retry: keep the call, bound it, retry in
   background on failure.
C. Defer: keep inline, add a circuit breaker, revisit when provider
   incidents exceed one a month.
D. Reuse: the existing outbox table used for invoices, add a second message
   type.

## Stressors
| # | Stressor | A | B | C | D |
|---|----------|---|---|---|---|
| 1 | Email provider down 6h | survives, queue grows | checkout survives, retries pile up in-process | checkout survives, no emails | survives |
| 2 | Checkout volume 10x on launch | survives if consumer scales | thread pool starves | breaker trips constantly | survives, outbox poller is the limit |
| 3 | Legal: confirmation must be sent within 60s | breaks unless monitored | survives | survives | breaks, poller interval is 5 min |
| 4 | Provider changes API | consumer only | checkout code changes | checkout code changes | consumer only |
| 5 | Team halves | one more system, nobody owns it | nothing new | nothing new | already owned |
| 6 | Company acquired, must use acquirer's mail platform | consumer only | checkout code changes | checkout code changes | consumer only |
| 7 | Confirmations must be reversible by a human | needs audit store | needs audit store | needs audit store | outbox already is one |
| 8 | Absurd: system must run offline a week | queue fills, disk | fails | fails | outbox fills, disk |
| 9 | Absurd: confirmations become a paid feature | consumer decides | checkout decides | checkout decides | consumer decides |

Attractors: 4, 6, 9 all break checkout in B and C and never in A and D. The
coupling is checkout to the mail provider, not checkout to the email itself.
Owner stressors: empty.

## Price
| Option | Build | Run, and who pays | Undo | Keeps open |
|--------|-------|-------------------|------|------------|
| A | days | a broker, ops | medium, consumers exist | any number of consumers |
| B | hours | nothing new | cheap | nothing |
| C | hours | nothing new | cheap | the decision itself |
| D | a day | nothing new, outbox exists | cheap | a second consumer, slowly |

## Cross-examination
Elevator pass: stressor 8 survived by nobody who matters, cut from the
decision. Stressor 2 is real only if a launch is planned; asked. A broker
for one message type is an option premium with no named exercise.
Residuality pass: B's "cheap" assumed the provider stays the provider;
stressors 4 and 6 make it the most expensive to change. D's 5-minute poll
was priced as free and stressor 3 makes it a legal breach. Re-priced D as
"a day, plus tightening the poll".

## Decision
D. Reuse the outbox with a tighter poll interval.
We give up the sub-second delivery A would allow to get no new system and
the same operational model as invoices.
Also accepted: a second message type in a table designed for one.

## Flips if
- Confirmation latency limit turns out to be under the achievable poll
  interval.
- A third message type wants the outbox; at that point A's broker premium
  has a named exercise.
- A launch with 10x volume is scheduled.

## Owner decisions
- How late is too late for a confirmation? Legal or product.
- Is the outbox owned by the same team as checkout in a year?
- Which stressors from your market are missing from the table?
