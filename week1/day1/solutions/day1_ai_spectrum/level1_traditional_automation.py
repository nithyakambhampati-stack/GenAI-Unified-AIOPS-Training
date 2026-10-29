"""
Level 1 - TRADITIONAL AUTOMATION  (no AI, no API key needed)
============================================================
Rules written by a person: "if the text contains X, do Y".

    ticket text --> keyword rules --> policy code --> action

Strengths : fast, free, 100% predictable, easy to audit.
Weakness  : it only understands the exact words its author thought of.
            Paraphrases, typos, other languages and context fall straight through.

Run:
    python solutions/day1_ai_spectrum/level1_traditional_automation.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Put the repository root on the import path so this file runs from ANY folder.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from solutions.day1_ai_spectrum import dispute_tools as dt  # noqa: E402
from solutions.day1_ai_spectrum._report import print_scoreboard  # noqa: E402

# --- The "intelligence" of Level 1: a hand-written word list -------------------------
REFUND_WORDS = ("refund", "money back")
ORDER_ID = re.compile(r"ORD-\d+", re.IGNORECASE)


def classify(text: str) -> tuple[str, str | None]:
    """Return (intent, order_id). Pure keyword matching - no understanding involved."""
    match = ORDER_ID.search(text)
    order_id = match.group(0).upper() if match else None
    wants_refund = any(word in text.lower() for word in REFUND_WORDS)
    return ("refund_request" if wants_refund else "other"), order_id


def handle(desk: dt.DisputeDesk, ticket: dict) -> str:
    """Route one ticket with fixed rules and perform the action. Returns a short note."""
    intent, order_id = classify(ticket["text"])

    if order_id is None:
        desk.escalate_to_human(ticket["ticket_id"], "Rules could not find an order number")
        return "no order id -> escalated"

    verdict = dt.evaluate(ticket["customer_email"], desk.orders.get(order_id))

    if intent != "refund_request":
        # The customer did not use our refund words, so we only send a canned status reply.
        desk.draft_reply(ticket["ticket_id"], "Thanks for contacting us. Your order status is on its way to you.")
        return "no refund keyword -> canned reply"

    if verdict["decision"] == "refund":
        # issue_refund applies the guardrails again (limit, budget, duplicates).
        result = desk.issue_refund(ticket["ticket_id"], order_id, verdict["amount"], verdict["reason_code"])
        return f"refund -> {result['status']}"
    if verdict["decision"] == "escalate":
        desk.escalate_to_human(ticket["ticket_id"], verdict["explanation"])
        return "policy says escalate"
    desk.draft_reply(ticket["ticket_id"], verdict["explanation"])
    return f"policy says {verdict['decision']} -> reply"


def main() -> None:
    desk = dt.DisputeDesk()
    print("LEVEL 1 - traditional automation (keyword rules + policy code)\n")
    for ticket in desk.tickets.values():
        print(f"{ticket['ticket_id']}: {handle(desk, ticket)}")
    print_scoreboard(desk)

    # --- Where rules break: same meaning, different words ---------------------------------
    print("\nBRITTLENESS DEMO - same intent, words the rule-writer did not expect:")
    probes = [
        "The mug in ORD-1002 arrived in pieces. I'd like to be reimbursed.",
        "Bestellung ORD-1001 kam viel zu spat an. Bitte Geld zuruck.",
        "my order ord-1003 is 12 days late!!! credit my card",
    ]
    for text in probes:
        intent, order_id = classify(text)
        print(f"  intent={intent:<15} order={order_id}  <- {text}")
    print("\nTakeaway: every paraphrase is a bug waiting to happen. Level 2 fixes this with a language model.")


if __name__ == "__main__":
    main()
