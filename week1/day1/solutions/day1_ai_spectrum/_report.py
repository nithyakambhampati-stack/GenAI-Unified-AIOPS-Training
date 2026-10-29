"""
solutions/day1_ai_spectrum/_report.py
=====================================
Shared helpers for the five level scripts: path setup, the "expected outcome" for
each ticket, and a results table.

The leading underscore in the filename is a Python convention meaning
"internal helper, not a lab exercise".
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow "python solutions/day1_ai_spectrum/levelN_xxx.py" from ANY folder: put the
# repository root on the import path so "from common import ..." works.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from solutions.day1_ai_spectrum import dispute_tools as dt  # noqa: E402


def expected_outcome(desk: dt.DisputeDesk, ticket: dict) -> str:
    """
    What a careful human following the policy would end up doing with this ticket.

    The policy code (dt.evaluate) is our ground truth, so we can score every level
    against it:
        refunded         - eligible and within the auto-approval limit
        pending_approval - eligible but above the limit (a human must approve)
        escalated        - a human must look at it
        reply            - no refund: send an explanation or a status update
    """
    import re

    match = re.search(r"ORD-\d+", ticket["text"], flags=re.IGNORECASE)
    order = desk.orders.get(match.group(0).upper()) if match else None
    verdict = dt.evaluate(ticket["customer_email"], order)
    if verdict["decision"] == "refund":
        return "pending_approval" if verdict["needs_human"] else "refunded"
    if verdict["decision"] == "escalate":
        return "escalated"
    return "reply"


def actual_outcome(desk: dt.DisputeDesk, ticket_id: str) -> str:
    """What a run actually did with the ticket, read from the desk's records."""
    if any(r["ticket_id"] == ticket_id for r in desk.refunds):
        return "refunded"
    if any(p["ticket_id"] == ticket_id for p in desk.pending_approval):
        return "pending_approval"
    if any(e["ticket_id"] == ticket_id for e in desk.escalations):
        return "escalated"
    if any(r["ticket_id"] == ticket_id for r in desk.replies):
        return "reply"
    return "UNHANDLED"


def print_scoreboard(desk: dt.DisputeDesk, ticket_ids: list[str] | None = None) -> tuple[int, int]:
    """Print expected vs actual per ticket and return (matches, total)."""
    ids = ticket_ids or list(desk.tickets)
    print(f"\n{'ticket':<7} {'expected':<17} {'actual':<17} match")
    print("-" * 50)
    matches = 0
    for tid in ids:
        exp = expected_outcome(desk, desk.tickets[tid])
        act = actual_outcome(desk, tid)
        ok = exp == act
        matches += ok
        print(f"{tid:<7} {exp:<17} {act:<17} {'yes' if ok else 'NO  <-- look here'}")
    print("-" * 50)
    print(f"{matches}/{len(ids)} tickets handled as the policy expects")
    print(f"Refunds paid: {sum(r['amount'] for r in desk.refunds):.2f}   "
          f"waiting for human approval: {sum(p['amount'] for p in desk.pending_approval):.2f}")
    return matches, len(ids)


def print_trace_event(event) -> None:
    """Callback for llm.run_tool_loop: show each tool call and result as it happens."""
    import json

    text = json.dumps(event.payload, ensure_ascii=False)
    text = text if len(text) <= 160 else text[:157] + "..."
    arrow = "  -> calls " if event.kind == "tool_call" else "  <- result"
    print(f"{arrow} {event.name}: {text}")


def require_key() -> None:
    """Stop with a friendly message (not a stack trace) when the API key is not set."""
    from common import config

    if not config.get_api_key():
        print(f"ANTHROPIC_API_KEY is not set. Edit {config.ENV_PATH} and run again.")
        raise SystemExit(1)
