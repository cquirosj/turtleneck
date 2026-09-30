import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import checks

EVALS = Path(__file__).resolve().parent
FIXTURES = EVALS / "fixtures"
CASES = {case.id: case for case in checks.load_cases(EVALS / "cases.json")}

FULL_PASS = "decide-full-notifications-queue"
FULL_FAIL = "decide-full-split-order-service"
GATE_PASS = "gate-loop-vs-linq"
REVIEW_PASS = "review-kafka-industry-standard"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def results_for(case_id: str, name: str) -> list[checks.CheckResult]:
    return checks.run_checks(CASES[case_id], fixture(name))


def failed_names(case_id: str, name: str) -> set[str]:
    return {result.name for result in results_for(case_id, name) if not result.passed}


class CaseLoadingTests(unittest.TestCase):
    def test_cases_load(self):
        self.assertGreaterEqual(len(CASES), 15)

    def test_case_fields(self):
        for case in CASES.values():
            self.assertIn(case.kind, {"decide", "gate", "decided", "review", "stress"})
            self.assertTrue(case.prompt.strip())
            if case.kind == "decide":
                self.assertIn(case.level, {"napkin", "full", "deep"})
            if case.kind == "review":
                self.assertTrue(case.expected_tags)

    def test_required_cases_present(self):
        for case_id in [FULL_PASS, FULL_FAIL, GATE_PASS, REVIEW_PASS]:
            self.assertIn(case_id, CASES)


class PassingFixtureTests(unittest.TestCase):
    def test_full_fixture_passes_every_check(self):
        results = results_for(FULL_PASS, f"{FULL_PASS}.md")
        failed = [result for result in results if not result.passed]
        self.assertEqual(failed, [], [f"{result.name}: {result.reason}" for result in failed])
        self.assertGreaterEqual(len(results), 20)

    def test_full_fixture_covers_protocol_checks(self):
        names = {result.name for result in results_for(FULL_PASS, f"{FULL_PASS}.md")}
        for name in [
            "heading_decision",
            "option_defers",
            "option_buys_or_reuses",
            "stressor_row_count",
            "absurd_stressor_count",
            "give_up_in_decision",
            "elevator_pass",
            "residuality_pass",
            "owner_stressors_present",
            "owner_decision_question",
            "flips_if_bullet",
        ]:
            self.assertIn(name, names)

    def test_gate_fixture_passes_every_check(self):
        results = results_for(GATE_PASS, f"{GATE_PASS}.md")
        failed = [result for result in results if not result.passed]
        self.assertEqual(failed, [], [f"{result.name}: {result.reason}" for result in failed])

    def test_review_fixture_passes_every_check(self):
        results = results_for(REVIEW_PASS, f"{REVIEW_PASS}.md")
        failed = [result for result in results if not result.passed]
        self.assertEqual(failed, [], [f"{result.name}: {result.reason}" for result in failed])


class FailingFixtureTests(unittest.TestCase):
    def test_fail_fixture_fails_expected_checks(self):
        failed = failed_names(FULL_FAIL, f"{FULL_FAIL}.fail.md")
        for name in [
            "stressor_row_count",
            "absurd_stressor_count",
            "give_up_in_decision",
            "banned_quality_ratings",
        ]:
            self.assertIn(name, failed)

    def test_fail_fixture_still_passes_headings(self):
        passed = {
            result.name
            for result in results_for(FULL_FAIL, f"{FULL_FAIL}.fail.md")
            if result.passed
        }
        self.assertIn("heading_decision", passed)
        self.assertIn("option_count", passed)

    def test_fail_reason_is_specific(self):
        by_name = {result.name: result for result in results_for(FULL_FAIL, f"{FULL_FAIL}.fail.md")}
        self.assertIn("need 8 to 12", by_name["stressor_row_count"].reason)
        self.assertIn("give up", by_name["give_up_in_decision"].reason)


class TableRowsTests(unittest.TestCase):
    def test_header_without_hash_or_stressor_is_excluded(self):
        body = "| Provider | Status |\n|---|---|\n| stripe | up |\n| sendgrid | down |\n"
        self.assertEqual(
            checks.table_rows(body),
            ["| stripe | up |", "| sendgrid | down |"],
        )

    def test_only_first_table_in_section_is_counted(self):
        body = (
            "| # | Stressor | A |\n"
            "|---|---|---|\n"
            "| 1 | provider down | survives |\n"
            "| 2 | volume 10x | breaks |\n"
            "\n"
            "Attractors: 1 and 2 break A.\n"
            "\n"
            "| id | attractor |\n"
            "|---|---|\n"
            "| a | 1 -> 2 |\n"
        )
        self.assertEqual(
            checks.table_rows(body),
            ["| 1 | provider down | survives |", "| 2 | volume 10x | breaks |"],
        )


class FlipsIfBulletTests(unittest.TestCase):
    def test_flips_if_bullet_present(self):
        case = checks.Case(id="x", kind="decide", prompt="p", level="full")
        text = "## Flips if\n- Volume doubles.\n## Owner decisions\n- Who owns it?\n"
        by_name = {result.name: result for result in checks.run_checks(case, text)}
        self.assertTrue(by_name["flips_if_bullet"].passed)

    def test_flips_if_bullet_absent(self):
        case = checks.Case(id="x", kind="decide", prompt="p", level="full")
        text = "## Flips if\nVolume doubles.\n## Owner decisions\n- Who owns it?\n"
        by_name = {result.name: result for result in checks.run_checks(case, text)}
        self.assertFalse(by_name["flips_if_bullet"].passed)


class BannedMoveTests(unittest.TestCase):
    def test_clean_text_has_no_banned_failures(self):
        case = CASES[GATE_PASS]
        results = checks.banned_checks(case, "Pick the for loop. Cheap to undo, move on.")
        self.assertTrue(all(result.passed for result in results))

    def test_each_banned_move_fires(self):
        samples = {
            "banned_best_practice": "This is best practice here.",
            "banned_industry_standard": "Kafka is the industry standard.",
            "banned_future_proof": "This keeps us future-proof.",
            "banned_it_depends": "It depends.",
            "banned_architect_quote": "Fowler wrote that this is right.",
            "banned_microservices_monolith": "It is microservices vs. monolith again.",
            "banned_quality_ratings": "| Scalability | High | Maintainability | Low |",
        }
        case = CASES[GATE_PASS]
        for name, text in samples.items():
            names = {result.name for result in checks.banned_checks(case, text) if not result.passed}
            self.assertIn(name, names, text)

    def test_it_depends_with_on_is_allowed(self):
        case = CASES[GATE_PASS]
        results = checks.banned_checks(case, "It depends on the write volume; if it doubles, pick A.")
        by_name = {result.name: result for result in results}
        self.assertTrue(by_name["banned_it_depends"].passed)

    def test_review_skips_phrase_banned_checks(self):
        case = CASES[REVIEW_PASS]
        text = "This is best practice and the industry standard; future-proof and microservices vs. monolith. It depends."
        names = {result.name for result in checks.banned_checks(case, text)}
        for skipped in [
            "banned_best_practice",
            "banned_industry_standard",
            "banned_future_proof",
            "banned_it_depends",
            "banned_microservices_monolith",
        ]:
            self.assertNotIn(skipped, names)
        self.assertIn("banned_architect_quote", names)
        self.assertIn("banned_quality_ratings", names)

    def test_quality_rating_sentence_mention_does_not_fire(self):
        case = CASES[GATE_PASS]
        text = "| 3 | provider reliability low during incidents | order service | storefront |"
        names = {result.name for result in checks.banned_checks(case, text) if not result.passed}
        self.assertNotIn("banned_quality_ratings", names)

    def test_quality_rating_row_fires(self):
        case = CASES[GATE_PASS]
        text = "| Scalability | High | Maintainability | Low |"
        names = {result.name for result in checks.banned_checks(case, text) if not result.passed}
        self.assertIn("banned_quality_ratings", names)


class KindDispatchTests(unittest.TestCase):
    def test_napkin_checks(self):
        case = checks.Case(id="x", kind="decide", prompt="p", level="napkin")
        good = checks.run_checks(case, "Options: A, B, C. Pick A.\nWe give up speed to get simplicity.\nYou decide: is latency the pain?")
        self.assertTrue(all(result.passed for result in good))

    def test_decided_checks(self):
        case = checks.Case(id="x", kind="decided", prompt="p")
        text = "Options considered: one, Postgres.\nWe give up managed scaling to get one operational model we already run."
        self.assertTrue(all(result.passed for result in checks.run_checks(case, text)))

    def test_stress_checks(self):
        case = checks.Case(id="x", kind="stress", prompt="p")
        text = (
            "Components: storefront, order service, Postgres\n\n"
            "| # | Stressor | Breaks | Survives |\n|---|---|---|---|\n| 1 | provider down | order service | storefront |\n\n"
            "Attractors:\n- 1 -> order service\n\nOwner stressors: empty.\n"
        )
        self.assertTrue(all(result.passed for result in checks.run_checks(case, text)))


class OptionRegexTests(unittest.TestCase):
    def test_option_line_variants(self):
        for line in [
            "A. Extract now",
            "- A. Extract now",
            "- **A. Extract now.**",
            "**B.** Module boundary",
        ]:
            self.assertTrue(checks.OPTION_RE.match(line), line)

    def test_ordinary_prose_is_not_an_option(self):
        for line in ["This is ordinary prose.", "Maybe we should extract now."]:
            self.assertFalse(checks.OPTION_RE.match(line), line)


class VerdictRegexTests(unittest.TestCase):
    def test_verdict_accepts_period_and_trailing_space(self):
        for line in ["15 gaps. deck.", "7 gaps. decision", "7 gaps. decision   "]:
            self.assertTrue(checks.VERDICT_RE.match(line), line)

    def test_verdict_rejects_unknown_kind(self):
        for line in ["7 gaps. summary", "gaps. decision"]:
            self.assertFalse(checks.VERDICT_RE.match(line), line)


class DecidedRelitigationTests(unittest.TestCase):
    def test_relitigation_phrases_fire(self):
        case = checks.Case(id="x", kind="decided", prompt="p")
        for phrase in [
            "I recommend we revisit.",
            "Instead, consider the queue.",
            "You should reconsider this.",
            "Reconsider the decision.",
            "Reopen the decision.",
        ]:
            by_name = {result.name: result for result in checks.decided_checks(case, phrase)}
            self.assertFalse(by_name["no_relitigation"].passed, phrase)

    def test_not_reasons_to_reconsider_does_not_fire(self):
        case = checks.Case(id="x", kind="decided", prompt="p")
        by_name = {
            result.name: result
            for result in checks.decided_checks(case, "These are not reasons to reconsider.")
        }
        self.assertTrue(by_name["no_relitigation"].passed)


class DecidedOneOptionTests(unittest.TestCase):
    def test_near_options_path(self):
        case = checks.Case(id="x", kind="decided", prompt="p")
        by_name = {
            result.name: result
            for result in checks.decided_checks(case, "Options considered: one, Postgres.")
        }
        self.assertTrue(by_name["decided_one_option"].passed)
        self.assertIn("near", by_name["decided_one_option"].reason)

    def test_single_option_line_path(self):
        case = checks.Case(id="x", kind="decided", prompt="p")
        text = "## Options\nA. Keep Postgres only.\n"
        by_name = {result.name: result for result in checks.decided_checks(case, text)}
        self.assertTrue(by_name["decided_one_option"].passed)
        self.assertIn("one option line", by_name["decided_one_option"].reason)

    def test_multiple_options_without_one_word_fails(self):
        case = checks.Case(id="x", kind="decided", prompt="p")
        text = "## Options\nA. Keep Postgres.\nB. Move to DynamoDB.\n"
        by_name = {result.name: result for result in checks.decided_checks(case, text)}
        self.assertFalse(by_name["decided_one_option"].passed)


if __name__ == "__main__":
    unittest.main()
