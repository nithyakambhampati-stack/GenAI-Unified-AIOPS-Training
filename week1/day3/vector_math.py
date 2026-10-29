"""
vector_math.py  -  the reference implementation (written from scratch, standard library only)
==============================================================================================
Four small functions are the whole "mathematics of closeness" behind embeddings and semantic search:

    dot(a, b)                 multiply matching numbers, then add them up
    norm(a)                   the length of a vector (Pythagoras in many dimensions)
    cosine_similarity(a, b)   do the two vectors point the SAME WAY?   (-1 .. 1, higher = more similar)
    euclidean_distance(a, b)  how FAR APART are the two end points?    (0 .. infinity, lower = more similar)

Run it on any two words from data/vectors.json and it prints every step so you can check your hand work:

    python vector_math.py loan mortgage
    python vector_math.py loan fraud
    python vector_math.py --list
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "vectors.json"


def _check_same_length(a: list[float], b: list[float]) -> None:
    """Vectors can only be compared if they have the same number of dimensions."""
    if len(a) != len(b):
        raise ValueError(f"Vectors must have the same length (got {len(a)} and {len(b)})")


def dot(a: list[float], b: list[float]) -> float:
    """Dot product: a1*b1 + a2*b2 + ... Example: (3,4)·(4,3) = 12 + 12 = 24."""
    _check_same_length(a, b)
    return sum(x * y for x, y in zip(a, b))


def norm(a: list[float]) -> float:
    """Length of a vector: square root of (a1^2 + a2^2 + ...). Example: |(3,4)| = sqrt(9+16) = 5."""
    return math.sqrt(sum(x * x for x in a))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    cos(angle between a and b) = (a . b) / (|a| x |b|)
    1.0  = same direction (very similar)      0.0 = at right angles (unrelated)      -1.0 = opposite
    A vector of all zeros has no direction, so the answer is undefined -> we raise an error instead of guessing.
    """
    _check_same_length(a, b)
    length_a, length_b = norm(a), norm(b)
    if length_a == 0 or length_b == 0:
        raise ValueError("Cosine similarity is undefined for a zero vector (it has no direction)")
    return dot(a, b) / (length_a * length_b)


def euclidean_distance(a: list[float], b: list[float]) -> float:
    """Straight-line distance: sqrt((a1-b1)^2 + (a2-b2)^2 + ...). Example: (3,4) to (4,3) = sqrt(1+1) = 1.414."""
    _check_same_length(a, b)
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def load_data() -> dict:
    """Read the toy vectors file."""
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def explain(name_a: str, a: list[float], name_b: str, b: list[float]) -> None:
    """Print every intermediate number, in the order you would write them on paper."""
    print(f"\nA = {name_a} = {a}\nB = {name_b} = {b}\n")
    products = [f"{x}x{y}" for x, y in zip(a, b)]
    print(f"1. Dot product      A.B   = {' + '.join(products)} = {dot(a, b):g}")
    print(f"2. Length of A      |A|   = sqrt({' + '.join(f'{x}^2' for x in a)}) = sqrt({sum(x * x for x in a):g}) = {norm(a):.4f}")
    print(f"3. Length of B      |B|   = sqrt({' + '.join(f'{y}^2' for y in b)}) = sqrt({sum(y * y for y in b):g}) = {norm(b):.4f}")
    print(f"4. Cosine similarity      = A.B / (|A| x |B|) = {dot(a, b):g} / ({norm(a):.4f} x {norm(b):.4f}) = {cosine_similarity(a, b):.4f}")
    diffs = [f"({x}-{y})^2" for x, y in zip(a, b)]
    print(f"5. Euclidean distance     = sqrt({' + '.join(diffs)}) = sqrt({sum((x - y) ** 2 for x, y in zip(a, b)):g}) = {euclidean_distance(a, b):.4f}")


def main(argv: list[str]) -> None:
    data = load_data()
    words = data["words"]
    if not argv or argv[0] == "--list":
        print("Words available:", ", ".join(words))
        print("Usage: python vector_math.py <word1> <word2>")
        return
    if len(argv) != 2 or argv[0] not in words or argv[1] not in words:
        sys.exit("Please give two words from the list (see: python vector_math.py --list)")
    print(f"Dimensions: {data['dimensions']}")
    explain(argv[0], words[argv[0]], argv[1], words[argv[1]])


if __name__ == "__main__":
    main(sys.argv[1:])
