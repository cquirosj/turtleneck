# Turtleneck evals

Measures whether a model with the turtleneck skill in its system prompt follows the protocol,
against the same model without it.

## Run

    python3 -m unittest discover -s evals -p "test_*.py"
    python3 evals/run.py --arm skill --dry-run
    python3 evals/run.py --arm skill --only gate-loop-vs-linq
    python3 evals/run.py --arm both --concurrency 4 --judge

Flags: `--arm skill|baseline|both` (required), `--model NAME`, `--only CASE_ID`, `--concurrency N`
(default 2), `--judge`, `--dry-run`. Ollama at http://localhost:11434, 300s timeout, temperature 0.
On a transport error or HTTP 5xx, a call waits 5s and retries once; the entry then carries
`"retried": true`. `--dry-run` prints the table and writes no results file.

## Modes
- `skill`: AGENTS.md + turtleneck SKILL.md + all four references, plus the review or stress
  SKILL.md for those kinds, read from disk at run time. Never copied into evals/.
- `baseline`: "You are a senior software architect. Answer the question." and nothing else.
- `--dry-run`: no model calls; checks `fixtures/<id>.md` and `<id>.fail.md`, other cases skipped.

## Add a case
Add an object to `evals/cases.json` with `id`, `kind`, `level`, `prompt`, `expected_tags`, `notes`.
Drop a fixture at `fixtures/<id>.md`; a failing variant is `fixtures/<id>.fail.md`.
For a new kind, add a checker in `checks.run_checks` and assert it in `test_checks.py`.

## Results
Each real run writes `evals/results/<UTC timestamp>-<arm>.json`: user prompt, per-variant system
prompt, raw output, per-check pass/fail with a reason, and judge scores when `--judge` is set.
`--dry-run` writes nothing. The judge runs only for `decide` and `decided` cases; other kinds
record `{"skipped": "rubric applies to decision records only"}`.

## Checks
decide/full+deep headings: `heading_two_floors`, `heading_options`, `heading_stressors`,
`heading_price`, `heading_cross_examination`, `heading_decision`, `heading_flips_if`,
`heading_owner_decisions` required level-2 headings
decide/full+deep: `option_count` at least 3 option lines in Options (A./B./C., optional - or * bullet, optional ** bold)
decide/full+deep: `option_defers` one option mentions defer
decide/full+deep: `option_buys_or_reuses` one option mentions buy or reuse
decide/full+deep: `stressor_row_count` 8-12 rows in the first Stressors table; deep needs 20+
decide/full+deep: `absurd_stressor_count` at least 2 stressor rows contain "absurd"
decide/full+deep: `flips_if_bullet` a Flips if line starts with -, *, or a digit plus . or )
decide/full+deep: `give_up_in_decision` "give up" in the Decision section
decide/full+deep: `elevator_pass` the phrase "Elevator pass" appears
decide/full+deep: `residuality_pass` the phrase "Residuality pass" appears
decide/full+deep: `owner_stressors_present` the phrase "Owner stressors" appears
decide/full+deep: `owner_decision_question` an Owner decisions line ends in "?"
decide/deep: `incidence_word` "incidence" appears; `contagion_word` "contagion" appears
decide/napkin: `napkin_line_limit` at most 12 non-empty lines
decide/napkin: `give_up_present` "give up" appears
decide/napkin: `has_question` at least one "?"
decide/napkin: `no_table_rows` no line starts with "|"
gate: `gate_line_limit` at most 8 non-empty lines
gate: `gate_no_stressors_heading` no "## Stressors"
gate: `gate_no_table_rows` no line starts with "|"
gate: `gate_phrase` contains cheap to undo, not architecture, move on, or ponytail
decided: `decided_one_option` "one" near "options", or exactly one option line in Options
decided: `give_up_present` "give up" appears
decided: `no_relitigation` no "I recommend", "instead, consider", "you should reconsider", "reconsider the decision", or "reopen the decision"
review: `review_gap_lines` at least one `§…: <tag>: …` line
review: `review_expected_tags` every case `expected_tags` tag is present
review: `review_verdict_line` last line matches `<n> gaps. decision|description|deck` with optional trailing period
review: phrase banned checks are skipped so a reviewer can quote the cliché it is tagging
stress: `stress_components` contains "Components:"
stress: `stress_table` a markdown table with a separator row
stress: `stress_attractors` contains "Attractors"
stress: `stress_owner_stressors` contains "Owner stressors"
stress: `stress_no_decision` no "## Decision" and no "I recommend"
all kinds: `banned_best_practice` "best practice", `banned_industry_standard` "industry standard",
`banned_future_proof` "future-proof", `banned_it_depends` "it depends" not followed by "on" fail
all kinds: `banned_quality_ratings` fails when a row's first cell is a quality word and another
cell is exactly high/medium/low
all kinds: `banned_architect_quote` fails on Hohpe/O'Reilly/Fowler/Uncle Bob says/said/argues/wrote
all kinds: `banned_microservices_monolith` fails on "microservices vs monolith"

A failed or non-JSON model call records one failed `model_error` check instead of crashing the run.
