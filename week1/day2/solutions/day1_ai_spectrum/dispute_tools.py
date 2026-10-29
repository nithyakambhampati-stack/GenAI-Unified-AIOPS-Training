"""
solutions/day1_ai_spectrum/dispute_tools.py
===========================================
The "business system" that every level of the spectrum plugs into.

Scenario (synthetic, fictional retailer): customers write in asking for refunds.
A support team must decide, per ticket, one of:
    refund | deny | status_update | escalate

This file contains NO AI. It is ordinary, deterministic Python:
  * the data (orders, tickets, policy)
  * the policy rules, written as code            -> evaluate()
  * the actions that change things               -> DisputeDesk.issue_refund(), escalate()
  * the tool descriptions the model will see     -> build_tools()

WHY THIS MATTERS (the main lesson of Day 1)
-------------------------------------------
The AI levels differ in how much they decide for themselves, but the DANGEROUS
actions always pass through the guardrails in this file. A model can be talked
into things by a clever customer message; Python code cannot. So:
    "Put rules in code, let the model do the language and the reasoning."
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable

from common import config

DATA_DIR = Path(__file__).resolve().parent / "data"

# Fixed "today" so the lab gives the same answers on every machine and every day.
TODAY = date(2026, 10, 22)

# Policy numbers (kept in step with data/policy.md).
LATE_GRACE_DAYS = 3          # an order is "late" only if it arrived MORE than this many days after the promise
CHANGE_OF_MIND_DAYS = 30     # change-of-mind window, counted from delivery
AUTO_APPROVE_LIMIT = 100.00  # an agent may approve refunds up to this value by itself


# ----------------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------------
def load_orders() -> dict[str, dict]:
    """Return orders keyed by order_id."""
    rows = json.loads((DATA_DIR / "orders.json").read_text(encoding="utf-8"))
    return {row["order_id"]: row for row in rows}


def load_tickets() -> list[dict]:
    """Return the support tickets as a list."""
    return json.loads((DATA_DIR / "tickets.json").read_text(encoding="utf-8"))


def policy_text() -> str:
    """Return the refund policy as plain text (the agents are allowed to read it)."""
    return (DATA_DIR / "policy.md").read_text(encoding="utf-8")


def _d(value: str | None) -> date | None:
    """Parse 'YYYY-MM-DD' into a date (None stays None)."""
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None


# ----------------------------------------------------------------------------------
# The policy, as code
# ----------------------------------------------------------------------------------
def evaluate(ticket_email: str, order: dict | None) -> dict[str, Any]:
    """
    Apply the refund policy to ONE order and return a decision.

    Returns a dict with:
        decision     : "refund" | "deny" | "status_update" | "escalate"
        reason_code  : short machine-readable reason
        amount       : refund amount (0 unless decision == "refund")
        needs_human  : True if the amount is above the auto-approval limit
        explanation  : one plain-English sentence
    """
    if order is None:
        return _decision("escalate", "ORDER_NOT_FOUND", 0, "No such order - a human must check.")

    # Rule 5 - ownership. The email comes from the TICKET (our data), never from the model.
    if order["customer_email"].lower() != ticket_email.lower():
        return _decision("escalate", "OWNERSHIP_MISMATCH", 0,
                         "The requester is not the customer on the order.")

    # Rule 4 - not delivered yet.
    if order["status"] != "delivered":
        return _decision("status_update", "IN_TRANSIT", 0,
                         "The order has not been delivered yet; send a status update.")

    delivered, promised = _d(order["delivered"]), _d(order["promised"])
    days_late = (delivered - promised).days  # negative means it arrived early

    # Rule 2 - damaged on arrival (the courier note says so).
    if "crushed" in order["condition_note"].lower() or "damaged" in order["condition_note"].lower():
        return _decision("refund", "DAMAGED", order["amount"], "Courier recorded damage on arrival.", order)

    # Rule 1 - late delivery beyond the grace period.
    if days_late > LATE_GRACE_DAYS:
        return _decision("refund", "LATE_DELIVERY", order["amount"],
                         f"Delivered {days_late} days after the promised date.", order)

    # Rule 3 - change of mind: outside the window it is a plain denial.
    days_since_delivery = (TODAY - delivered).days
    if days_since_delivery > CHANGE_OF_MIND_DAYS:
        return _decision("deny", "OUTSIDE_WINDOW", 0,
                         f"Delivered {days_since_delivery} days ago; the change-of-mind window is "
                         f"{CHANGE_OF_MIND_DAYS} days.")

    # Within the window but no fault found: a person must decide.
    return _decision("escalate", "MANUAL_REVIEW", 0, "No fault found; needs a human decision.")


def _decision(decision: str, code: str, amount: float, why: str, order: dict | None = None) -> dict[str, Any]:
    """Small helper so every decision has the same shape."""
    return {
        "decision": decision,
        "reason_code": code,
        "amount": amount,
        "needs_human": amount > AUTO_APPROVE_LIMIT,
        "explanation": why,
    }


# ----------------------------------------------------------------------------------
# The desk: holds state and performs the ONLY actions that change anything
# ----------------------------------------------------------------------------------
class DisputeDesk:
    """
    One object per run. Holds orders, tickets, a refund budget and everything that
    happened (refunds, approvals waiting for a human, escalations, an audit log).
    """

    def __init__(self, budget: float = 300.00, write_logs: bool = True):
        self.orders = load_orders()
        self.tickets = {t["ticket_id"]: t for t in load_tickets()}
        self.budget_remaining = budget            # spend cap for this run (Level 5 safety net)
        self.refunds: list[dict] = []             # refunds actually paid (simulated)
        self.pending_approval: list[dict] = []    # refunds waiting for a human
        self.escalations: list[dict] = []         # tickets handed to a human
        self.replies: list[dict] = []             # customer replies drafted
        self.audit: list[dict] = []               # everything, in order
        self._write_logs = write_logs

    # -- audit ---------------------------------------------------------------------
    def log(self, action: str, **details: Any) -> None:
        """Append one audit record. Every tool call lands here, allowed or blocked."""
        record = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "action": action, **details}
        self.audit.append(record)

    def save_audit(self, filename: str) -> Path | None:
        """Write the audit trail as JSON Lines (one JSON object per line) into outputs/."""
        if not self._write_logs:
            return None
        path = config.output_dir() / filename
        path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in self.audit) + "\n", encoding="utf-8")
        return path

    # -- read-only tools (safe) ---------------------------------------------------------
    def lookup_order(self, order_id: str) -> dict:
        """Return an order record plus derived facts the model should not have to calculate."""
        order = self.orders.get(order_id.strip().upper())
        self.log("lookup_order", order_id=order_id, found=bool(order))
        if not order:
            return {"error": f"Order {order_id} not found"}
        result = dict(order)
        if order["delivered"]:
            # Derived by code, so the model never does date arithmetic (a classic source of mistakes).
            result["days_late"] = (_d(order["delivered"]) - _d(order["promised"])).days
            result["days_since_delivery"] = (TODAY - _d(order["delivered"])).days
        return result

    def get_policy(self) -> dict:
        self.log("get_policy")
        return {"policy": policy_text()}

    def get_ticket(self, ticket_id: str) -> dict:
        self.log("get_ticket", ticket_id=ticket_id)
        ticket = self.tickets.get(ticket_id)
        return ticket if ticket else {"error": f"Ticket {ticket_id} not found"}

    def list_open_tickets(self) -> dict:
        """Tickets not yet closed by a refund, escalation or reply."""
        closed = ({r["ticket_id"] for r in self.refunds} | {p["ticket_id"] for p in self.pending_approval}
                  | {e["ticket_id"] for e in self.escalations} | {r["ticket_id"] for r in self.replies})
        open_ids = [tid for tid in self.tickets if tid not in closed]
        self.log("list_open_tickets", count=len(open_ids))
        return {"open_ticket_ids": open_ids}

    # -- write tools (guarded) ------------------------------------------------------------
    def issue_refund(self, ticket_id: str, order_id: str, amount: float, reason: str) -> dict:
        """
        Pay a refund - but only if EVERY guardrail passes. The model asks; this code decides.

        Guardrails, in order:
          1. ticket and order must exist
          2. the policy (evaluate) must say "refund"  -> blocks injected or invented requests
          3. the amount must equal the order amount   -> model cannot choose its own number
          4. not already refunded                     -> no double payment
          5. above the auto-approval limit            -> goes to a human queue, NOT paid
          6. the run budget must cover it             -> hard spend cap
        """
        ticket = self.tickets.get(ticket_id)
        order = self.orders.get(order_id.strip().upper())
        if not ticket or not order:
            return self._blocked(ticket_id, order_id, amount, "UNKNOWN_TICKET_OR_ORDER")

        verdict = evaluate(ticket["customer_email"], order)          # guardrail 2
        if verdict["decision"] != "refund":
            return self._blocked(ticket_id, order_id, amount, f"POLICY_SAYS_{verdict['decision'].upper()}:{verdict['reason_code']}")

        if abs(float(amount) - order["amount"]) > 0.005:             # guardrail 3
            return self._blocked(ticket_id, order_id, amount, f"AMOUNT_MISMATCH(order is {order['amount']:.2f})")

        if any(r["order_id"] == order["order_id"] for r in self.refunds + self.pending_approval):  # guardrail 4
            return self._blocked(ticket_id, order_id, amount, "DUPLICATE_REFUND")

        entry = {"ticket_id": ticket_id, "order_id": order["order_id"], "amount": order["amount"],
                 "reason_code": verdict["reason_code"], "agent_reason": reason}

        if order["amount"] > AUTO_APPROVE_LIMIT:                     # guardrail 5
            self.pending_approval.append(entry)
            self.log("refund_pending_human_approval", **entry)
            return {"status": "pending_human_approval",
                    "note": f"Amount exceeds the {AUTO_APPROVE_LIMIT:.2f} auto-approval limit; queued for a human."}

        if order["amount"] > self.budget_remaining:                  # guardrail 6
            return self._blocked(ticket_id, order_id, amount, "BUDGET_EXCEEDED")

        self.budget_remaining -= order["amount"]
        self.refunds.append(entry)
        self.log("refund_issued", **entry, budget_remaining=round(self.budget_remaining, 2))
        return {"status": "refunded", "amount": order["amount"], "budget_remaining": round(self.budget_remaining, 2)}

    def escalate_to_human(self, ticket_id: str, reason: str) -> dict:
        """Hand a ticket to a person. Always allowed - escalating is the safe default."""
        entry = {"ticket_id": ticket_id, "reason": reason}
        self.escalations.append(entry)
        self.log("escalated", **entry)
        return {"status": "escalated"}

    def draft_reply(self, ticket_id: str, message: str) -> dict:
        """Save a customer reply as a DRAFT. Nothing is sent: a person sends it."""
        entry = {"ticket_id": ticket_id, "message": message}
        self.replies.append(entry)
        self.log("reply_drafted", ticket_id=ticket_id)
        return {"status": "draft_saved"}

    def _blocked(self, ticket_id: str, order_id: str, amount: Any, why: str) -> dict:
        """Record a refused action. Blocked attempts are valuable audit evidence."""
        self.log("refund_BLOCKED", ticket_id=ticket_id, order_id=order_id, amount=amount, why=why)
        return {"status": "blocked", "reason": why}


# ----------------------------------------------------------------------------------
# Tool descriptions the model sees
# ----------------------------------------------------------------------------------
def _tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    """Build one tool definition in the Anthropic JSON-schema format."""
    return {"name": name, "description": description,
            "input_schema": {"type": "object", "properties": properties, "required": required}}


_STR = {"type": "string"}

TOOL_DEFS: dict[str, dict] = {
    "lookup_order": _tool("lookup_order", "Look up an order by ID. Returns status, dates, amount, courier notes, days_late.",
                          {"order_id": {**_STR, "description": "e.g. ORD-1001"}}, ["order_id"]),
    "get_policy": _tool("get_policy", "Return the refund policy text.", {}, []),
    "get_ticket": _tool("get_ticket", "Return one support ticket by ID.", {"ticket_id": _STR}, ["ticket_id"]),
    "list_open_tickets": _tool("list_open_tickets", "List ticket IDs that still need handling.", {}, []),
    "issue_refund": _tool("issue_refund",
                          "Request a refund for a ticket's order. Guardrails in code may block it or queue it for a human.",
                          {"ticket_id": _STR, "order_id": _STR, "amount": {"type": "number"},
                           "reason": {**_STR, "description": "why this refund is justified"}},
                          ["ticket_id", "order_id", "amount", "reason"]),
    "escalate_to_human": _tool("escalate_to_human", "Hand the ticket to a human agent, with the reason.",
                               {"ticket_id": _STR, "reason": _STR}, ["ticket_id", "reason"]),
    "draft_reply": _tool("draft_reply", "Save a draft reply to the customer (a person reviews and sends it).",
                         {"ticket_id": _STR, "message": _STR}, ["ticket_id", "message"]),
}

READ_ONLY = ["lookup_order", "get_policy"]
SINGLE_TICKET = ["lookup_order", "get_policy", "issue_refund", "escalate_to_human", "draft_reply"]
QUEUE = ["list_open_tickets", "get_ticket", "lookup_order", "get_policy", "issue_refund",
         "escalate_to_human", "draft_reply"]


def build_tools(desk: DisputeDesk, names: list[str]) -> tuple[list[dict], dict[str, Callable[..., Any]]]:
    """
    Return (tool_definitions, handlers) for the chosen tool names.

    The model only ever sees the definitions. The handlers are the real Python
    methods - the model can request them but never touches the code itself.
    """
    handlers = {name: getattr(desk, name) for name in names}
    return [TOOL_DEFS[n] for n in names], handlers
