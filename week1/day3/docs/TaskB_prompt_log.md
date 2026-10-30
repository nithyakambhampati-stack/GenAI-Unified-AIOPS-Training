# Task B - prompt log

I used Claude Code in VS Code, working in this folder. I ran and checked everything before keeping it.

1. Prompt 1: write `dot`, `norm`, `cosine_similarity` and `euclidean_distance` using only the standard library, with
   a comment above each line, a ValueError for zero vectors and for different lengths, and without looking at
   `vector_math.py`.
   It wrote the four functions plus a small `_check_same_length()` helper. Nothing was wrong. `norm` only takes one
   vector, so the "different lengths" rule doesn't apply to it, which is fine. I ran `step3_check_my_code.py` and got
   4/4. I also checked it against my paper working (dot 24, lengths 5 and 5, cosine 0.96), and the numbers matched.

2. Prompt 2: walk me through `cosine_similarity([3, 4], [4, 3])` line by line.
   Length check, norms 5 and 5, zero check, dot 24, 24 / 25 = 0.96. That matched what I had on paper.

3. Prompt 5: add `nearest(query, candidates, metric="cosine")`.
   The first version used two `sorted()` calls, one descending for cosine and one ascending for distance. I found
   three problems with it (`outputs/taskB_nearest_v1_issues.txt`):
   - With tied scores the order depended on the dict, so the same data in a different order gave a different answer.
   - A zero-vector candidate crashed the whole ranking, and the error didn't say which candidate it was.
   - A bad metric with an empty candidate list was only caught because of the order of the `if` statements.
   I asked for a second version: break ties by name, check the metric first, name the bad candidate in the error, and
   round scores to 12 decimal places so floating-point noise doesn't break a real tie.

4. Prompt 4: write unittest tests in `test_mine.py` and run them.
   It started with 5 tests. The problem was that the `nearest` test used candidates where both metrics agree, so it
   would still pass if someone mixed up "higher is better" and "lower is better". I changed it so one candidate is
   far away but pointing the same way, and the other is close but at an angle, which makes cosine and distance give
   opposite answers. I also added tests for ties (both dict orders), empty candidates, the zero-vector error, a bad
   metric, wrong lengths, `centroid()`, and my Task A numbers.

5. Stretch: add `centroid(vectors)`.
   It averages each position and raises ValueError for an empty list or mixed lengths. I kept it as is and used it in
   `day3_extras.py`.

End result: `python -m unittest test_mine -v` gives 14 OK, and `step3_check_my_code.py` is still 4/4.

What I learnt: the first version worked fine on normal input. The problems only showed up with things you don't
think to try in a demo, like ties, an empty list or a zero vector. And a test is only worth having if it can
actually fail.
