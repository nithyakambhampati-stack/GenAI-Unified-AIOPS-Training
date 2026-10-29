"""
Homework helper: same query, three consumer chat tools (no API key needed)
==========================================================================
Homework: send the SAME prompt to ChatGPT, Claude.ai and Gemini in their normal web
or mobile chat apps and compare the answers. No API keys, no code, no cost.

This script prepares everything so the comparison is fair:
  1. It prints the exact prompt to paste (identical for every tool).
  2. It runs the redaction check on the prompt - a habit to build before pasting anything.
  3. It prints the lab's approved-tools guidance (an EXAMPLE table you can edit).
  4. It writes a ready-to-fill comparison sheet to outputs/homework_comparison.md.

Run:
    python solutions/day2_models_and_embeddings/homework_pack.py
    python solutions/day2_models_and_embeddings/homework_pack.py --query Q3

Fair-test rules (also in the sheet):
  * Use a NEW chat for each tool so earlier messages do not influence the answer.
  * Paste the identical text. Do not tweak the wording for one tool.
  * Use only the synthetic text from this lab. No real customer, employee or company data.
  * Note the model name and plan the app shows (free/paid tiers can change the model).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # run from any folder

from common import config  # noqa: E402
from solutions.day2_models_and_embeddings.compare_tiers_cli import load_query  # noqa: E402
from solutions.day2_models_and_embeddings.redact_pii import redact  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "data"
TOOLS = ["ChatGPT", "Claude.ai", "Gemini"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare the consumer-chat comparison homework")
    parser.add_argument("--query", default="Q1", help="query id from data/queries.json (default Q1)")
    args = parser.parse_args()

    query = load_query(args.query)
    prompt = query["prompt"]

    print(f"HOMEWORK QUERY {query['id']}: {query['title']}\n")
    print("=" * 70 + "\nCOPY EVERYTHING BETWEEN THE LINES INTO EACH TOOL (new chat each time)\n" + "=" * 70)
    print(prompt)
    print("=" * 70)

    _, found = redact(prompt)
    print(f"\nPII check on this prompt: {found or 'nothing recognised'}  (the text is synthetic, so this is expected to be clean)")

    tools_info = json.loads((DATA_DIR / "approved_tools.json").read_text(encoding="utf-8"))
    print("\nApproved-tools guidance (EXAMPLE table - confirm with your own organisation's policy):")
    for row in tools_info["tools"]:
        print(f"  - {row['tool']} [{row['account']}] -> {row['allowed_data']}")

    lines = [f"# Homework comparison - {query['id']}: {query['title']}", "",
             "## Fair-test rules",
             "- New chat for each tool; identical pasted text; synthetic data only.",
             "- Record the model name and plan each app shows.", "",
             "## Prompt used", "```", prompt, "```", ""]
    if query.get("expected_facts"):
        lines += ["## Reference answer (check yours against this)"] + [f"- {f}" for f in query["expected_facts"]] + [""]
    lines += ["## Results", "",
              "| Question | " + " | ".join(TOOLS) + " |", "|---|" + "---|" * len(TOOLS),
              "| Model / plan shown in the app | " + " | ".join(" " for _ in TOOLS) + " |",
              "| Credit amount correct (620.00)? | " + " | ".join(" " for _ in TOOLS) + " |",
              "| Termination charge correct (24,800)? | " + " | ".join(" " for _ in TOOLS) + " |",
              "| Quoted clause 11.4 for the data question? | " + " | ".join(" " for _ in TOOLS) + " |",
              "| Stayed under 150 words? | " + " | ".join(" " for _ in TOOLS) + " |",
              "| Time to answer (seconds, roughly) | " + " | ".join(" " for _ in TOOLS) + " |",
              "| Did it add anything NOT in the clauses? | " + " | ".join(" " for _ in TOOLS) + " |", "",
              "## Privacy settings check (do this once per tool)",
              "- Where is the setting that controls whether chats are used to improve the model? Is it on or off by default?",
              "- Is the account personal/free or enterprise? What does that change about what you may paste?", "",
              "## Reflection (3-5 sentences)",
              "Which answer would you trust without checking, and why? What would you verify first?", ""]
    path = config.output_dir() / "homework_comparison.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nComparison sheet saved: {path}")
    print("Fill it in, then bring it to the next session.")


if __name__ == "__main__":
    main()
