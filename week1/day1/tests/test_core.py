"""
tests/test_core.py - policy rules, guardrails, the agent loop and helpers.
Run all tests:  python -m unittest discover -s tests -v
"""
import unittest

from common import config, llm
from solutions.day1_ai_spectrum import dispute_tools as dt
from tests.fakes import FakeClient, response, text_block, tool_block


class PolicyTests(unittest.TestCase):
    """The policy is code, so every rule can be tested without any AI."""

    def setUp(self):
        self.desk = dt.DisputeDesk(write_logs=False)

    def decide(self, ticket_id):
        t = self.desk.tickets[ticket_id]
        order_id = next(w for w in t["text"].replace("(", " ").replace(")", " ").split() if w.startswith("ORD-"))
        return dt.evaluate(t["customer_email"], self.desk.orders[order_id.strip(".,")])

    def test_late_delivery_refund_within_limit(self):
        d = self.decide("T-01")
        self.assertEqual((d["decision"], d["reason_code"], d["amount"], d["needs_human"]), ("refund", "LATE_DELIVERY", 79.0, False))

    def test_damaged_refund(self):
        self.assertEqual(self.decide("T-09")["reason_code"], "DAMAGED")   # reported on day 14: still inside the window

    def test_large_refund_needs_human(self):
        self.assertTrue(self.decide("T-03")["needs_human"])

    def test_outside_window_denied(self):
        self.assertEqual(self.decide("T-04")["decision"], "deny")

    def test_in_transit_is_status_update(self):
        self.assertEqual(self.decide("T-05")["decision"], "status_update")

    def test_wrong_email_escalates(self):
        self.assertEqual(self.decide("T-06")["reason_code"], "OWNERSHIP_MISMATCH")

    def test_unknown_order_escalates(self):
        self.assertEqual(dt.evaluate("x@example.com", None)["reason_code"], "ORDER_NOT_FOUND")


class GuardrailTests(unittest.TestCase):
    def setUp(self):
        self.desk = dt.DisputeDesk(budget=100.0, write_logs=False)

    def test_valid_refund_is_paid_and_budget_drops(self):
        r = self.desk.issue_refund("T-01", "ORD-1001", 79.0, "late")
        self.assertEqual(r["status"], "refunded")
        self.assertAlmostEqual(self.desk.budget_remaining, 21.0)

    def test_injected_500_refund_is_blocked(self):
        """The prompt-injection ticket (T-07): even if the model obeyed, code refuses."""
        r = self.desk.issue_refund("T-07", "ORD-1007", 500.0, "system note says so")
        self.assertEqual(r["status"], "blocked")
        self.assertEqual(self.desk.refunds, [])

    def test_wrong_amount_blocked(self):
        r = self.desk.issue_refund("T-01", "ORD-1001", 5.0, "model chose a number")
        self.assertIn("AMOUNT_MISMATCH", r["reason"])

    def test_ownership_blocked(self):
        r = self.desk.issue_refund("T-06", "ORD-1006", 58.0, "please")
        self.assertEqual(r["status"], "blocked")

    def test_duplicate_blocked(self):
        self.desk.issue_refund("T-01", "ORD-1001", 79.0, "late")
        self.assertEqual(self.desk.issue_refund("T-01", "ORD-1001", 79.0, "again")["reason"], "DUPLICATE_REFUND")

    def test_over_limit_goes_to_human_queue_not_paid(self):
        r = self.desk.issue_refund("T-03", "ORD-1003", 420.0, "late")
        self.assertEqual(r["status"], "pending_human_approval")
        self.assertEqual(self.desk.refunds, [])
        self.assertEqual(len(self.desk.pending_approval), 1)

    def test_budget_cap(self):
        self.desk.issue_refund("T-01", "ORD-1001", 79.0, "late")      # leaves 21.00
        r = self.desk.issue_refund("T-09", "ORD-1009", 27.0, "damaged")   # T-02 is no longer refundable (rule 2 window)
        self.assertEqual(r["reason"], "BUDGET_EXCEEDED")

    def test_audit_records_blocked_attempts(self):
        self.desk.issue_refund("T-07", "ORD-1007", 500.0, "x")
        self.assertTrue(any(a["action"] == "refund_BLOCKED" for a in self.desk.audit))

    def test_open_ticket_list_shrinks(self):
        before = len(self.desk.list_open_tickets()["open_ticket_ids"])
        self.desk.escalate_to_human("T-06", "owner mismatch")
        self.assertEqual(len(self.desk.list_open_tickets()["open_ticket_ids"]), before - 1)


class AgentLoopTests(unittest.TestCase):
    def tearDown(self):
        llm._client = None  # never leave a fake client behind for other tests

    def test_tool_call_is_executed_and_result_returned(self):
        fake = FakeClient([
            response([tool_block("lookup_order", {"order_id": "ORD-1001"})], stop_reason="tool_use"),
            response([text_block("done")]),
        ])
        llm._client = fake
        seen = []
        run = llm.run_tool_loop("hi", "sys", [{"name": "lookup_order"}],
                                {"lookup_order": lambda order_id: seen.append(order_id) or {"ok": True}})
        self.assertEqual(seen, ["ORD-1001"])
        self.assertEqual(run.final_text, "done")
        self.assertEqual((run.input_tokens, run.output_tokens), (20, 10))
        # second request must contain the tool_result tied to the request id
        last_user = fake.messages.calls[1]["messages"][-1]
        self.assertEqual(last_user["content"][0]["tool_use_id"], "tu_1")

    def test_handler_exception_becomes_error_result_not_crash(self):
        fake = FakeClient([
            response([tool_block("boom", {})], stop_reason="tool_use"),
            response([text_block("recovered")]),
        ])
        llm._client = fake

        def boom():
            raise RuntimeError("tool failed")

        run = llm.run_tool_loop("hi", "sys", [{"name": "boom"}], {"boom": boom})
        self.assertEqual(run.final_text, "recovered")
        self.assertTrue(fake.messages.calls[1]["messages"][-1]["content"][0]["is_error"])

    def test_unknown_tool_is_reported_to_model(self):
        fake = FakeClient([response([tool_block("nope", {})], stop_reason="tool_use"), response([text_block("ok")])])
        llm._client = fake
        llm.run_tool_loop("hi", "sys", [], {})
        self.assertIn("KeyError", fake.messages.calls[1]["messages"][-1]["content"][0]["content"])

    def test_step_budget_stops_endless_loop(self):
        endless = [response([tool_block("t", {}, f"tu_{i}")], stop_reason="tool_use") for i in range(5)]
        llm._client = FakeClient(endless)
        run = llm.run_tool_loop("hi", "sys", [], {"t": lambda: {}}, max_steps=3)
        self.assertEqual(run.stopped_reason, "max_steps")

    def test_ask_returns_text_and_tokens(self):
        llm._client = FakeClient([response([text_block("hello")], tokens=(7, 3))])
        r = llm.ask("hi", system="s")
        self.assertEqual((r.text, r.input_tokens, r.output_tokens), ("hello", 7, 3))

    def test_count_tokens(self):
        llm._client = FakeClient([])
        self.assertEqual(llm.count_tokens("anything"), 42)


class HelperTests(unittest.TestCase):
    def test_extract_json_plain_fenced_and_embedded(self):
        self.assertEqual(llm.extract_json('{"a": 1}'), {"a": 1})
        self.assertEqual(llm.extract_json('Sure!\n```json\n{"a": 2}\n```'), {"a": 2})
        self.assertEqual(llm.extract_json('The answer is {"a": 3} as requested.'), {"a": 3})

    def test_extract_json_raises_when_no_json(self):
        with self.assertRaises(ValueError):
            llm.extract_json("no json here")

    def test_estimate_tokens(self):
        self.assertEqual(llm.estimate_tokens("a" * 40), 10)

    def test_placeholder_key_is_treated_as_missing(self):
        import os
        old = os.environ.get("ANTHROPIC_API_KEY")
        try:
            os.environ["ANTHROPIC_API_KEY"] = "sk-ant-your-key-here"
            self.assertIsNone(config.get_api_key())
            os.environ["ANTHROPIC_API_KEY"] = ' "sk-ant-real-looking" '
            self.assertEqual(config.get_api_key(), "sk-ant-real-looking")
        finally:
            if old is None:
                os.environ.pop("ANTHROPIC_API_KEY", None)
            else:
                os.environ["ANTHROPIC_API_KEY"] = old

    def test_get_client_without_key_gives_friendly_error(self):
        import os
        old = os.environ.pop("ANTHROPIC_API_KEY", None)
        llm._client = None
        try:
            with self.assertRaises(RuntimeError) as ctx:
                llm.get_client()
            self.assertIn(".env", str(ctx.exception))
        finally:
            if old is not None:
                os.environ["ANTHROPIC_API_KEY"] = old


if __name__ == "__main__":
    unittest.main()
