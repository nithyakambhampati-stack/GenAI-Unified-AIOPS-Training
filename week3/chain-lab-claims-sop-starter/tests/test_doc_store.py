import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from doc_store import load_sections, search, split_sections

SECTIONS = load_sections(Path(__file__).resolve().parent.parent / "data" / "sop.txt")


class DocStoreTests(unittest.TestCase):
    def test_sections_are_split(self):
        self.assertGreaterEqual(len(SECTIONS), 10)
        self.assertEqual(SECTIONS[0]["id"], "S1.1")

    def test_section_ids_are_unique(self):
        ids = [s["id"] for s in SECTIONS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_title_and_text_are_separated(self):
        s21 = [s for s in SECTIONS if s["id"] == "S2.1"][0]
        self.assertEqual(s21["title"], "Pre-authorisation for planned admission")
        self.assertIn("at least 48 hours before a planned admission", s21["text"])
        self.assertNotIn("[S2.2]", s21["text"])

    def test_preamble_and_empty_text(self):
        self.assertEqual(split_sections(""), [])
        self.assertEqual(split_sections("just a title line\nno headings"), [])

    def test_best_section_for_first_question(self):
        top = search('How long before a planned admission must the hospital submit the pre-authorisation request?', SECTIONS, 3)
        self.assertEqual(top[0]["id"], 'S2.1')

    def test_search_returns_k_results(self):
        self.assertEqual(len(search("waiting period", SECTIONS, 3)), 3)

    def test_title_words_count_double(self):
        top = search("What room rent limit applies to an ICU room?", SECTIONS, 3)
        self.assertEqual(top[0]["id"], "S4.1")

    def test_other_known_questions_rank_their_section_first(self):
        cases = {"What is the waiting period for pre-existing diseases?": "S3.2",
                 "Within what time must the hospital intimate the insurer of an emergency admission?": "S2.2",
                 "Within how many working days must the insurer communicate the reasons for a rejection in writing?": "S5.1"}
        for q, sid in cases.items():
            self.assertEqual(search(q, SECTIONS, 3)[0]["id"], sid, q)


if __name__ == "__main__":
    unittest.main()
