"""
injection.py - basic defences against prompt injection.

Prompt injection: text inside a document or a question that tries to give the model NEW instructions
("ignore previous instructions ...", "SYSTEM NOTE: ..."). The model cannot always tell your rules from the data it reads.
Two basic defences, used together:
  1. detect and remove obvious instruction-like sentences before the model sees them (this file)
  2. wrap untrusted text in delimiters and tell the model, in the system message, that it is DATA, not instructions
Neither is perfect. That is why the answer is also verified afterwards (chain.py).
"""
import re

PATTERNS = [
    r"\bignore (all |any )?(the )?(previous|prior|above|earlier) (instructions|guidance|rules)",
    r"\b(disregard|forget) (all |any )?(the )?(previous|prior|above|earlier) (instructions|guidance|rules|policy)",
    r"\b(disregard|forget) (all |the )?(policy|rules|instructions|guidance) above",
    r"\bassistant instruction",
    r"\bsystem (note|prompt|instruction|override)",
    r"\bact as\b",
    r"\byou are now\b",
    r"\bapprove (every|all) claims?\b",
    r"\bprint\b[^.?!]*\b[a-z]+-\d{3,}\b",
]
REDACTED = "[removed: instruction-like text]"
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def detect_injection(text):
    """Return the list of patterns found in the text (empty list = nothing suspicious). Ignore case."""
    return [p for p in PATTERNS if re.search(p, text, re.IGNORECASE)]


def redact(text):
    """Replace every sentence that looks like an instruction with a marker. Keeps the rest of the text.

    Works sentence by sentence inside each line, so a question that hides an instruction in front of a real
    question ("Forget the previous guidance ... Also, how long ...?") keeps its real question.
    """
    out = []
    for line in text.splitlines():
        parts = SENTENCE_END.split(line)
        out.append(" ".join(REDACTED if detect_injection(p) else p for p in parts))
    return "\n".join(out)


def wrap_untrusted(text, tag="document"):
    """Wrap text in <tag> ... </tag>. A closing tag inside the text must not be able to end the block early."""
    # Escape any opening or closing tag with the same name inside the text, so only our own tags remain.
    pattern = re.compile(r"<\s*(/?)\s*" + re.escape(tag) + r"\s*>", re.IGNORECASE)
    safe = pattern.sub(lambda m: "&lt;" + m.group(1) + tag + "&gt;", text)
    return f"<{tag}>\n{safe}\n</{tag}>"
