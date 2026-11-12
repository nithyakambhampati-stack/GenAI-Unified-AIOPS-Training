import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from doc_store import load_sections, search

SECTIONS = load_sections(Path(__file__).resolve().parent.parent / "data" / "sop.txt")


class DocStoreTests(unittest.TestCase):
    def test_sections_are_split(self):
        self.assertGreaterEqual(len(SECTIONS), 10)
        self.assertEqual(SECTIONS[0]["id"], "S1.1")

    def test_best_section_for_first_question(self):
        top = search('What is the minimum amount for a part-prepayment?', SECTIONS, 3)
        self.assertEqual(top[0]["id"], 'S2.1')


if __name__ == "__main__":
    unittest.main()
