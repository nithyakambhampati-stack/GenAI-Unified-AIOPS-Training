"""
injection.py - basic defences against prompt injection.

Prompt injection: text inside a document or a question that tries to give the model NEW instructions
("ignore previous instructions ...", "SYSTEM NOTE: ..."). The model cannot always tell your rules from the data it reads.
Two basic defences, used together:
  1. detect and remove obvious instruction-like lines before the model sees them (this file)
  2. wrap untrusted text in delimiters and tell the model, in the system message, that it is DATA, not instructions
Neither is perfect. That is why the answer is also verified afterwards (chain.py).
"""
import re

PATTERNS = [
    r"ignore (all |any )?(the )?(previous|prior|above|earlier) instructions",
    r"disregard (all |any )?(the )?(previous|prior|above|earlier|your) (instructions|rules)",
    r"forget (all |your |the )?(previous |prior )?(instructions|rules)",
    r"system (note|prompt|message|override)\s*:",
    r"\bpretend\b",
    r"\byou are now\b",
    r"\bnew instructions?\b",
    r"\bconfirm that (all )?(charges|fees|claims)\b",
]
REDACTED = "[removed: instruction-like text]"
SENTENCE = re.compile(r"(?<=[.!?])\s+")


def detect_injection(text):
    """Return the list of patterns found in the text (empty list = nothing suspicious). Ignore case."""
    return [p for p in PATTERNS if re.search(p, text, re.IGNORECASE)]


def redact(text):
    """Replace every sentence that looks like an instruction with a marker. Keeps the rest of the text.

    Works per sentence, not per line, so a real question that follows an injected sentence on the same line survives.
    """
    out = []
    for line in text.splitlines():
        if not detect_injection(line):
            out.append(line)
            continue
        out.append(" ".join(REDACTED if detect_injection(s) else s for s in SENTENCE.split(line)))
    return "\n".join(out)


def wrap_untrusted(text, tag="document"):
    """Wrap text in <tag> ... </tag>. A closing tag inside the text must not be able to end the block early."""
    # Neutralise any opening or closing tag of the same name inside the text, whatever its case or spacing.
    safe = re.sub(r"<(\s*/?\s*" + re.escape(tag) + r")", r"&lt;\1", text, flags=re.IGNORECASE)
    return f"<{tag}>\n{safe}\n</{tag}>"
