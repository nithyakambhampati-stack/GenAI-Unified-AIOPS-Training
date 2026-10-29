"""
step1_by_hand_check.py  -  do the maths on PAPER first, then type your answers here to check them
=================================================================================================
How to use it
-------------
1. Run:   python step1_by_hand_check.py
2. For each exercise it shows two vectors. Work out, on paper (a calculator is fine):
       the dot product,  the cosine similarity,  and the Euclidean distance.
3. Type each answer when asked (press Enter to skip one). Rounding to 2 decimals is fine.
4. You get instant feedback, and a hint if you are off.

Stuck?  python step1_by_hand_check.py --show      prints all the answers with the working
"""
from __future__ import annotations

import argparse

import vector_math as vm

TOLERANCE = 0.01   # answers within 0.01 of the true value count as correct


def exercises() -> list[tuple[str, list[float], list[float]]]:
    """Four exercises: two easy 2-D warm-ups, then two real 4-D word pairs from data/vectors.json."""
    words = vm.load_data()["words"]
    return [
        ("E1  (2-D warm-up)", [3, 4], [4, 3]),
        ("E2  (same direction, different length)", [3, 4], [6, 8]),
        ("E3  loan vs mortgage (4-D)", words["loan"], words["mortgage"]),
        ("E4  loan vs fraud (4-D)", words["loan"], words["fraud"]),
    ]


def ask_number(prompt: str) -> float | None:
    """Read a number from the keyboard. Returns None if the person just presses Enter (skip)."""
    while True:
        text = input(prompt).strip()
        if text == "":
            return None
        try:
            return float(text)
        except ValueError:
            print("   Please type a number such as 0.96 (or press Enter to skip).")


def grade(label: str, typed: float | None, truth: float, hint: str) -> bool:
    """Compare one typed answer with the true value and print feedback."""
    if typed is None:
        print(f"   {label}: skipped (answer: {truth:.4f})")
        return False
    if abs(typed - truth) <= TOLERANCE:
        print(f"   {label}: correct")
        return True
    print(f"   {label}: not quite (you typed {typed:g}). Hint: {hint}")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Check your hand calculations")
    parser.add_argument("--show", action="store_true", help="print all answers with the working")
    args = parser.parse_args()

    if args.show:
        for title, a, b in exercises():
            print("\n" + "=" * 60 + f"\n{title}")
            vm.explain("A", a, "B", b)
        return

    correct = total = 0
    for title, a, b in exercises():
        print("\n" + "=" * 60 + f"\n{title}\n   A = {a}\n   B = {b}")
        checks = [
            ("dot product", vm.dot(a, b), "multiply the matching numbers, then add: a1*b1 + a2*b2 + ..."),
            ("cosine similarity", vm.cosine_similarity(a, b), "dot / (length of A x length of B). Did you take the square roots?"),
            ("Euclidean distance", vm.euclidean_distance(a, b), "subtract matching numbers, square, add, then take ONE square root at the end"),
        ]
        for label, truth, hint in checks:
            typed = ask_number(f"   Your {label}: ")
            correct += grade(label, typed, truth, hint)
            total += 1
    print("\n" + "=" * 60 + f"\nScore: {correct}/{total} correct")
    print("Next: Claude Code writes the same functions in Python (step 2), and you check its work (step 3).")


if __name__ == "__main__":
    main()
