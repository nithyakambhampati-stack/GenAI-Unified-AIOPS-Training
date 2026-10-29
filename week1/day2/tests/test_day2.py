"""
tests/test_day2.py - verification, embeddings, redaction, CLI wrapper, homework pack.
"""
import json
import subprocess
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

from common import config
from solutions.day2_models_and_embeddings import compare_tiers_cli as cli
from solutions.day2_models_and_embeddings import embeddings_map as emb
from solutions.day2_models_and_embeddings import redact_pii, verify_outputs as vo

DOC = (vo.DATA_DIR / "vendor_clause.txt").read_text(encoding="utf-8")


class Verification(unittest.TestCase):
    def good(self):
        q = {"monthly_fee": "a fixed monthly fee of 12,400.00 for the Managed Support Service",
             "late_interest_pct_month": "Invoices unpaid after 30 days incur interest at 1.5% per month on the overdue amount",
             "credit_percent_per_step": "credit 5% of that month's fee for each full 0.5 percentage points below 99.5%",
             "credit_cap_percent": "up to a maximum credit of 20% of the monthly fee",
             "credit_for_98_6": "credit 5% of that month's fee for each full 0.5 percentage points below 99.5%",
             "termination_charge_8m": "an early-termination charge equal to two months' fees applies"}
        vals = vo.ground_truth()
        return {k: {"value": vals[k], "quote": q[k]} for k in q}

    def test_ground_truth(self):
        t = vo.ground_truth()
        self.assertEqual((t["credit_for_98_6"], t["termination_charge_8m"]), (620.0, 24800.0))

    def test_correct_findings_are_low_risk(self):
        checks = vo.verify(self.good(), DOC)
        self.assertTrue(all(c["passed"] for c in checks))
        self.assertEqual(vo.risk_tier(checks)[0], "LOW")

    def test_fabricated_quote_is_high_risk(self):
        findings = json.loads(vo.OFFLINE_REPLY)
        self.assertEqual(vo.risk_tier(vo.verify(findings, DOC))[0], "HIGH")

    def test_wrong_arithmetic_is_medium_risk(self):
        f = self.good()
        f["credit_for_98_6"]["value"] = 1240
        self.assertEqual(vo.risk_tier(vo.verify(f, DOC))[0], "MEDIUM")

    def test_missing_item_fails(self):
        f = self.good()
        del f["monthly_fee"]
        self.assertFalse(vo.verify(f, DOC)[0]["passed"])

    # ---- Day 2 Part D: late-payment interest (clause 4.2) and the stricter evidence checks ----
    def by_item(self, findings):
        return {c["item"]: c for c in vo.verify(findings, DOC)}

    def test_late_interest_correct_is_low_risk(self):
        row = self.by_item(self.good())["late_interest_pct_month"]
        self.assertEqual((row["expected"], row["passed"]), (1.5, True))
        self.assertEqual(vo.risk_tier(vo.verify(self.good(), DOC))[0], "LOW")

    def test_late_interest_invented_quote_is_high_risk(self):
        f = self.good()
        f["late_interest_pct_month"] = {"value": 1.5, "quote": "overdue invoices carry interest of 1.5% per month"}
        self.assertFalse(self.by_item(f)["late_interest_pct_month"]["quote_exists"])
        self.assertEqual(vo.risk_tier(vo.verify(f, DOC))[0], "HIGH")

    def test_late_interest_wrong_value_is_high_risk(self):
        f = self.good()
        f["late_interest_pct_month"]["value"] = 2   # the real quote, but the number does not appear in it
        self.assertFalse(self.by_item(f)["late_interest_pct_month"]["number_in_quote"])
        self.assertEqual(vo.risk_tier(vo.verify(f, DOC))[0], "HIGH")

    def test_decimal_is_never_looked_for_as_a_rounded_whole_number(self):
        self.assertNotIn("2", vo._number_variants(1.5))
        self.assertIn("12,400", vo._number_variants(12400))

    def test_number_inside_another_number_does_not_count(self):
        self.assertFalse(vo._number_appears(5, "interest at 1.5% per month"))
        self.assertTrue(vo._number_appears(5, "credit 5% of that month's fee"))
        self.assertFalse(vo._number_appears(20, "a fixed monthly fee of 12,400.00"))

    def test_real_quote_from_the_wrong_clause_is_high_risk(self):
        f = self.good()
        f["credit_percent_per_step"]["quote"] = "interest at 1.5% per month on the overdue amount"   # clause 4.2, not 7.1
        row = self.by_item(f)["credit_percent_per_step"]
        self.assertEqual((row["quote_exists"], row["right_clause"]), (True, False))
        self.assertEqual(vo.risk_tier(vo.verify(f, DOC))[0], "HIGH")

    def test_unsupported_number_raises_the_tier(self):
        # Before the fix: a real quote that does not contain the number still came out LOW.
        f = self.good()
        f["credit_cap_percent"]["quote"] = "up to a maximum credit of 20% of the monthly fee"
        f["monthly_fee"]["quote"] = "invoiced on the first business day of each month"   # real 4.1 text, no 12,400
        self.assertEqual(vo.risk_tier(vo.verify(f, DOC))[0], "HIGH")

    def test_clauses_are_split_by_number(self):
        clauses = vo.split_clauses(DOC)
        self.assertEqual(list(clauses), ["4.1", "4.2", "7.1", "9.2", "11.4"])
        self.assertIn("1.5% per month", clauses["4.2"])


class Embeddings(unittest.TestCase):
    def test_toy_vectors_are_unit_length(self):
        m = emb.toy_embed(["refund my money", "reset my password"])
        np.testing.assert_allclose(np.linalg.norm(m, axis=1), 1.0)

    def test_synonym_query_finds_right_topic_with_no_shared_words(self):
        import json as j
        rows = j.loads((emb.DATA_DIR / "sentences.json").read_text(encoding="utf-8"))
        m = emb.toy_embed([r["text"] for r in rows])
        for query, topic in [("I can't sign into my profile", "it_access"),
                             ("How much vacation am I entitled to?", "hr_leave")]:
            top = emb.cosine_top_k(emb.toy_embed([query])[0], m, k=1)[0][0]
            self.assertEqual(rows[top]["topic"], topic, query)
        # Day 2 Part C: since the facilities topic was added, "faulty lock" (damage word group) puts a
        # facilities sentence first for this refund query. Refunds must still be in the top 2.
        top2 = [rows[i]["topic"] for i, _ in emb.cosine_top_k(emb.toy_embed(["Reimburse me for the defective goods"])[0], m, k=2)]
        self.assertIn("refunds", top2)

    def test_facilities_topic_added(self):
        import json as j
        rows = j.loads((emb.DATA_DIR / "sentences.json").read_text(encoding="utf-8"))
        self.assertEqual(sum(r["topic"] == "facilities" for r in rows), 8)

    def test_toy_embedder_sends_a_room_booking_to_leave(self):
        """Documents a known toy-embedder failure: "book" is in the leave word group, so a room booking
        (facilities) lands on hr_leave. A real model should not make this mistake."""
        import json as j
        rows = j.loads((emb.DATA_DIR / "sentences.json").read_text(encoding="utf-8"))
        m = emb.toy_embed([r["text"] for r in rows])
        top = emb.cosine_top_k(emb.toy_embed(["Book a room for the team workshop"])[0], m, k=1)[0][0]
        self.assertEqual(rows[top]["topic"], "hr_leave")

    def test_facilities_synonym_query_with_real_model(self):
        """The real check for the new topic: no shared content words, so only meaning can match it."""
        try:
            import fastembed  # noqa: F401
        except ImportError as exc:   # includes "DLL load failed" when the onnxruntime runtime is missing
            self.skipTest(f"fastembed not usable on this machine: {exc}")
        import json as j
        rows = j.loads((emb.DATA_DIR / "sentences.json").read_text(encoding="utf-8"))
        m = emb.real_embed([r["text"] for r in rows])
        top = emb.cosine_top_k(emb.real_embed(["Book a room for the team workshop"])[0], m, k=1)[0][0]
        self.assertEqual(rows[top]["topic"], "facilities")

    def test_keyword_overlap(self):
        self.assertEqual(emb.keyword_overlap("my money back", "money for you"), 1)


class Redaction(unittest.TestCase):
    def test_patterns(self):
        clean, found = redact_pii.redact("a@b.com +44 7700 900123 4111 1111 1111 1111 ORD-1001 1990-04-12")
        self.assertEqual(found, {"EMAIL": 1, "CARD": 1, "DOB": 1, "PHONE": 1, "ORDER_ID": 1})
        self.assertNotIn("@", clean)

    def test_money_amounts_survive(self):
        clean, _ = redact_pii.redact("fee of 12,400.00 and 5% credit")
        self.assertIn("12,400.00", clean)


class CliWrapper(unittest.TestCase):
    def fake_run(self, stdout="", returncode=0, stderr=""):
        return mock.patch.object(cli.subprocess, "run",
                                 return_value=SimpleNamespace(stdout=stdout, stderr=stderr, returncode=returncode))

    def test_command_flags(self):
        cmd = cli.build_command("claude", "haiku")
        self.assertEqual(cmd[:4], ["claude", "-p", "--model", "haiku"])
        self.assertIn("--tools", cmd)
        self.assertEqual(cmd[cmd.index("--tools") + 1], "")

    def test_parses_json_reply(self):
        reply = json.dumps({"result": "620 and 24,800", "duration_ms": 2500, "total_cost_usd": 0.01,
                            "usage": {"input_tokens": 3, "output_tokens": 9}, "modelUsage": {"claude-haiku-5-5": {}}})
        with mock.patch.object(cli.shutil, "which", return_value="/bin/claude"), self.fake_run(reply):
            r = cli.run_cli("prompt", "haiku", 10)
        self.assertTrue(r["ok"])
        self.assertEqual((r["seconds"], r["served_by"]), (2.5, "claude-haiku-5-5"))

    def test_api_key_is_passed_via_environment_not_arguments(self):
        with mock.patch.object(cli.shutil, "which", return_value="/bin/claude"), \
             mock.patch.object(cli.config, "get_api_key", return_value="sk-ant-secret"), \
             self.fake_run(json.dumps({"result": "x"})) as run:
            cli.run_cli("prompt", "sonnet", 10)
        kwargs = run.call_args.kwargs
        self.assertEqual(kwargs["env"]["ANTHROPIC_API_KEY"], "sk-ant-secret")
        self.assertNotIn("sk-ant-secret", " ".join(run.call_args.args[0]))
        self.assertEqual(kwargs["input"], "prompt")

    def test_failures_are_reported_not_raised(self):
        with mock.patch.object(cli.shutil, "which", return_value=None):
            self.assertFalse(cli.run_cli("p", "haiku", 5)["ok"])
        with mock.patch.object(cli.shutil, "which", return_value="/bin/claude"), self.fake_run("", 1, "auth error"):
            self.assertIn("auth error", cli.run_cli("p", "haiku", 5)["error"])
        with mock.patch.object(cli.shutil, "which", return_value="/bin/claude"), self.fake_run("not json"):
            self.assertIn("JSON", cli.run_cli("p", "haiku", 5)["error"])
        with mock.patch.object(cli.shutil, "which", return_value="/bin/claude"), \
             mock.patch.object(cli.subprocess, "run", side_effect=subprocess.TimeoutExpired("claude", 5)):
            self.assertIn("timed out", cli.run_cli("p", "haiku", 5)["error"])

    def test_auto_check_and_query_loading(self):
        self.assertEqual(cli.auto_check("620 and 24,800", ["620", "24,800"]), "2/2 key numbers")
        q = cli.load_query("Q1")
        self.assertIn("SERVICES AGREEMENT", q["prompt"])
        self.assertNotIn("{document}", q["prompt"])


class RepoHygiene(unittest.TestCase):
    def test_env_example_has_only_placeholder_key(self):
        text = (config.REPO_ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("ANTHROPIC_API_KEY=sk-ant-your-key-here", text)

    def test_gitignore_excludes_env(self):
        self.assertIn(".env", (config.REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    unittest.main()
