import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import checks  # noqa: E402
import prompt_lint  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


class TestPromptLint(unittest.TestCase):
    def test_worksheet_answers(self):
        snippets = json.loads((ROOT / "by_hand" / "snippets.json").read_text(encoding="utf-8"))
        answers = json.loads((ROOT / "by_hand" / "my_answers.json").read_text(encoding="utf-8"))
        for sid, text in snippets.items():
            lint_result = prompt_lint.lint(text)
            self.assertEqual(answers[sid], {key: lint_result[key] for key in answers[sid]}, sid)

    def test_improved_prompts_have_required_strategies(self):
        expected = {
            "t1_classify.md": ("few-shot", False, False),
            "t2_reply.md": ("zero-shot", True, True),
            "t3_summary.md": ("zero-shot", False, False),
        }
        for name, strategy in expected.items():
            result = prompt_lint.lint((ROOT / "prompts" / "improved" / name).read_text(encoding="utf-8"))
            self.assertEqual(result["score"], 4, name)
            self.assertEqual((result["shots"], result["role"], result["persona"]), strategy, name)


class TestFixedChecks(unittest.TestCase):
    def test_classification_is_case_insensitive(self):
        cfg = {"allowed_categories": ["card_fraud"]}
        label = {"category": "card_fraud", "severity": "High", "escalate": True}
        result = checks.check_classification(
            '{"category": "CARD_FRAUD", "severity": "high", "escalate": true}', label, cfg
        )
        self.assertEqual(checks.score(result), 1.0)

    def test_numbers_normalize_commas_without_counting_identifiers(self):
        snippet = {"id": "C04", "text": "The fee is Rs 1,50,000 after 12 months."}
        cfg = {"summary_fields": ["one_line_answer", "source_id"]}
        result = checks.check_summary(
            '{"one_line_answer":"Rs 150000 after 12 months","source_id":"C04"}', snippet, cfg
        )
        self.assertTrue(result["numbers_grounded"])


class TestDataHygiene(unittest.TestCase):
    def test_complaint_ids_are_unique_and_categories_allowed(self):
        complaints = json.loads((ROOT / "data" / "complaints.json").read_text(encoding="utf-8"))
        config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        ids = [case["id"] for case in complaints]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({case["label"]["category"] for case in complaints} <= set(config["allowed_categories"]))

    def test_prompt_inputs_use_documented_placeholder(self):
        for name in ("t1_classify.md", "t2_reply.md", "t3_summary.md"):
            for variant in ("weak", "improved"):
                text = (ROOT / "prompts" / variant / name).read_text(encoding="utf-8")
                self.assertIn("{{INPUT}}", text, f"{variant}/{name}")
                self.assertNotIn("{{TEXT}}", text, f"{variant}/{name}")


if __name__ == "__main__":
    unittest.main()