# Task B - prompt log (Claude Code)

Tool: Claude Code in VS Code, working in this folder. Every result was run and checked before it was accepted.

| # | Prompt (short form) | What Claude Code produced | What was wrong or missing | What I did |
|---|---|---|---|---|
| 1 | Prompt 1: implement `dot`, `norm`, `cosine_similarity`, `euclidean_distance`; standard library only; comment above each line; `ValueError` for a zero vector and for different lengths; do not open `vector_math.py` | The four functions plus a small `_check_same_length()` helper used by the three two-vector functions | Nothing wrong. `norm` takes one vector, so the "different lengths" rule cannot apply to it - noted rather than forced | Ran `step3_check_my_code.py`: 4/4 PASS. Compared with my hand working (dot 24, lengths 5 and 5, cosine 0.96): same numbers |
| 2 | Prompt 2: walk through `cosine_similarity([3, 4], [4, 3])` line by line | Length check, norms 5 and 5, zero check, dot 24, 24 / 25 = 0.96 | Nothing | Matched my paper working |
| 3 | Prompt 5: add `nearest(query, candidates, metric="cosine")` | Version 1: two `sorted()` calls, `reverse=True` for cosine, ascending for euclidean, `ValueError` for an unknown metric | (a) **Ties**: equal scores came back in whatever order the dict happened to have, so the same data in a different order gave a different answer (`outputs/taskB_nearest_v1_issues.txt`). (b) **Zero-vector candidate**: the whole ranking crashed with "undefined for a zero vector" without saying *which* candidate was the problem. (c) An unknown metric with an empty candidate list was only caught because of the order of the `if`s - fragile | Asked for version 2: tie-break by name, check the metric first, name the bad candidate in every error, round scores to 12 decimals so floating-point noise does not break a real tie |
| 4 | Prompt 4: write unittest tests, put them in `test_mine.py`, run them | First set: 5 tests (worked example, zero vector, different lengths, negatives, direction vs length) | The first `nearest` test used candidates where both metrics agree on the order, so it **could not fail** if someone swapped "higher is better" and "lower is better" | Rewrote it with one candidate that is far away but in the same direction and one that is close but angled, so cosine and distance give **opposite** orders. Added tests for ties (both dict orders), empty candidates, the named zero-vector error, a bad metric, a bad length, and `centroid()`. Added my Task A numbers as a test |
| 5 | Stretch: add `centroid(vectors)` | Average of each position, `ValueError` for an empty list or mixed lengths | Nothing | Accepted; used in `day3_extras.py` |

**Final state:** `python -m unittest test_mine -v` → 14 tests OK (`outputs/taskB_test_mine.txt`);
`python step3_check_my_code.py` → still 4/4 PASS (`outputs/step3_check_my_code.txt`).

**What I learnt:** the first version "worked" on the happy path. The problems only showed up with inputs nobody
writes by accident in a demo: ties, an empty form, a blank vector. A test only counts if it can fail.
