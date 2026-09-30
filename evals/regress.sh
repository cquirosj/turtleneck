#!/bin/sh
# Kata regression after a skill change: regenerate the six kata records, judge
# them, and compare the mean against the last committed scorecard.
#   ./evals/regress.sh                 (defaults below)
#   JUDGE_MODEL=ollama/deepseek-v4.1-flash:cloud ./evals/regress.sh
set -eu
cd "$(dirname "$0")/.."
MODEL="${MODEL:-deepseek-v4.1-flash:cloud}"
JUDGE_MODEL="${JUDGE_MODEL:-claude-bridge/claude-opus-5-5}"

python3 -m unittest discover -s evals -p "test_*.py" >/dev/null
previous=$(git ls-files 'evals/results/*-kata-scorecard.md' | sort | tail -1)

python3 evals/run.py --arm skill --cases evals/katas.json --model "$MODEL" --concurrency 3
results=$(ls -t evals/results/*-katas-skill.json | head -1)
python3 evals/kata_judge.py --results "$results" --judge-model "$JUDGE_MODEL" --concurrency 3
current=$(ls -t evals/results/*-kata-scorecard.md | head -1)

mean() { awk -F'|' '/^\| mean/ {gsub(/ /,"",$(NF-1)); print $(NF-1)}' "$1"; }
echo
echo "skill commit: $(git rev-parse --short HEAD)$(git diff --quiet -- skills AGENTS.md || echo ' (uncommitted skill changes)')"
if [ -n "$previous" ]; then
  echo "previous scorecard: $previous  mean $(mean "$previous")"
fi
echo "current scorecard:  $current  mean $(mean "$current")"
echo "commit the current scorecard alongside the skill change so the trend stays comparable."
