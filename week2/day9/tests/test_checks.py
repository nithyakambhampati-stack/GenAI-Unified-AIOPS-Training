import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import checks  # noqa: E402

CFG = {"allowed_categories": ["card_fraud", "other"], "summary_fields": ["one_line_answer", "source_id"],
       "reply": {"word_limit": 50, "forbidden_phrases": ["guarantee"]}}


class TestParseJson(unittest.TestCase):
    def test_plain_json(self):
        self.assertEqual(checks.parse_json('{"a": 1}'), {"a": 1})

    def test_json_inside_text(self):
        self.assertEqual(checks.parse_json('Here you go:\n{"a": 1}\nThanks'), {"a": 1})

    def test_no_json(self):
        self.assertIsNone(checks.parse_json("category: card_fraud"))


class TestWordCount(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(checks.word_count("Dear customer, sorry."), 4)


class TestReply(unittest.TestCase):
    CASE = {"complaint_ref": "CR-1", "timeline": "within 7 working days"}

    def test_good_reply_passes(self):
        r = checks.check_reply("Dear Sir, your complaint CR-1 is resolved; the reversal is done within 7 working days.",
                               self.CASE, CFG)
        self.assertEqual(checks.score(r), 1.0)

    def test_forbidden_phrase(self):
        r = checks.check_reply("We guarantee a refund for CR-1 within 7 working days.", self.CASE, CFG)
        self.assertFalse(r["no_forbidden_phrase"])

    def test_full_card_number_detected(self):
        r = checks.check_reply("Card 4111 2222 3333 4444, CR-1, within 7 working days.", self.CASE, CFG)
        self.assertFalse(r["no_full_card_number"])


class TestSummary(unittest.TestCase):
    SNIP = {"id": "C31", "text": "Foreclosure charges are 4 percent after 12 EMIs."}

    def test_grounded(self):
        r = checks.check_summary('{"one_line_answer": "4 percent after 12 EMIs", "source_id": "C31"}', self.SNIP, CFG)
        self.assertEqual(checks.score(r), 1.0)

    def test_invented_number(self):
        r = checks.check_summary('{"one_line_answer": "5 percent", "source_id": "C31"}', self.SNIP, CFG)
        self.assertFalse(r["numbers_grounded"])


if __name__ == "__main__":
    unittest.main()
