---
name: turtleneck-review
description: >
  Review an architecture decision record, design doc, RFC, or PR description
  for skipped trade-off work. Finds what is missing: options never explored,
  costs never priced, stressors never named, decisions justified after the
  fact, domain knowledge invented instead of asked for. One line per gap:
  location, tag, what is missing, what would fill it. Use when the user says
  "review this ADR", "review this design", "what is missing from this
  decision", "poke holes in this", or invokes /turtleneck-review. Does not
  review correctness, style, or code; only decision quality.
---

# Turtleneck review

Read the whole document first. Then emit a gap list. Nothing else.

## Format

`§<section or heading>: <tag> <what is missing>. <what would fill it>.`

Use `L<line>` when the input has line numbers, `§<heading>` otherwise.

Tags:

- `one-floor:` only penthouse or only engine room stated. Name the missing floor's first question.
- `unexplored:` an option listed but never stressed or priced, or only one option present. Name the option that deserved the same treatment.
- `unpriced:` an option with no build, run, or undo cost, or no owner of the ongoing cost. Name the column.
- `unstressed:` no stressors, or only polite ones, or -ilities in place of stressors. Name two stressors that would change the picture.
- `justified-after:` a decision followed by reasons, with no alternative that was seriously in the running. Name the alternative.
- `no-flip:` no observable condition that would reverse the decision. Propose one.
- `unowned:` domain knowledge asserted that the document could not know. Turn it into the owner question it should have been.
- `invented:` a real or plausible quote, statistic, or reference used as authority. Replace with the argument or drop it.
- `cliché:` a banned move from [references/cliches.md](../turtleneck/references/cliches.md). Name the better move.
- `reinvented:` a known pattern under a new name. Name the original.

## Examples

❌ "The document could benefit from a more thorough exploration of
alternatives and a clearer articulation of the trade-offs involved."

✅ `§Decision: justified-after: Kafka chosen, alternatives section lists "considered RabbitMQ" with no stressor or price. Same stressor table for both, or admit options considered: one.`

✅ `§Context: one-floor: engine room only. Who pays for the broker in year two, and what does the business lose if we defer a year?`

✅ `§Trade-offs: cliché: scalability high, maintainability medium. Which stressor? "Volume 10x" and "team halves" would give the same table different answers.`

✅ `§Consequences: no-flip: nothing here would reverse the decision. "If a second consumer does not appear within two quarters, collapse back to the outbox."`

✅ `§Rationale: unowned: "regulators require 7-year retention" asserted, no source in the doc. Owner question for legal.`

✅ `L42: invented: quote attributed to a named architect. Drop it, the argument stands or falls without the name.`

## Scoring

End with one line: `<n> gaps. <verdict>`, where verdict is one of
`decision`, `description`, or `deck`. A decision has losers and a price. A
description has neither. A deck has slides.

## Boundaries

Only decision quality. Not correctness, not code, not prose style, not
formatting. If the document is a code change with no design content, say
"no architecture decision in scope" and stop. Do not rewrite the document.
The author decides what to fill in.
