"""
step4_why_cosine.py  -  WHY do closer vectors mean similar meaning, and why cosine?
====================================================================================
Four short experiments, no API key, standard library only (numpy is used at the end if installed).

    python step4_why_cosine.py
"""
from __future__ import annotations

import vector_math as vm


def experiment_1_direction_vs_length() -> None:
    print("\nEXPERIMENT 1 - Same direction, different length")
    short, long_ = [3, 4], [6, 8]          # the long one is the short one doubled
    print(f"  A = {short}, B = {long_} (B is A doubled)")
    print(f"  cosine similarity  = {vm.cosine_similarity(short, long_):.4f}   <- identical direction: 'the same meaning'")
    print(f"  euclidean distance = {vm.euclidean_distance(short, long_):.4f}   <- far apart, only because B is bigger")
    print("  Real-life version: a 2-page and a 20-page policy about the SAME topic produce vectors of different length.")
    print("  Cosine ignores length and compares topic. That is why it is the usual choice for text.")


def experiment_2_ranking() -> None:
    """Rank the same sentences with cosine and with distance, for every query in the data file."""
    data = vm.load_data()
    for query_text, query in data["queries"].items():
        print(f"\nEXPERIMENT 2 - Rank sentences for the query: '{query_text}'")
        rows = []
        for text, vec in data["sentences"].items():
            rows.append((text, vm.cosine_similarity(query, vec), vm.euclidean_distance(query, vec)))
        by_cos = sorted(rows, key=lambda r: -r[1])      # higher cosine = more similar
        by_euc = sorted(rows, key=lambda r: r[2])       # lower distance = more similar
        print(f"  {'sentence':<68}{'cosine':>8}{'distance':>10}")
        for text, cos, euc in by_cos:
            print(f"  {text:<68}{cos:>8.3f}{euc:>10.3f}")
        print(f"  Best by cosine   : {by_cos[0][0]}")
        print(f"  Best by distance : {by_euc[0][0]}")
        if by_cos[0][0] != by_euc[0][0]:
            print("  THEY DISAGREE. Cosine prefers the very long document: it points the same way as the query.")
            print("  Distance prefers the short, on-topic sentence: the long document's vector is simply far away (it is big).")
            print("  Neither is always right. It is one reason retrieval systems cut documents into chunks of similar size (Day 4).")
        else:
            print("  They agree here. Look at the next query: there they will not.")


def experiment_3_unit_vectors() -> None:
    print("\nEXPERIMENT 3 - Shrink every vector to length 1 and the two measures become the same story")
    a, b = [5, 1, 2, 2], [5, 1, 3, 1]
    ua = [x / vm.norm(a) for x in a]
    ub = [x / vm.norm(b) for x in b]
    cos = vm.cosine_similarity(a, b)
    euc = vm.euclidean_distance(ua, ub)
    print(f"  cosine(loan, mortgage)                       = {cos:.4f}")
    print(f"  dot product of the unit-length versions      = {vm.dot(ua, ub):.4f}   (same number)")
    print(f"  distance^2 of unit-length versions           = {euc ** 2:.4f}")
    print(f"  2 - 2 x cosine                               = {2 - 2 * cos:.4f}   (same number)")
    print("  So on unit-length vectors: higher cosine <=> smaller distance. Many embedding models output unit-length vectors.")


def experiment_4_numpy_agrees() -> None:
    print("\nEXPERIMENT 4 - Do professional libraries give the same answers?")
    try:
        import numpy as np
    except ImportError:
        print("  numpy is not installed (optional). Skip, or run: pip install numpy")
        return
    a, b = [5, 1, 2, 2], [5, 1, 3, 1]
    np_cos = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    np_euc = float(np.linalg.norm(np.array(a) - np.array(b)))
    print(f"  cosine    mine={vm.cosine_similarity(a, b):.6f}  numpy={np_cos:.6f}")
    print(f"  distance  mine={vm.euclidean_distance(a, b):.6f}  numpy={np_euc:.6f}")
    print("  Same numbers: libraries do exactly this arithmetic, only faster and on millions of vectors at once.")


if __name__ == "__main__":
    experiment_1_direction_vs_length()
    experiment_2_ranking()
    experiment_3_unit_vectors()
    experiment_4_numpy_agrees()
