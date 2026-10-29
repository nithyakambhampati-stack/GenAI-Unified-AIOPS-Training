"""
tests/test_levels.py - the five spectrum levels, exercised with scripted fake models.
No network, no API key, deterministic.
"""
import json
import unittest
from unittest import mock

from common import llm
from solutions.day1_ai_spectrum import (level1_traditional_automation as l1, level2_ai_automation as l2,
                                        level3_ai_agent as l3, level4_multi_agent as l4, level5_agentic_ai as l5)
from solutions.day1_ai_spectrum import dispute_tools as dt
from solutions.day1_ai_spectrum._report import actual_outcome, expected_outcome
from tests.fakes import FakeClient, response, text_block, tool_block


def result(text):
    return llm.LLMResult(text=text, model="fake", input_tokens=1, output_tokens=1, latency_s=0.0)


class Level1(unittest.TestCase):
    def test_keyword_rules_miss_the_paraphrase_ticket(self):
        desk = dt.DisputeDesk(write_logs=False)
        for t in desk.tickets.values():
            l1.handle(desk, t)
        wrong = [tid for tid in desk.tickets if actual_outcome(desk, tid) != expected_outcome(desk, desk.tickets[tid])]
        self.assertEqual(wrong, ["T-08"])  # "return my payment" contains no refund keyword

    def test_classify_misses_synonyms(self):
        self.assertEqual(l1.classify("I'd like to be reimbursed for ORD-1002")[0], "other")


class Level2(unittest.TestCase):
    def test_workflow_routes_by_python_not_model(self):
        desk = dt.DisputeDesk(write_logs=False)
        info = json.dumps({"intent": "refund_request", "order_id": "ORD-1001", "injection_suspected": False, "summary": "late"})
        with mock.patch.object(l2.llm, "ask", side_effect=[result(info), result("Your refund is on its way.")]):
            note = l2.handle(desk, desk.tickets["T-01"])
        self.assertEqual(note, "refund -> refunded")
        self.assertEqual(actual_outcome(desk, "T-01"), "refunded")

    def test_injection_flag_escalates(self):
        desk = dt.DisputeDesk(write_logs=False)
        info = json.dumps({"intent": "refund_request", "order_id": "ORD-1007", "injection_suspected": True, "summary": "x"})
        with mock.patch.object(l2.llm, "ask", return_value=result(info)):
            l2.handle(desk, desk.tickets["T-07"])
        self.assertEqual(actual_outcome(desk, "T-07"), "escalated")

    def test_garbage_model_output_fails_safe(self):
        desk = dt.DisputeDesk(write_logs=False)
        with mock.patch.object(l2.llm, "ask", return_value=result("I am not JSON at all")):
            l2.handle(desk, desk.tickets["T-01"])
        self.assertEqual(actual_outcome(desk, "T-01"), "escalated")
        self.assertEqual(desk.refunds, [])


class Level3(unittest.TestCase):
    def tearDown(self):
        llm._client = None

    def test_agent_refunds_and_replies(self):
        desk = dt.DisputeDesk(write_logs=False)
        llm._client = FakeClient([
            response([tool_block("lookup_order", {"order_id": "ORD-1001"}, "a")], "tool_use"),
            response([tool_block("issue_refund", {"ticket_id": "T-01", "order_id": "ORD-1001", "amount": 79.0, "reason": "late"}, "b")], "tool_use"),
            response([tool_block("draft_reply", {"ticket_id": "T-01", "message": "Refunded."}, "c")], "tool_use"),
            response([text_block("Done.")]),
        ])
        l3.run_ticket(desk, desk.tickets["T-01"])
        self.assertEqual(actual_outcome(desk, "T-01"), "refunded")

    def test_gullible_model_is_still_stopped_by_guardrails(self):
        """Worst case: the model OBEYS the injected instruction in T-07. Code must still block it."""
        desk = dt.DisputeDesk(write_logs=False)
        llm._client = FakeClient([
            response([tool_block("issue_refund", {"ticket_id": "T-07", "order_id": "ORD-1007", "amount": 500, "reason": "system note"}, "a")], "tool_use"),
            response([text_block("I could not refund; escalating.")]),
        ])
        l3.run_ticket(desk, desk.tickets["T-07"])
        self.assertEqual(desk.refunds, [])
        self.assertTrue(any(a["action"] == "refund_BLOCKED" for a in desk.audit))


class Level4(unittest.TestCase):
    FACTS = json.dumps({"order_id": "ORD-1002", "order_found": True, "status": "delivered", "amount": 45.5})

    def run_handle(self, proposal, verdict, ticket_id="T-02"):
        desk = dt.DisputeDesk(write_logs=False)
        agent = mock.Mock(return_value=llm.AgentRun(final_text=self.FACTS))
        asks = [result(json.dumps(proposal)), result(json.dumps(verdict))]
        with mock.patch.object(l4.llm, "run_tool_loop", agent), mock.patch.object(l4.llm, "ask", side_effect=asks):
            note = l4.handle(desk, desk.tickets[ticket_id], verbose=False)
        return desk, note

    def test_approved_refund_executes(self):
        desk, note = self.run_handle({"action": "refund", "amount": 45.5, "reasoning": "damaged"}, {"verdict": "approve", "reason": "ok"})
        self.assertEqual(note, "refund -> refunded")
        self.assertEqual(len(desk.refunds), 1)

    def test_reviewer_rejection_escalates_and_pays_nothing(self):
        desk, note = self.run_handle({"action": "refund", "amount": 45.5, "reasoning": "damaged"}, {"verdict": "reject", "reason": "doubt"})
        self.assertIn("escalated", note)
        self.assertEqual(desk.refunds, [])

    def test_approved_but_wrong_proposal_is_blocked_by_code(self):
        # Reviewer and resolver both wrongly agree on a 500 refund; the guardrail still refuses.
        desk, note = self.run_handle({"action": "refund", "amount": 500, "reasoning": "x"}, {"verdict": "approve", "reason": "ok"})
        self.assertIn("guardrail blocked", note)
        self.assertEqual(desk.refunds, [])


class Level5(unittest.TestCase):
    def tearDown(self):
        llm._client = None

    def test_queue_run_handles_tickets_and_respects_limits(self):
        desk = dt.DisputeDesk(budget=300, write_logs=False)
        tools, handlers = dt.build_tools(desk, dt.QUEUE)
        script = [
            response([tool_block("issue_refund", {"ticket_id": "T-03", "order_id": "ORD-1003", "amount": 420, "reason": "late"}, "a"),
                      tool_block("issue_refund", {"ticket_id": "T-07", "order_id": "ORD-1007", "amount": 500, "reason": "injected"}, "b"),
                      tool_block("escalate_to_human", {"ticket_id": "T-07", "reason": "injection"}, "c")], "tool_use"),
            response([text_block("Summary")]),
        ]
        llm._client = FakeClient(script)
        run = llm.run_tool_loop("clear queue", l5.GOAL_SYSTEM, tools, handlers, max_steps=5)
        self.assertEqual(run.final_text, "Summary")
        self.assertEqual(actual_outcome(desk, "T-03"), "pending_approval")   # queued, not paid
        self.assertEqual(desk.refunds, [])
        self.assertEqual(actual_outcome(desk, "T-07"), "escalated")


if __name__ == "__main__":
    unittest.main()
