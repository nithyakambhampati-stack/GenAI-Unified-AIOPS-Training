"""My own tests for my_vector_math.py: the four functions, nearest() and centroid().

Run:  python -m unittest test_mine -v
"""
import math
import unittest

from my_vector_math import centroid, cosine_similarity, dot, euclidean_distance, nearest, norm


class FourFunctions(unittest.TestCase):
    def test_worked_example(self):
        # The 3-4-5 example from Step 1: dot 24, lengths 5 and 5, cosine 0.96, distance sqrt(2)
        self.assertEqual(dot([3, 4], [4, 3]), 24)
        self.assertEqual(norm([3, 4]), 5)
        self.assertAlmostEqual(cosine_similarity([3, 4], [4, 3]), 0.96)
        self.assertAlmostEqual(euclidean_distance([3, 4], [4, 3]), math.sqrt(2))

    def test_task_a_pairs(self):
        # My hand-calculated Task A answers, kept here so the code is checked against my working
        overdraft, chargeback = [4, 2, 1, 3], [1, 4, 1, 3]
        self.assertEqual(dot(overdraft, chargeback), 22)
        self.assertAlmostEqual(cosine_similarity(overdraft, chargeback), 0.773, places=3)
        self.assertAlmostEqual(euclidean_distance(overdraft, chargeback), 3.606, places=3)

    def test_zero_vector(self):
        # A zero vector has length 0 and no direction, so cosine must refuse it (either side)
        self.assertEqual(norm([0, 0, 0]), 0)
        with self.assertRaises(ValueError):
            cosine_similarity([0, 0], [1, 2])
        with self.assertRaises(ValueError):
            cosine_similarity([1, 2], [0, 0])

    def test_different_lengths(self):
        # Every two-vector function must refuse mismatched lengths
        for func in (dot, cosine_similarity, euclidean_distance):
            with self.subTest(func=func.__name__):
                with self.assertRaises(ValueError):
                    func([1, 2, 3], [1, 2])

    def test_negative_numbers(self):
        # Opposite directions give cosine -1; negatives must square correctly
        self.assertEqual(dot([-1, 2], [3, -4]), -11)
        self.assertEqual(norm([-3, -4]), 5)
        self.assertAlmostEqual(cosine_similarity([1, 2], [-1, -2]), -1.0)
        self.assertEqual(euclidean_distance([-1, -1], [2, 3]), 5)


class Nearest(unittest.TestCase):
    # One candidate points the same way as the query but is far away; the other is close but at an angle.
    # The two metrics must rank them in OPPOSITE orders - so a test that swapped "higher/lower is better"
    # for either metric would fail here.
    QUERY = [1, 0]
    CANDIDATES = {"same_direction_far": [10, 0], "close_but_angled": [1, 1]}

    def test_cosine_higher_is_better(self):
        self.assertEqual(nearest(self.QUERY, self.CANDIDATES), ["same_direction_far", "close_but_angled"])

    def test_euclidean_lower_is_better(self):
        self.assertEqual(nearest(self.QUERY, self.CANDIDATES, metric="euclidean"),
                         ["close_but_angled", "same_direction_far"])

    def test_ties_broken_by_name_whatever_the_dict_order(self):
        # [2,0] and [3,0] both have cosine 1.0 with [1,0]: a tie. The answer must not depend on dict order.
        self.assertEqual(nearest([1, 0], {"b": [2, 0], "a": [3, 0]}), ["a", "b"])
        self.assertEqual(nearest([1, 0], {"a": [3, 0], "b": [2, 0]}), ["a", "b"])

    def test_empty_candidates(self):
        self.assertEqual(nearest([1, 2], {}), [])

    def test_zero_vector_candidate_is_named(self):
        with self.assertRaisesRegex(ValueError, "blank_form"):
            nearest([1, 0], {"ok": [1, 1], "blank_form": [0, 0]})

    def test_zero_vector_allowed_for_euclidean(self):
        # Distance is still defined for a zero vector, so it is ranked normally
        self.assertEqual(nearest([0, 0], {"far": [3, 4], "origin": [0, 0]}, metric="euclidean"), ["origin", "far"])

    def test_bad_metric_and_bad_length(self):
        with self.assertRaises(ValueError):
            nearest([1, 0], {"a": [1, 0]}, metric="manhattan")
        with self.assertRaisesRegex(ValueError, "short"):
            nearest([1, 0], {"short": [1]})


class Centroid(unittest.TestCase):
    def test_average_of_each_position(self):
        self.assertEqual(centroid([[1, 2], [3, 4], [5, 0]]), [3, 2])

    def test_empty_and_mismatched(self):
        with self.assertRaises(ValueError):
            centroid([])
        with self.assertRaises(ValueError):
            centroid([[1, 2], [1, 2, 3]])


if __name__ == "__main__":
    unittest.main()
