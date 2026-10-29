"""
scenario_matrix.py  -  compare every item with every other item in YOUR own mini scenario
=========================================================================================
Used in the unguided session. You describe 5-8 items with a few numbers each (in a small JSON file), and this
script prints a table of cosine similarities and distances, and names the most and least similar pairs.

    python scenario_matrix.py data/my_scenario_template.json      # the example file
    python scenario_matrix.py data/my_scenario.json               # your own file (copy the template and edit)

File format (see data/my_scenario_template.json):
    {"dimensions": ["name of number 1", "name of number 2", ...],
     "items": {"short item name": [numbers...], ...}}
Every item must have exactly as many numbers as there are dimensions. Use whole numbers 0-5 so the arithmetic stays easy.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import vector_math as vm


def load(path: str) -> tuple[list[str], dict[str, list[float]]]:
    """Read and validate a scenario file. Gives friendly errors for the usual mistakes."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    dims, items = data["dimensions"], data["items"]
    for name, vec in items.items():
        if len(vec) != len(dims):
            sys.exit(f"'{name}' has {len(vec)} numbers but there are {len(dims)} dimensions")
        if all(v == 0 for v in vec):
            sys.exit(f"'{name}' is all zeros: it has no direction, so cosine similarity is undefined")
    return dims, items


def print_matrix(title: str, names: list[str], func, fmt: str) -> None:
    """Print a square table: row item against column item."""
    print(f"\n{title}")
    width = max(len(n) for n in names) + 2
    print(" " * width + "".join(f"{i + 1:>7}" for i in range(len(names))))
    for i, a in enumerate(names):
        row = "".join(fmt.format(func(a, b)) for b in names)
        print(f"{str(i + 1) + '. ' + a:<{width}}{row}")


def main(argv: list[str]) -> None:
    if len(argv) != 1:
        sys.exit("Usage: python scenario_matrix.py <scenario.json>")
    dims, items = load(argv[0])
    names = list(items)
    print(f"Dimensions: {dims}")
    print_matrix("COSINE SIMILARITY (1 = same direction)", names,
                 lambda a, b: vm.cosine_similarity(items[a], items[b]), "{:>7.2f}")
    print_matrix("EUCLIDEAN DISTANCE (0 = identical)", names,
                 lambda a, b: vm.euclidean_distance(items[a], items[b]), "{:>7.2f}")
    pairs = [(vm.cosine_similarity(items[a], items[b]), a, b) for a, b in itertools.combinations(names, 2)]
    pairs.sort(reverse=True)
    print(f"\nMost similar pair  : {pairs[0][1]}  <->  {pairs[0][2]}   (cosine {pairs[0][0]:.2f})")
    print(f"Least similar pair : {pairs[-1][1]}  <->  {pairs[-1][2]}   (cosine {pairs[-1][0]:.2f})")
    print("Was this what you predicted? If not, which of your numbers surprised you?")


if __name__ == "__main__":
    main(sys.argv[1:])
