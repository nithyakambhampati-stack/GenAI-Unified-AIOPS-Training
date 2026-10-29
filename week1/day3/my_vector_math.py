"""
my_vector_math.py  -  YOUR file. Claude Code will write these four functions; YOU will check them.
=================================================================================================
Step 2 of the lab: ask Claude Code to fill in the four functions below. Good prompts are in
CLAUDE_CODE_PROMPTS.md. Rules:

  * Use only Python's standard library (the `math` module is fine). No numpy here - the point is to see the maths.
  * Add a short comment above each line of working so you can explain it.
  * Do NOT copy from vector_math.py - that is the answer key used by the checker.

When you think it is done, run:   python step3_check_my_code.py
"""
from __future__ import annotations

import math


def _check_same_length(a: list[float], b: list[float]) -> None:
    """Raise ValueError if the two vectors have different lengths."""
    # Pairing numbers position by position only makes sense when both vectors have the same length
    if len(a) != len(b):
        raise ValueError(f"vectors have different lengths: {len(a)} and {len(b)}")


def dot(a: list[float], b: list[float]) -> float:
    """Return the dot product of two equal-length vectors."""
    # Refuse vectors of different lengths
    _check_same_length(a, b)
    # Multiply each pair of matching numbers and add up all the products
    return sum(x * y for x, y in zip(a, b))


def norm(a: list[float]) -> float:
    """Return the length (magnitude) of a vector."""
    # Square every number, add them up, take the square root (Pythagoras in n dimensions)
    return math.sqrt(sum(x * x for x in a))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Return cosine similarity. Raise ValueError for a zero vector or different lengths."""
    # Refuse vectors of different lengths
    _check_same_length(a, b)
    # Work out the length of each vector
    length_a = norm(a)
    length_b = norm(b)
    # A zero vector has no direction, so the angle (and the cosine) is undefined
    if length_a == 0 or length_b == 0:
        raise ValueError("cosine similarity is undefined for a zero vector")
    # Divide the dot product by both lengths, so only the direction counts
    return dot(a, b) / (length_a * length_b)


def euclidean_distance(a: list[float], b: list[float]) -> float:
    """Return straight-line distance. Raise ValueError for different lengths."""
    # Refuse vectors of different lengths
    _check_same_length(a, b)
    # Square the gap in each position, add them up, take the square root
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def nearest(query: list[float], candidates: dict[str, list[float]], metric: str = "cosine") -> list[str]:
    """Return candidate names sorted from most to least similar to the query.

    cosine: higher is better. euclidean: lower is better. Ties are broken by name (A-Z) so the
    order never depends on the order of the dict. An empty dict gives an empty list.
    """
    # Check the metric first, so a typo fails even when there are no candidates
    if metric not in ("cosine", "euclidean"):
        raise ValueError(f"unknown metric {metric!r}: use 'cosine' or 'euclidean'")
    # A zero query has no direction, so no candidate can be ranked against it by cosine
    if metric == "cosine" and norm(query) == 0:
        raise ValueError("query is a zero vector: cosine similarity is undefined")
    scored = []
    for name, vector in candidates.items():
        # Name the bad candidate in the error, so the caller knows which row to fix
        if len(vector) != len(query):
            raise ValueError(f"candidate {name!r} has {len(vector)} numbers, query has {len(query)}")
        if metric == "cosine" and norm(vector) == 0:
            raise ValueError(f"candidate {name!r} is a zero vector: cosine similarity is undefined")
        # Turn every score into "smaller is better": negate cosine, keep distance as it is
        if metric == "cosine":
            sort_key = -cosine_similarity(query, vector)
        else:
            sort_key = euclidean_distance(query, vector)
        # Round away floating-point noise so equal scores really count as ties
        scored.append((round(sort_key, 12), name))
    # Sort by score first, then by name to break ties the same way every time
    return [name for _, name in sorted(scored)]


def centroid(vectors: list[list[float]]) -> list[float]:
    """Return the average vector (the 'centre') of a group of equal-length vectors."""
    # An average of nothing is undefined
    if not vectors:
        raise ValueError("centroid needs at least one vector")
    # Every vector must have the same length as the first one
    for v in vectors:
        _check_same_length(vectors[0], v)
    # Average each position across all the vectors
    return [sum(column) / len(vectors) for column in zip(*vectors)]
