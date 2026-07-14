from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from assessment_core import Answer, AssessmentError, Check, evaluate  # noqa: E402


def check(check_id: str, priority: str = "high", domain: str = "Runtime") -> Check:
    return Check(check_id, domain, priority, "description", "evidence", "action")


def answer(check_id: str, status: str) -> Answer:
    return Answer(check_id, status, "evidence", "owner", "2026-12-01", "")


class EvaluationTest(unittest.TestCase):
    def test_ready_when_weighted_score_is_at_least_85(self) -> None:
        result = evaluate(
            [check("A"), check("B"), check("C")],
            [answer("A", "pass"), answer("B", "pass"), answer("C", "pass")],
        )
        self.assertEqual("READY", result["decision"])

    def test_score_between_65_and_85_is_conditional(self) -> None:
        result = evaluate(
            [check("A"), check("B"), check("C")],
            [answer("A", "pass"), answer("B", "pass"), answer("C", "partial")],
        )
        self.assertEqual("CONDITIONAL", result["decision"])
        self.assertEqual(83.3, result["score"])

    def test_critical_failure_blocks_even_with_high_score(self) -> None:
        result = evaluate(
            [check("A", "critical"), check("B", "critical"), check("C", "critical")],
            [answer("A", "fail"), answer("B", "pass"), answer("C", "pass")],
        )
        self.assertEqual("BLOCKED", result["decision"])
        self.assertEqual(["A"], [item["id"] for item in result["critical_blockers"]])

    def test_score_below_65_is_blocked(self) -> None:
        result = evaluate(
            [check("A"), check("B")],
            [answer("A", "pass"), answer("B", "fail")],
        )
        self.assertEqual("BLOCKED", result["decision"])

    def test_na_is_excluded_from_denominator(self) -> None:
        result = evaluate(
            [check("A"), check("B")],
            [answer("A", "pass"), answer("B", "na")],
        )
        self.assertEqual(100.0, result["score"])

    def test_missing_answer_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssessmentError, "Missing assessment ids: B"):
            evaluate([check("A"), check("B")], [answer("A", "pass")])

    def test_failed_action_precedes_partial_at_same_priority(self) -> None:
        result = evaluate(
            [check("A"), check("B")],
            [answer("A", "partial"), answer("B", "fail")],
        )
        self.assertEqual(["B", "A"], [item["id"] for item in result["priority_actions"]])

    def test_unknown_critical_check_blocks_assessment(self) -> None:
        result = evaluate([check("A", "critical")], [answer("A", "unknown")])
        self.assertEqual("BLOCKED", result["decision"])
        self.assertEqual(["A"], [item["id"] for item in result["critical_blockers"]])


if __name__ == "__main__":
    unittest.main()
