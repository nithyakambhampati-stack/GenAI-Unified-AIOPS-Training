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


def dot(a: list[float], b: list[float]) -> float:
    """Return the dot product of two equal-length vectors."""
    raise NotImplementedError("Ask Claude Code to write this function")


def norm(a: list[float]) -> float:
    """Return the length (magnitude) of a vector."""
    raise NotImplementedError("Ask Claude Code to write this function")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Return cosine similarity. Raise ValueError for a zero vector or different lengths."""
    raise NotImplementedError("Ask Claude Code to write this function")


def euclidean_distance(a: list[float], b: list[float]) -> float:
    """Return straight-line distance. Raise ValueError for different lengths."""
    raise NotImplementedError("Ask Claude Code to write this function")
