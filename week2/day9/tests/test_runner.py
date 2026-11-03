import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import runner  # noqa: E402


class TestRunner(unittest.TestCase):
    def test_label_never_sent(self):
        case = {"id": "X", "text": "hello", "label": {"category": "other"}}
        self.assertNotIn("label", runner.case_input("t1", case))

    def test_input_placeholder_filled(self):
        out = runner.fill("Task.\n{{INPUT}}", "t1", {"id": "X", "text": "hello"})
        self.assertIn("hello", out)
        self.assertNotIn("{{", out)

    def test_examples_placeholder_filled(self):
        out = runner.fill("{{EXAMPLES}}\n{{INPUT}}", "t1", {"id": "X", "text": "hello"})
        self.assertIn("Input:", out)

    def test_mask_long_number(self):
        self.assertEqual(runner.mask_pii("acct 123456789012"), "acct XXXXXXXX9012")

    def test_weak_prompts_receive_the_case(self):
        for name in runner.TASK_FILE.values():
            text = open(os.path.join(ROOT, "prompts", "weak", name), encoding="utf-8").read()
            self.assertIn("{{INPUT}}", text, name)


if __name__ == "__main__":
    unittest.main()
