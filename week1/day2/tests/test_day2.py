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


class Embeddings(unittest.TestCase):
    def test_toy_vectors_are_unit_length(self):
        m = emb.toy_embed(["refund my money", "reset my password"])
        np.testing.assert_allclose(np.linalg.norm(m, axis=1), 1.0)

    def test_synonym_query_finds_right_topic_with_no_shared_words(self):
        import json as j
        rows = j.loads((emb.DATA_DIR / "sentences.json").read_text(encoding="utf-8"))
        m = emb.toy_embed([r["text"] for r in rows])
        for query, topic in [("Reimburse me for the defective goods", "refunds"),
                             ("I can't sign into my profile", "it_access"),
                             ("How much vacation am I entitled to?", "hr_leave")]:
            top = emb.cosine_top_k(emb.toy_embed([query])[0], m, k=1)[0][0]
            self.assertEqual(rows[top]["topic"], topic, query)

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
