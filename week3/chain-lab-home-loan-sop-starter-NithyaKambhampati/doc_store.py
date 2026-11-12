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
        if m:
            current = {"id": m.group(1), "title": m.group(2).strip(), "lines": []}
            sections.append(current)
        elif current is not None:                     # text before the first heading (document title) is skipped
            current["lines"].append(line)
    return [{"id": s["id"], "title": s["title"], "text": "\n".join(s["lines"]).strip()} for s in sections]


def load_sections(path):
    return split_sections(Path(path).read_text(encoding="utf-8"))


def tokens(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]


def search(question, sections, k=3):
    """Rank sections by how many question words they contain (title words count double). Return the best k, best first."""
    words = set(tokens(question))
    scored = []
    for i, s in enumerate(sections):
        title, body = set(tokens(s["title"])), set(tokens(s["text"]))
        score = sum(2 if w in title else 1 if w in body else 0 for w in words)
        if score > 0:
            scored.append((-score, i, s))             # ties keep document order
    return [s for _, _, s in sorted(scored, key=lambda t: (t[0], t[1]))[:k]]


