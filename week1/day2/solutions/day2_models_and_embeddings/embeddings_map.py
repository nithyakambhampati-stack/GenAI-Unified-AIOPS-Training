"""
Embeddings: turning meaning into numbers  (and drawing a "map of meaning")
==========================================================================
An EMBEDDING is a list of numbers (a vector) that represents the MEANING of a piece of
text. Texts with similar meaning get vectors that point in similar directions - even
when they share no words.

    "I want my money returned for a broken item"   <-- no word in common with ...
    "Please reimburse the full purchase price"     <-- ... this one, yet very similar in meaning

COSINE SIMILARITY measures that closeness: 1.0 = same direction, 0 = unrelated.
A VECTOR DATABASE stores many embeddings and finds the nearest ones quickly. This
script does the same thing with a plain list, so you can see there is no magic.

Two embedders
-------------
  * fastembed (real, small open model "bge-small") - run:  pip install -r requirements-embeddings.txt
    The first run downloads the model (~70 MB) and caches it; needs internet once.
  * toy lexicon embedder (built in, works offline) - a 6-number vector built from word groups
    (money, delivery, damage, access, leave, security). Crude, but it shows the idea in a
    way you can inspect by eye.

Run:
    python solutions/day2_models_and_embeddings/embeddings_map.py           # uses fastembed if installed
    python solutions/day2_models_and_embeddings/embeddings_map.py --toy     # force the offline toy embedder

Output: nearest-neighbour results in the terminal and outputs/embedding_map.png
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zlib
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # run from any folder

from common import config  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "data"

# ----------------------------------------------------------------------------------
# Embedder 1: the toy lexicon embedder (offline)
# ----------------------------------------------------------------------------------
# Each dimension is a CONCEPT. A word that belongs to the concept adds to that dimension.
CONCEPTS = {
    "money":    {"refund", "reimburse", "money", "payment", "price", "card", "credit", "invoice", "charged", "amount", "reversed", "purchase", "returned"},
    "delivery": {"parcel", "package", "courier", "shipment", "order", "dispatched", "warehouse", "tracking", "arrived", "late", "promised", "address", "delivery"},
    "damage":   {"broken", "faulty", "damaged", "smashed", "crushed", "defective"},
    "access":   {"password", "login", "sign", "account", "locked", "access", "portal", "code", "two-factor", "folder", "grant", "profile"},
    "leave":    {"leave", "holiday", "vacation", "sick", "annual", "days", "manager", "carry", "book"},
    "security": {"personal", "confidential", "privacy", "breach", "data"},
}
CONCEPT_NAMES = list(CONCEPTS)


def toy_embed(texts: list[str]) -> np.ndarray:
    """Count concept words per text (plus small nudges from other words), then normalise to unit length."""
    vectors = []
    for text in texts:
        words = re.findall(r"[a-z\-]+", text.lower())
        vec = np.array([sum(w in group for w in words) for group in CONCEPTS.values()], dtype=float)
        # Words outside every concept group add a small, repeatable nudge to one dimension (chosen by a
        # checksum of the word). Real models also pick up "other" words; here it also keeps different
        # sentences from collapsing onto exactly the same point.
        known = set().union(*CONCEPTS.values())
        for w in words:
            if w not in known:
                vec[zlib.crc32(w.encode()) % len(vec)] += 0.12
        vec += 0.01
        vectors.append(vec / np.linalg.norm(vec))   # unit length -> cosine similarity = dot product
    return np.vstack(vectors)


# ----------------------------------------------------------------------------------
# Embedder 2: a real model via fastembed (optional)
# ----------------------------------------------------------------------------------
def real_embed(texts: list[str]) -> np.ndarray:
    """Embed with a small open-source model running locally (no API key, no data leaves the machine)."""
    from fastembed import TextEmbedding  # imported here so the toy path works without the package

    model = TextEmbedding("BAAI/bge-small-en-v1.5")      # 384-number vectors
    vectors = np.array(list(model.embed(texts)))
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def choose_embedder(force_toy: bool):
    """Return (name, function). Falls back to the toy embedder if fastembed is missing."""
    if not force_toy:
        try:
            import fastembed  # noqa: F401

            return "fastembed bge-small (384-d)", real_embed
        except ImportError:
            print("fastembed not installed -> using the offline toy embedder.\n"
                  "(For real embeddings: pip install -r requirements-embeddings.txt)\n")
    return "toy lexicon embedder (6-d)", toy_embed


# ----------------------------------------------------------------------------------
# Search and plotting
# ----------------------------------------------------------------------------------
def cosine_top_k(query_vec: np.ndarray, matrix: np.ndarray, k: int = 3) -> list[tuple[int, float]]:
    """Rank rows of `matrix` by cosine similarity to the query. Vectors are unit length, so dot = cosine."""
    scores = matrix @ query_vec
    order = np.argsort(-scores)[:k]
    return [(int(i), float(scores[i])) for i in order]


def keyword_overlap(a: str, b: str) -> int:
    """How many words two texts share - what a classic keyword search would see."""
    wa, wb = set(re.findall(r"[a-z]+", a.lower())), set(re.findall(r"[a-z]+", b.lower()))
    return len(wa & wb)


def plot_map(vectors: np.ndarray, rows: list[dict], title: str, path: Path) -> None:
    """Project the vectors to 2-D with PCA and draw them, one colour per topic."""
    import matplotlib

    matplotlib.use("Agg")  # draw to a file; no window needed (works on servers and VMs)
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA

    points = PCA(n_components=2, random_state=0).fit_transform(vectors)  # keep the 2 directions with most variation
    topics = sorted({r["topic"] for r in rows})
    palette = ["#1f77b4", "#d95f02", "#2ca02c", "#7b3294", "#e7298a", "#66a61e", "#a6761d", "#666666"]
    if len(topics) > len(palette):
        # zip() would silently drop the extra topics from the map, so refuse instead.
        raise ValueError(f"{len(topics)} topics but only {len(palette)} colours: add colours to the palette")
    fig, ax = plt.subplots(figsize=(8, 6))
    for colour, topic in zip(palette, topics):
        idx = [i for i, r in enumerate(rows) if r["topic"] == topic]
        ax.scatter(points[idx, 0], points[idx, 1], s=90, color=colour, label=topic, edgecolor="white")
    ax.set_title(title)
    ax.set_xlabel("PCA axis 1 (axes have no fixed meaning)")
    ax.set_ylabel("PCA axis 2")
    ax.legend(title="topic")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Embeddings and semantic search demo")
    parser.add_argument("--toy", action="store_true", help="force the offline toy embedder")
    parser.add_argument("--query", action="append", default=[],
                        help="extra query to search for (repeat for several); added to the three built-in ones")
    args = parser.parse_args()

    rows = json.loads((DATA_DIR / "sentences.json").read_text(encoding="utf-8"))
    texts = [r["text"] for r in rows]
    name, embed = choose_embedder(args.toy)
    print(f"Embedder: {name}\nEmbedding {len(texts)} sentences ...")
    matrix = embed(texts)
    print(f"Each sentence became a vector of {matrix.shape[1]} numbers.\n")

    queries = [
        "Reimburse me for the defective goods",
        "I can't sign into my profile",
        "How much vacation am I entitled to?",
    ] + args.query
    q_vecs = embed(queries)
    for query, q_vec in zip(queries, q_vecs):
        print(f"QUERY: {query}")
        for rank, (i, score) in enumerate(cosine_top_k(q_vec, matrix), start=1):
            shared = keyword_overlap(query, texts[i])
            print(f"  {rank}. sim={score:5.2f}  shared words={shared}  [{rows[i]['topic']}] {texts[i]}")
        print()
    print("Look at 'shared words': the best matches share few or no words with the query - that is semantic search.")
    print("(The toy embedder is coarse, so ties at 1.00 are expected; a real model gives finer scores.)\n")

    # Show what the toy dimensions mean, so the numbers are not a black box.
    if name.startswith("toy"):
        print("Toy vector for the first sentence, by concept:")
        for concept, value in zip(CONCEPT_NAMES, matrix[0]):
            print(f"  {concept:<9}{value:5.2f}  {'#' * int(round(value * 20))}")
        print()

    path = config.output_dir() / "embedding_map.png"
    plot_map(matrix, rows, f"Map of meaning - {name}", path)
    print(f"Map saved: {path}  (sentences on the same topic should cluster)")


if __name__ == "__main__":
    main()
