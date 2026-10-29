"""
Redact personal data BEFORE text leaves your machine
====================================================
Rule of the lab: only synthetic or public text goes into consumer chat tools
(the homework). In real work, if text might contain personal data, run it through a
redaction step first - or better, do not paste it into a personal account at all.

This is a SIMPLE pattern-based redactor. It finds things with a recognisable shape:
emails, phone numbers, card numbers, order ids, dates of birth. It CANNOT reliably find
names or free-text details ("the lady in flat 4 who works at the bank").
Treat it as a safety net and a teaching tool, not as a compliance control.

Run:
    python solutions/day2_models_and_embeddings/redact_pii.py --text "Call Asha on +91 98765 43210 or asha@example.com"
    python solutions/day2_models_and_embeddings/redact_pii.py --file mytext.txt
    python solutions/day2_models_and_embeddings/redact_pii.py --demo
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Order matters: the card pattern must run before the phone pattern, otherwise a 16-digit
# card number could be eaten by the phone rule.
PATTERNS: list[tuple[str, re.Pattern]] = [
    ("EMAIL", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    # 13-16 digits, optionally separated by single spaces or dashes. Ends on a digit so the
    # trailing space is NOT swallowed.
    ("CARD", re.compile(r"\b(?:\d[ -]?){12,15}\d\b")),
    # Dates such as 1990-04-12 or 12/03/1988 (must run before PHONE, which also loves digits and dashes).
    ("DOB", re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b")),
    # Optional +, then 9-17 more digits/spaces/dashes/brackets, ending in a digit.
    ("PHONE", re.compile(r"(?<![\w.])\+?\d[\d\s\-()]{7,16}\d(?![\w.])")),
    ("ORDER_ID", re.compile(r"\bORD-\d+\b", re.IGNORECASE)),
]


def redact(text: str) -> tuple[str, dict[str, int]]:
    """Replace each match with a tag like [EMAIL]. Returns (clean text, count per type)."""
    counts: dict[str, int] = {}
    for label, pattern in PATTERNS:
        text, n = pattern.subn(f"[{label}]", text)
        if n:
            counts[label] = n
    return text, counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Pattern-based PII redaction")
    parser.add_argument("--text", help="text to redact")
    parser.add_argument("--file", help="path to a text file to redact")
    parser.add_argument("--demo", action="store_true", help="run on a built-in synthetic example")
    args = parser.parse_args()

    if args.demo:
        text = ("Customer Asha Rao (asha.rao@example.com, +91 98765 43210) says card 4111 1111 1111 1111 "
                "was charged for ORD-1001. DOB 1990-04-12.")
    elif args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        sys.exit(1)

    clean, counts = redact(text)
    print("ORIGINAL :", text)
    print("REDACTED :", clean)
    print("FOUND    :", counts or "nothing recognised")
    if args.demo:
        print("\nNote: the NAME 'Asha Rao' was NOT caught. Patterns cannot find names - a person must check.")
    else:
        print("\nReminder: names and free-text details are NOT detected. Read the result yourself before sharing.")


if __name__ == "__main__":
    main()
