import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import kata_judge

KEYS = kata_judge.CRITERION_KEYS


def full_scores(value: int) -> dict:
    return {key: value for key in KEYS}


def judgement(case_id: str, value: int, move: str) -> dict:
    return {
        "id": case_id,
        "scores": full_scores(value),
        "whys": {key: "because" for key in KEYS},
        "strongest_line": "a line worth keeping",
        "weakest_move": move,
        "raw": "",
        "error": None,
    }


class ParseJudgeTests(unittest.TestCase):
    def test_clean_json(self):
        payload = {
            **{key: {"score": 4, "why": f"why {key}"} for key in KEYS},
            "strongest_line": "we give up reach to get a stable settlement window",
            "weakest_move": "prices the migration but not the dual-run cost",
        }
        parsed = kata_judge.parse_judge(json.dumps(payload))
        self.assertTrue(parsed["parsed"])
        for key in KEYS:
            self.assertEqual(parsed["scores"][key], 4)
            self.assertEqual(parsed["whys"][key], f"why {key}")
        self.assertIn("stable settlement window", parsed["strongest_line"])
        self.assertIn("dual-run cost", parsed["weakest_move"])

    def test_clamps_and_coerces_flat_scores(self):
        parsed = kata_judge.parse_judge(json.dumps({"load_bearing": "5", "uses_brief": 9}))
        self.assertEqual(parsed["scores"]["load_bearing"], 5)
        self.assertEqual(parsed["scores"]["uses_brief"], 5)

    def test_fenced_json(self):
        body = {
            **{key: {"score": 3, "why": "ok"} for key in KEYS},
            "strongest_line": "quote",
            "weakest_move": "move",
        }
        text = "```json\n" + json.dumps(body) + "\n```"
        parsed = kata_judge.parse_judge(text)
        self.assertTrue(parsed["parsed"])
        self.assertEqual(parsed["scores"]["coupling_found"], 3)
        self.assertEqual(parsed["weakest_move"], "move")

    def test_partially_broken_json_falls_back_per_key(self):
        text = (
            "{\n"
            '  "load_bearing": {"score": 5, "why": "hardest to undo"},\n'
            '  "uses_brief": {"score": 4, "why": "uses the scale"},\n'
            '  "options_differ_in_kind": {"score": 3,\n'
            '  "stressors_specific": 2,\n'
            '  "strongest_line": "we give up overseas reach",\n'
            '  "weakest_move": "generic cloud vendor list"\n'
        )
        parsed = kata_judge.parse_judge(text)
        self.assertFalse(parsed["parsed"])
        self.assertEqual(parsed["scores"]["load_bearing"], 5)
        self.assertEqual(parsed["scores"]["uses_brief"], 4)
        self.assertEqual(parsed["scores"]["options_differ_in_kind"], 3)
        self.assertEqual(parsed["scores"]["stressors_specific"], 2)
        self.assertIsNone(parsed["scores"]["price_realistic"])
        self.assertIn("overseas reach", parsed["strongest_line"])
        self.assertIn("generic cloud", parsed["weakest_move"])

    def test_garbage_yields_all_missing(self):
        parsed = kata_judge.parse_judge("the model refused to answer")
        self.assertFalse(parsed["parsed"])
        self.assertTrue(all(score is None for score in parsed["scores"].values()))


class ScorecardTests(unittest.TestCase):
    def setUp(self):
        self.scorecard = kata_judge.render_scorecard(
            [judgement("case-a", 5, "weak move a"), judgement("case-b", 3, "weak move b")],
            model="ollama/test",
            results_path="evals/results/example.json",
        )

    def test_header_has_abbreviations(self):
        header = self.scorecard.splitlines()[4]
        for _, abbrev, _ in kata_judge.CRITERIA:
            self.assertIn(f" {abbrev} ", header)
        self.assertIn("total/50", header)

    def test_case_rows_and_totals(self):
        self.assertIn("| case-a |", self.scorecard)
        self.assertIn("| case-b |", self.scorecard)
        self.assertIn("| 50 |", self.scorecard)
        self.assertIn("| 30 |", self.scorecard)

    def test_mean_row(self):
        mean_line = next(line for line in self.scorecard.splitlines() if line.startswith("| mean |"))
        self.assertIn("4.0", mean_line)
        self.assertIn("| 40.0 |", mean_line)

    def test_weakest_moves_and_lowest(self):
        self.assertIn("- case-a: weak move a", self.scorecard)
        self.assertIn("- case-b: weak move b", self.scorecard)
        self.assertIn("Lowest mean criteria:", self.scorecard)

    def test_errored_case_renders_placeholder(self):
        errored = judgement("case-c", 0, "")
        errored["scores"] = {key: None for key in KEYS}
        errored["error"] = "pi exited 1"
        card = kata_judge.render_scorecard([errored, judgement("case-d", 5, "move d")])
        self.assertIn("| case-c |", card)
        self.assertIn("- case-c: pi exited 1", card)
        mean_line = next(line for line in card.splitlines() if line.startswith("| mean |"))
        self.assertIn("| 50.0 |", mean_line)


class RoutingTests(unittest.TestCase):
    def test_ollama_prefix_strips_and_routes_to_ollama(self):
        calls = []

        def fake_ollama(model, system, user):
            calls.append(("ollama", model, system, user))
            return "judge text", None

        def fake_pi(model, system, user):
            calls.append(("pi", model, system, user))
            return "pi text", None

        raw, error = kata_judge.route_model(
            "ollama/llama3.1", "sys", "user", ollama=fake_ollama, pi=fake_pi
        )
        self.assertEqual(raw, "judge text")
        self.assertIsNone(error)
        self.assertEqual(calls, [("ollama", "llama3.1", "sys", "user")])

    def test_any_other_model_routes_to_pi(self):
        calls = []

        def fake_ollama(model, system, user):
            calls.append(("ollama", model))
            return "ollama", None

        def fake_pi(model, system, user):
            calls.append(("pi", model, system, user))
            return "pi text", None

        raw, error = kata_judge.route_model(
            "claude-bridge/claude-sonnet-5", "sys", "user", ollama=fake_ollama, pi=fake_pi
        )
        self.assertEqual(raw, "pi text")
        self.assertIsNone(error)
        self.assertEqual(calls, [("pi", "claude-bridge/claude-sonnet-5", "sys", "user")])

    def test_error_propagates_from_injected_callable(self):
        def fake_pi(model, system, user):
            return "", "pi exited 1: boom"

        _, error = kata_judge.route_model("m", "sys", "user", pi=fake_pi)
        self.assertEqual(error, "pi exited 1: boom")


class JudgeCaseTests(unittest.TestCase):
    def test_empty_output_is_not_sent_to_model(self):
        called = []

        def fake_ollama(model, system, user):
            called.append(model)
            return "{}", None

        result = kata_judge.judge_case(
            {"id": "empty", "prompt": "brief", "output": "  "}, "ollama/x", ollama=fake_ollama
        )
        self.assertEqual(called, [])
        self.assertEqual(result["error"], "no output to judge")
        self.assertTrue(all(score is None for score in result["scores"].values()))

    def test_case_error_is_reported(self):
        result = kata_judge.judge_case(
            {"id": "broken", "prompt": "brief", "output": "text", "error": "model_error"},
            "ollama/x",
            ollama=lambda *a: ("", None),
        )
        self.assertIn("model_error", result["error"])


class HashTests(unittest.TestCase):
    def test_hash_of_first_system_prompt(self):
        import hashlib

        digest = kata_judge.system_prompt_hash({"system_prompts": {"skill": "abc", "baseline": "def"}})
        self.assertEqual(digest, hashlib.sha256(b"abc").hexdigest())

    def test_hash_absent_when_no_prompts(self):
        self.assertIsNone(kata_judge.system_prompt_hash({"cases": []}))


if __name__ == "__main__":
    unittest.main()
