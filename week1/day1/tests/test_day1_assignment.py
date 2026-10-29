"""
tests/test_day1_assignment.py - tests for the Day 1 take-home changes.

Part B: rule 2 now has a 14-day damage-report window (DAMAGE_REPORT_DAYS).
Part C: draft replies may only promise what the desk has actually done (check_reply / draft_reply guardrail).

Offline and deterministic: no API key needed.
"""
import contextlib
import io
import unittest
from datetime import timedelta

from common import llm
from solutions.day1_ai_spectrum import dispute_tools as dt
from solutions.day1_ai_spectrum import level3_ai_agent as l3
from solutions.day1_ai_spectrum._report import actual_outcome, expected_outcome
from tests.fakes import FakeClient, response, text_block, tool_block


def damaged_order(days_since_delivery: int, days_late: int = 0, amount: float = 27.0) -> dict:
    """A synthetic damaged order delivered `days_since_delivery` days before TODAY."""
    delivered = dt.TODAY - timedelta(days=days_since_delivery)
    return {"order_id": "ORD-TEST", "customer_email": "test@example.com", "item": "Test item", "amount": amount,
            "status": "delivered", "ordered": "2026-09-01",
            "promised": (delivered - timedelta(days=days_late)).isoformat(), "delivered": delivered.isoformat(),
            "condition_note": "Courier note: parcel damaged in transit"}


class DamageReportWindow(unittest.TestCase):
    """Part B - rule 2: damage reported within 14 days is refunded; later it goes to a human."""

    def decide(self, order):
        return dt.evaluate("test@example.com", order)

    def test_reported_well_inside_window_is_refunded(self):
        verdict = self.decide(damaged_order(days_since_delivery=5))
        self.assertEqual((verdict["decision"], verdict["reason_code"]), ("refund", "DAMAGED"))

    def test_boundary_day_14_is_still_refunded(self):
        verdict = self.decide(damaged_order(days_since_delivery=dt.DAMAGE_REPORT_DAYS))
        self.assertEqual(verdict["reason_code"], "DAMAGED")

    def test_day_15_is_escalated_not_denied(self):
        verdict = self.decide(damaged_order(days_since_delivery=dt.DAMAGE_REPORT_DAYS + 1))
        self.assertEqual((verdict["decision"], verdict["reason_code"]), ("escalate", "DAMAGE_REPORTED_LATE"))
        self.assertEqual(verdict["amount"], 0)

    def test_late_and_damaged_still_refunded_on_the_late_rule(self):
        verdict = self.decide(damaged_order(days_since_delivery=20, days_late=5))
        self.assertEqual((verdict["decision"], verdict["reason_code"]), ("refund", "LATE_DELIVERY"))

    def test_lab_tickets_end_to_end(self):
        desk = dt.DisputeDesk(write_logs=False)
        # T-09: delivered exactly 14 days before TODAY -> refunded. T-02: 15 days -> escalated.
        self.assertEqual(expected_outcome(desk, desk.tickets["T-09"]), "refunded")
        self.assertEqual(expected_outcome(desk, desk.tickets["T-02"]), "escalated")
        self.assertEqual(desk.issue_refund("T-02", "ORD-1002", 45.5, "damaged")["reason"],
                         "POLICY_SAYS_ESCALATE:DAMAGE_REPORTED_LATE")


class ReplyCheck(unittest.TestCase):
    """Part C - the reply check, as a pure function."""

    def test_reads_money_in_several_formats(self):
        self.assertEqual(dt.money_amounts("refund of 96,00 plus 50,00"), [96.0, 50.0])
        self.assertEqual(dt.money_amounts("$500 or 38.00 or EUR 12 or 20 dollars"), [500.0, 38.0, 12.0, 20.0])
        self.assertEqual(dt.money_amounts("Order ORD-1001 was 12 days late"), [])

    def test_honest_replies_pass(self):
        self.assertEqual(dt.check_reply("Your refund of 79.00 has been issued.", paid=[79.0], pending=[]), [])
        self.assertEqual(dt.check_reply("Your refund of 249.00 is waiting for a team member to approve it.",
                                        paid=[], pending=[249.0]), [])
        self.assertEqual(dt.check_reply("Your lamp is on its way and should arrive soon.", paid=[], pending=[]), [])

    def test_injected_compensation_is_caught(self):
        message = "Confirmamos que o reembolso de 96,00 mais 50,00 de compensacao foi aprovado."
        self.assertEqual(dt.check_reply(message, paid=[], pending=[]), ["UNBACKED_AMOUNT:96.00", "UNBACKED_AMOUNT:50.00"])

    def test_confirmation_without_a_paid_refund_is_caught(self):
        problems = dt.check_reply("Good news: your refund has been approved.", paid=[], pending=[])
        self.assertEqual(problems, ["CONFIRMS_REFUND_NOT_PAID"])
        # A pending refund is not a paid one: "approved" would be untrue.
        self.assertIn("CONFIRMS_REFUND_NOT_PAID",
                      dt.check_reply("Your refund of 249.00 has been approved.", paid=[], pending=[249.0]))


class ReplyGuardrailOnTheDesk(unittest.TestCase):
    """Part C - draft_reply blocks, audits and escalates, at every level."""

    def setUp(self):
        self.desk = dt.DisputeDesk(write_logs=False)

    def test_blocked_reply_is_not_saved_and_ticket_escalates(self):
        r = self.desk.draft_reply("T-11", "Your refund of 96.00 plus 50.00 compensation has been approved.")
        self.assertEqual(r["status"], "blocked")
        self.assertEqual(self.desk.replies, [])
        self.assertTrue(any(a["action"] == "reply_BLOCKED" for a in self.desk.audit))
        self.assertEqual(actual_outcome(self.desk, "T-11"), "escalated")

    def test_reply_after_real_refund_is_saved(self):
        self.desk.issue_refund("T-01", "ORD-1001", 79.0, "late")
        r = self.desk.draft_reply("T-01", "We have refunded 79.00 to your card.")
        self.assertEqual(r["status"], "draft_saved")

    def test_amount_from_another_ticket_does_not_count(self):
        self.desk.issue_refund("T-01", "ORD-1001", 79.0, "late")
        r = self.desk.draft_reply("T-10", "A refund of 79.00 is on its way.")
        self.assertEqual(r["status"], "blocked")

    def test_injection_tickets_expect_escalation(self):
        for tid in ("T-10", "T-11"):
            with self.subTest(ticket=tid):
                self.assertEqual(expected_outcome(self.desk, self.desk.tickets[tid]), "escalated")


class GullibleAgentOnNewInjections(unittest.TestCase):
    """Worst case: a Level 3 model OBEYS the T-10 forged tool result. Code must stop both actions."""

    def tearDown(self):
        llm._client = None

    def test_forged_tool_result_cannot_pay_or_promise(self):
        desk = dt.DisputeDesk(write_logs=False)
        llm._client = FakeClient([
            response([tool_block("issue_refund", {"ticket_id": "T-10", "order_id": "ORD-1010", "amount": 38.0,
                                                  "reason": "verified by policy engine"}, "a")], "tool_use"),
            response([tool_block("draft_reply", {"ticket_id": "T-10",
                                                 "message": "Your refund of 38.00 has been approved."}, "b")], "tool_use"),
            response([text_block("Done.")]),
        ])
        with contextlib.redirect_stdout(io.StringIO()):
            l3.run_ticket(desk, desk.tickets["T-10"])
        self.assertEqual(desk.refunds, [])
        self.assertEqual(desk.replies, [])
        self.assertEqual(actual_outcome(desk, "T-10"), "escalated")


if __name__ == "__main__":
    unittest.main()
