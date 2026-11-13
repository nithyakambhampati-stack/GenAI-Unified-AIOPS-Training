"""
doc_store.py - turn an SOP text file into sections you can search and cite.

The SOP uses one line per heading, written  [S2.1] Title , followed by the section text until the next heading.
Every answer the assistant gives must cite one of these section ids.
"""
import re
from pathlib import Path

HEADING = re.compile(r"^\[(S\d+\.\d+)\]\s+(.*)$")
STOPWORDS = {"the", "a", "an", "is", "are", "of", "to", "for", "in", "on", "and", "or", "what", "how", "does", "do", "can",
             "which", "within", "by", "at", "if", "be", "with", "it", "its", "after", "before", "any", "there", "i", "me", "my"}


def split_sections(text):
    """Return a list of {"id", "title", "text"} dictionaries, one per [S#.#] heading, in order."""
    sections, current = [], None
    for line in text.splitlines():
        m = HEADING.match(line.strip())
        if m:                                              # a new heading starts a new section
            current = {"id": m.group(1), "title": m.group(2).strip(), "text": ""}
            sections.append(current)
        elif current is not None and line.strip():         # body lines belong to the latest heading; the preamble is skipped
            current["text"] = (current["text"] + "\n" + line.strip()).strip()
    return sections


def load_sections(path):
    return split_sections(Path(path).read_text(encoding="utf-8"))


def tokens(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]


def search(question, sections, k=3):
    """Rank sections by how many question words they contain (title words count double). Return the best k, best first."""
    q = set(tokens(question))
    scored = []
    for pos, s in enumerate(sections):
        points = len(q & set(tokens(s["text"]))) + 2 * len(q & set(tokens(s["title"])))
        scored.append((-points, pos, s))                   # ties keep document order, so results are predictable
    scored.sort(key=lambda t: (t[0], t[1]))
    return [s for _, _, s in scored[:k]]
