"""
step3_check_my_code.py  -  never trust code you have not tested
================================================================
Runs YOUR functions (my_vector_math.py) against the answer key (vector_math.py) on many vector pairs, including the
awkward cases: a zero vector, vectors of different lengths, negative numbers, and a vector compared with itself.

    python step3_check_my_code.py

Reading the result:
  PASS  - your function matches the answer key on every test
  FAIL  - it differs somewhere: the line shows the first failing case. Fix it (or ask Claude Code to) and run again.
  TODO  - the function has not been written yet
"""
from __future__ import annotations

import math

import my_vector_math as mine
import vector_math as key

# Test vectors: ordinary, negative, decimals, and the same direction at different scale.
PAIRS = [
    ([3, 4], [4, 3]),
    ([3, 4], [6, 8]),
    ([1, 0], [0, 1]),
    ([1, 2, 3], [-1, -2, -3]),
    ([0.5, 1.5, -2.0], [2.0, -1.0, 0.25]),
    ([5, 1, 2, 2], [5, 1, 3, 1]),
    ([2, 2], [2, 2]),
]


def close(x: float, y: float) -> bool:
    """Floating-point numbers should be compared with a small tolerance, never with ==."""
    return math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-9)


def raises_value_error(func, *args) -> bool:
    """True if calling func(*args) raises ValueError (the behaviour we require for bad input)."""
    try:
        func(*args)
    except ValueError:
        return True
    except Exception:
        return False
    return False


def check(name: str) -> str:
    """Return 'PASS', 'TODO' or a FAIL message for one function."""
    mine_f, key_f = getattr(mine, name), getattr(key, name)
    try:
        if name == "norm":
            for a, _ in PAIRS:
                if not close(mine_f(a), key_f(a)):
                    return f"FAIL  norm({a}) gave {mine_f(a)}, expected {key_f(a)}"
            return "PASS"
        for a, b in PAIRS:
            got, want = mine_f(a, b), key_f(a, b)
            if not close(got, want):
                return f"FAIL  {name}({a}, {b}) gave {got}, expected {want}"
        if not raises_value_error(mine_f, [1, 2], [1, 2, 3]):
            return "FAIL  different-length vectors should raise ValueError"
        if name == "cosine_similarity" and not raises_value_error(mine_f, [0, 0], [1, 2]):
            return "FAIL  a zero vector should raise ValueError (no direction)"
        return "PASS"
    except NotImplementedError:
        return "TODO  not written yet"
    except Exception as exc:
        return f"FAIL  crashed with {type(exc).__name__}: {exc}"


def main() -> None:
    results = {name: check(name) for name in ("dot", "norm", "cosine_similarity", "euclidean_distance")}
    print("Checking my_vector_math.py against the answer key\n")
    for name, result in results.items():
        print(f"  {name:<20}{result}")
    passed = sum(r == "PASS" for r in results.values())
    print(f"\n{passed}/4 functions pass.")
    if passed == 4:
        print("All good. Now explain to your partner, in your own words, what each function does and why.")


if __name__ == "__main__":
    main()
