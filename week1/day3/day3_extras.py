"""
day3_extras.py  -  Task E (a misleading high score) and the three stretch tasks, on my legacy-modernization scenario.

    python day3_extras.py

Uses only my_vector_math.py (my own functions) and data/my_scenario.json. All data is synthetic.
"""
from __future__ import annotations

import json
from pathlib import Path

from my_vector_math import centroid, cosine_similarity, euclidean_distance, norm

SCENARIO = json.loads((Path(__file__).parent / "data" / "my_scenario.json").read_text(encoding="utf-8"))
DIMS: list[str] = SCENARIO["dimensions"]
ITEMS: dict[str, list[float]] = SCENARIO["items"]


def unit(v: list[float]) -> list[float]:
    """Scale a vector to length 1 (same direction)."""
    length = norm(v)
    return [x / length for x in v]


def task_e() -> None:
    print("TASK E - two change requests that score as near-duplicates but mean the opposite")
    # Both requests talk about the same job, with the same scheduling, data and file work.
    # The only difference is the verb: retire versus keep. My four dimensions have no slot for that.
    retire = [5, 3, 2, 2]   # "Retire the COBOL batch posting job after cut-over"
    keep = [5, 3, 2, 3]     # "Keep the COBOL batch posting job running; month-end close still depends on it"
    print(f"  retire request: {retire}")
    print(f"  keep request  : {keep}")
    print(f"  cosine = {cosine_similarity(retire, keep):.3f}   distance = {euclidean_distance(retire, keep):.3f}")
    print("  A similarity search would treat these as the same request. Acting on the wrong one switches off")
    print("  a job that month-end close depends on (or leaves a retired job running and paying licence costs).\n")


def stretch_unit_identity() -> None:
    print("STRETCH 1 - on unit vectors, distance^2 = 2 - 2 x cosine")
    a_name, b_name = "COBOL batch posting job", "Monthly report extract"
    a, b = ITEMS[a_name], ITEMS[b_name]
    cos = cosine_similarity(a, b)
    d2 = euclidean_distance(unit(a), unit(b)) ** 2
    print(f"  pair: {a_name} / {b_name}")
    print(f"  cosine                       = {cos:.6f}")
    print(f"  distance^2 of unit vectors   = {d2:.6f}")
    print(f"  2 - 2 x cosine               = {2 - 2 * cos:.6f}\n")


def stretch_centroids() -> None:
    print("STRETCH 2 - centroids of two migration waves")
    waves = {
        "wave 1 (scheduler-heavy batch)": ["COBOL batch posting job", "Nightly reconciliation"],
        "wave 2 (data and file movement)": ["Informatica mapping", "Monthly report extract", "SFTP file transfer"],
    }
    centres = {}
    for label, names in waves.items():
        centres[label] = centroid([ITEMS[n] for n in names])
        print(f"  {label:<33} centre = {[round(x, 2) for x in centres[label]]}")
    w1, w2 = centres.values()
    print(f"  cosine between the two centres = {cosine_similarity(w1, w2):.3f}")
    # Where should the job nobody assigned yet go? Compare it with each centre.
    loose = "Abend error handler"
    for label, centre in centres.items():
        print(f"  {loose} vs {label}: cosine {cosine_similarity(ITEMS[loose], centre):.3f}")
    print("  The same idea is a drift check: compare the centre of this month's items with last month's.\n")


def stretch_sensitivity() -> None:
    print("STRETCH 3 - which dimension moves the cosine most? (COBOL batch posting vs Monthly report extract)")
    base_a, b = ITEMS["COBOL batch posting job"], ITEMS["Monthly report extract"]
    base = cosine_similarity(base_a, b)
    print(f"  baseline cosine = {base:.4f}")
    for i, dim in enumerate(DIMS):
        changes = []
        for step in (+1, +2):
            a = list(base_a)
            a[i] = a[i] + step
            changes.append(f"{step:+d}: {cosine_similarity(a, b) - base:+.4f}")
        print(f"  {dim:<20} " + "   ".join(changes))
    print("  A number moves the score most when it is in a dimension where the two items disagree;")
    print("  raising an already-large shared number barely moves it. No dimension has a fixed weight.\n")


if __name__ == "__main__":
    task_e()
    stretch_unit_identity()
    stretch_centroids()
    stretch_sensitivity()
