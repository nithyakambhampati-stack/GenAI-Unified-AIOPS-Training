"""
Verify what a model tells you  (human-in-the-loop in practice)
=============================================================
A fluent answer is not a correct answer. This script shows a simple, reusable pattern:

    PROPOSE  -> the model extracts figures from a contract, each with a word-for-word quote
    VERIFY   -> CODE checks (a) the quote really exists in the document,
                              (b) the number really appears in that quote, and
                              (c) derived figures match an independent recalculation
    TIER     -> any failed check raises the risk tier
    DECIDE   -> a human reviews anything that is not LOW, and every decision is logged

The model is allowed to be wrong; the system is not allowed to ACT on an unchecked answer.

Run:
    python solutions/day2_models_and_embeddings/verify_outputs.py --offline-demo   # no API key needed
    python solutions/day2_models_and_embeddings/verify_outputs.py                   # live call to the model

--offline-demo uses a prepared model reply that contains two deliberate mistakes
(a made-up quote and a wrong calculation) so you can watch the checks catch them.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # run from any folder

from common import config, llm  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "data"

# What we ask for. For each item the model must return a number AND the exact supporting quote.
EXTRACT_SYSTEM = """You extract figures from a contract. Use ONLY the provided clauses.
Reply with ONLY a JSON object with exactly these keys. Each value is {"value": <number>, "quote": "<exact words copied from the clauses>"}.
For derived items, "quote" must be the clause sentence the calculation relies on.
  monthly_fee               - the fixed monthly fee
  credit_percent_per_step   - credit percent for each 0.5 percentage-point step below the target
  credit_cap_percent        - the maximum credit as a percent of the monthly fee
  credit_for_98_6           - money credit owed when availability was 98.6%
  termination_charge_8m     - money charge if the Customer terminates after 8 months"""

# A canned "model reply" for the offline demo: two items are deliberately wrong.
OFFLINE_REPLY = json.dumps({
    "monthly_fee": {"value": 12400, "quote": "a fixed monthly fee of 12,400.00 for the Managed Support Service"},
    "credit_percent_per_step": {"value": 5, "quote": "the Supplier shall credit 5% of that month's fee for each full 0.5 percentage points below 99.5%"},
    "credit_cap_percent": {"value": 25, "quote": "up to a maximum credit of 25% of the monthly fee"},          # WRONG: invented quote and number
    "credit_for_98_6": {"value": 1240, "quote": "the Supplier shall credit 5% of that month's fee for each full 0.5 percentage points below 99.5%"},   # WRONG: 2 steps instead of 1
    "termination_charge_8m": {"value": 24800, "quote": "an early-termination charge equal to two months' fees applies"},
})


# ----------------------------------------------------------------------------------
# Independent ground truth: computed by code, never by the model
# ----------------------------------------------------------------------------------
def ground_truth() -> dict[str, float]:
    fee, step_pct, cap_pct = 12_400.00, 5.0, 20.0
    availability, target, step_size = 98.6, 99.5, 0.5
    full_steps = int((target - availability + 1e-9) // step_size)       # whole 0.5-point steps below target
    credit = min(fee * step_pct / 100 * full_steps, fee * cap_pct / 100)  # cap at 20% of the fee
    termination = 2 * fee                                                # two months' fees
    return {"monthly_fee": fee, "credit_percent_per_step": step_pct, "credit_cap_percent": cap_pct,
            "credit_for_98_6": round(credit, 2), "termination_charge_8m": termination}


# Items whose number must literally appear inside the quote (others are derived by calculation).
NUMBER_IN_QUOTE = {"monthly_fee", "credit_percent_per_step", "credit_cap_percent"}


def _squash(text: str) -> str:
    """Collapse whitespace and lowercase, so line breaks in the contract do not cause false alarms."""
    return re.sub(r"\s+", " ", text).strip().lower()


def _number_variants(value: float) -> list[str]:
    """Ways the same number may be written in a contract: 12400, 12,400, 12,400.00, 5, 5%."""
    n = float(value)
    forms = {f"{n:,.2f}", f"{n:,.0f}", f"{n:.0f}", f"{n:g}"}
    return sorted(forms)


def verify(findings: dict, document: str) -> list[dict]:
    """Run the three checks on every item. Pure function: easy to unit-test, no model involved."""
    truth, doc = ground_truth(), _squash(document)
    checks = []
    for key, expected in truth.items():
        item = findings.get(key)
        row = {"item": key, "expected": expected, "model_value": None, "quote_exists": False,
               "number_in_quote": None, "value_correct": False}
        if isinstance(item, dict):
            row["model_value"] = item.get("value")
            quote = _squash(str(item.get("quote", "")))
            row["quote_exists"] = bool(quote) and quote in doc                    # check (a): not made up
            if key in NUMBER_IN_QUOTE:                                            # check (b): number is in the quote
                row["number_in_quote"] = any(v in quote for v in _number_variants(item.get("value", 0)))
            try:
                row["value_correct"] = abs(float(item.get("value")) - expected) < 0.005  # check (c): recalculation
            except (TypeError, ValueError):
                row["value_correct"] = False
        row["passed"] = row["quote_exists"] and row["value_correct"] and row["number_in_quote"] in (True, None)
        checks.append(row)
    return checks


def risk_tier(checks: list[dict]) -> tuple[str, str]:
    """Turn check results into a tier and the action it implies."""
    if any(not c["quote_exists"] for c in checks):
        return "HIGH", "Possible fabricated evidence. Do not use. A person must review the source."
    if any(not c["value_correct"] for c in checks):
        return "MEDIUM", "Numbers disagree with recalculation. A person must correct them before use."
    return "LOW", "All checks passed. Normal practice: spot-check a sample."


def write_audit(tier: str, checks: list[dict], source: str) -> Path:
    """Append one line per run to a JSON Lines audit log (who/what/when/outcome)."""
    path = config.output_dir() / "verification_audit.jsonl"
    record = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "source": source,
              "tier": tier, "failed_items": [c["item"] for c in checks if not c["passed"]]}
    with path.open("a", encoding="utf-8") as fh:  # "a" = append, never overwrite history
        fh.write(json.dumps(record) + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify model-extracted contract figures")
    parser.add_argument("--offline-demo", action="store_true", help="use a prepared reply with deliberate errors")
    args = parser.parse_args()

    document = (DATA_DIR / "vendor_clause.txt").read_text(encoding="utf-8")

    if args.offline_demo:
        raw, source = OFFLINE_REPLY, "offline-demo"
    else:
        if not config.get_api_key():
            raise SystemExit(f"ANTHROPIC_API_KEY is not set. Edit {config.ENV_PATH}, or use --offline-demo.")
        raw = llm.ask(f"<clauses>\n{document}\n</clauses>", system=EXTRACT_SYSTEM, max_tokens=800).text
        source = config.DEFAULT_MODEL

    try:
        findings = llm.extract_json(raw)
    except ValueError:
        raise SystemExit("The model did not return usable JSON. That is itself a result: do not act on it.")

    checks = verify(findings, document)
    print(f"{'item':<26}{'model':>10}{'expected':>10}  quote exists  number in quote  value ok")
    print("-" * 84)
    for c in checks:
        niq = "n/a" if c["number_in_quote"] is None else ("yes" if c["number_in_quote"] else "NO")
        print(f"{c['item']:<26}{str(c['model_value']):>10}{c['expected']:>10g}  "
              f"{'yes' if c['quote_exists'] else 'NO':<13}{niq:<17}{'yes' if c['value_correct'] else 'NO'}")

    tier, action = risk_tier(checks)
    print(f"\nRISK TIER: {tier}\n-> {action}")
    print(f"Audit entry appended to: {write_audit(tier, checks, source)}")
    print("\nPattern to remember: the model PROPOSES, code VERIFIES, a human DECIDES, the system LOGS.")


if __name__ == "__main__":
    main()
