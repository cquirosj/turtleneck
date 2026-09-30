§Decision: justified-after: Kafka chosen and the alternatives section lists RabbitMQ and HTTP with no stressor or price against either. Give both the same stressor table, or admit options considered: one.
§Trade-offs: cliché: scalability high, maintainability medium, performance high, reliability medium given as ratings. Which stressor? "Volume 10x" and "the team halves" would give that table different answers.
§Context: unstressed: no stressors named anywhere, only -ilities. Add "the provider changes its API" and "the platform team halves" and see what breaks.
§Consequences: unpriced: the platform team is named as the operator but no build, run, or undo cost appears. Add the price columns.
§Alternatives considered: unexplored: RabbitMQ is listed as rejected with no reason that survives a stressor. Stress it against the same table.
§Consequences: no-flip: nothing here would reverse the decision. "If a second service does not consume order events within two quarters, collapse back to the database."
§Rationale: unowned: the record asserts that streaming at this scale needs this platform, with no source in the doc. Turn it into the owner question for the platform team.
7 gaps. description
