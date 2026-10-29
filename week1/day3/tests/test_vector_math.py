"""Unit tests for the lab. Run from the repo root:  python -m unittest discover -s tests"""
import math
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # make vector_math importable

import my_vector_math
import step1_by_hand_check as step1
import scenario_matrix
import step3_check_my_code as step3
import vector_math as vm


class ReferenceMaths(unittest.TestCase):
    def test_worked_examples(self):
        self.assertEqual(vm.dot([3, 4], [4, 3]), 24)
        self.assertEqual(vm.norm([3, 4]), 5)
        self.assertAlmostEqual(vm.cosine_similarity([3, 4], [4, 3]), 0.96)
        self.assertAlmostEqual(vm.euclidean_distance([3, 4], [4, 3]), math.sqrt(2))

    def test_same_direction_different_length(self):
        self.assertAlmostEqual(vm.cosine_similarity([3, 4], [6, 8]), 1.0)
        self.assertAlmostEqual(vm.euclidean_distance([3, 4], [6, 8]), 5.0)

    def test_opposite_and_orthogonal(self):
        self.assertAlmostEqual(vm.cosine_similarity([1, 2], [-1, -2]), -1.0)
        self.assertAlmostEqual(vm.cosine_similarity([1, 0], [0, 1]), 0.0)

    def test_loan_mortgage(self):
        w = vm.load_data()["words"]
        self.assertAlmostEqual(vm.cosine_similarity(w["loan"], w["mortgage"]), math.sqrt(34) / 6)

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            vm.cosine_similarity([0, 0], [1, 2])
        with self.assertRaises(ValueError):
            vm.dot([1], [1, 2])
        with self.assertRaises(ValueError):
            vm.euclidean_distance([1], [1, 2])

    def test_unit_vector_identity(self):
        a, b = [5, 1, 2, 2], [5, 1, 3, 1]
        ua, ub = [x / vm.norm(a) for x in a], [x / vm.norm(b) for x in b]
        self.assertAlmostEqual(vm.euclidean_distance(ua, ub) ** 2, 2 - 2 * vm.cosine_similarity(a, b))

    def test_data_file_is_consistent(self):
        d = vm.load_data()
        n = len(d["dimensions"])
        for group in ("words", "sentences", "queries"):
            for name, vec in d[group].items():
                self.assertEqual(len(vec), n, name)

    def test_experiment_2_has_a_disagreement(self):
        d = vm.load_data()
        q = d["queries"]["Question about our loans and customer service"]
        s = d["sentences"]
        best_cos = max(s, key=lambda k: vm.cosine_similarity(q, s[k]))
        best_euc = min(s, key=lambda k: vm.euclidean_distance(q, s[k]))
        self.assertNotEqual(best_cos, best_euc)


class Checker(unittest.TestCase):
    def test_stub_reports_todo(self):
        self.assertTrue(step3.check("dot").startswith("TODO"))

    def test_correct_implementation_passes(self):
        with mock.patch.multiple(my_vector_math, dot=vm.dot, norm=vm.norm,
                                 cosine_similarity=vm.cosine_similarity, euclidean_distance=vm.euclidean_distance):
            for name in ("dot", "norm", "cosine_similarity", "euclidean_distance"):
                self.assertEqual(step3.check(name), "PASS", name)

    def test_common_bug_is_caught(self):
        def forgot_sqrt(a, b):            # classic mistake: no square root in the distance
            return sum((x - y) ** 2 for x, y in zip(a, b))
        with mock.patch.object(my_vector_math, "euclidean_distance", forgot_sqrt):
            self.assertTrue(step3.check("euclidean_distance").startswith("FAIL"))

    def test_missing_zero_vector_guard_is_caught(self):
        def no_guard(a, b):
            return vm.dot(a, b) / (vm.norm(a) * vm.norm(b) or 1)
        with mock.patch.object(my_vector_math, "cosine_similarity", no_guard):
            self.assertTrue(step3.check("cosine_similarity").startswith("FAIL"))


class HandCheck(unittest.TestCase):
    def test_grading(self):
        self.assertTrue(step1.grade("x", 0.96, 0.96, "h"))
        self.assertTrue(step1.grade("x", 0.955, 0.96, "h"))      # within tolerance
        self.assertFalse(step1.grade("x", 0.5, 0.96, "h"))
        self.assertFalse(step1.grade("x", None, 0.96, "h"))

    def test_four_exercises(self):
        self.assertEqual(len(step1.exercises()), 4)


class ScenarioFile(unittest.TestCase):
    def test_template_loads_and_is_valid(self):
        dims, items = scenario_matrix.load(str(Path(__file__).resolve().parents[1] / "data" / "my_scenario_template.json"))
        self.assertEqual(len(dims), 4)
        self.assertGreaterEqual(len(items), 5)

    def test_zero_vector_is_rejected(self):
        import json, tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump({"dimensions": ["a", "b"], "items": {"x": [0, 0]}}, fh)
        with self.assertRaises(SystemExit):
            scenario_matrix.load(fh.name)


if __name__ == "__main__":
    unittest.main()
