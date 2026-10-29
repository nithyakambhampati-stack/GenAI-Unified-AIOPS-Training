"""
Context window vs prompt, and tokens vs words
=============================================
Two ideas that explain most "why did the model forget / why is it expensive" questions.

  TOKEN          The unit a model reads and bills in: a piece of text, often part of a
                 word. Roughly 4 characters or 3/4 of an English word - but NOT constant.
                 Code, numbers and non-English text usually need MORE tokens per word.

  PROMPT         What you send in one request (instructions + data + question).

  CONTEXT WINDOW The maximum total tokens the model can consider at once: everything it
                 is given PLUS what it writes back. Anything outside it simply does not
                 exist for the model. In an agent loop the history grows every step, so
                 the window fills up and every step costs more.

  CHUNK          A slice of a large document sized to fit (and to be searched). Day 2
                 builds on this with embeddings and vector search.

Run:
    python solutions/day1_ai_spectrum/context_and_tokens.py            # offline estimate
    python solutions/day1_ai_spectrum/context_and_tokens.py --exact    # exact counts from the API

The offline mode needs no API key. The window sizes below are ILLUSTRATIVE; check the
current limits for your chosen model in the Anthropic documentation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # run from any folder

from common import config, llm  # noqa: E402
from solutions.day1_ai_spectrum import dispute_tools as dt  # noqa: E402

# Illustrative window sizes (tokens) for the "how full is it?" table.
WINDOWS = {"small (8k)": 8_000, "standard (200k)": 200_000}

# Samples chosen to show that tokens-per-word is not constant.
SAMPLES = {
    "plain English": "Please refund my order because it arrived late and the box was damaged.",
    "order id + numbers": "ORD-1003 amount 420.00 delivered 2026-10-14 promised 2026-10-02",
    "Python code": "def evaluate(ticket_email, order):\n    return order['amount'] > 100.0",
    "Hindi (Devanagari)": "कृपया मेरा ऑर्डर वापस कर दीजिए क्योंकि वह देर से पहुंचा।",
}


class Counter:
    """Count tokens exactly (API) or approximately (offline rule of thumb)."""

    def __init__(self, exact: bool):
        self.exact = exact

    def __call__(self, text: str) -> int:
        return llm.count_tokens(text) if self.exact else llm.estimate_tokens(text)

    @property
    def label(self) -> str:
        return "exact (API)" if self.exact else "estimate (~4 chars/token)"


def part_a_tokens_vs_words(count: Counter) -> None:
    print(f"\nA. TOKENS vs WORDS  [{count.label}]")
    print(f"{'sample':<22}{'words':>7}{'chars':>7}{'tokens':>8}{'tok/word':>10}")
    for name, text in SAMPLES.items():
        words = len(text.split())
        tokens = count(text)
        print(f"{name:<22}{words:>7}{len(text):>7}{tokens:>8}{tokens / words:>10.2f}")
    if not count.exact:
        print("  (offline estimates ignore script differences; run with --exact to see Hindi and code cost more)")


def part_b_context_budget(count: Counter) -> None:
    """How much of a window does 'give the agent everything' use?"""
    orders, tickets, policy = dt.load_orders(), dt.load_tickets(), dt.policy_text()
    pieces = {
        "system prompt (Level 5)": 220 if not count.exact else count(
            "You are an autonomous support operations agent for a retailer. " * 6),
        "policy": count(policy),
        "all orders (JSON)": count(json.dumps(list(orders.values()))),
        "all tickets (JSON)": count(json.dumps(tickets)),
    }
    total = sum(pieces.values())
    print(f"\nB. CONTEXT BUDGET for the toy dataset  [{count.label}]")
    for name, tokens in pieces.items():
        print(f"  {name:<26}{tokens:>7} tokens")
    print(f"  {'TOTAL':<26}{total:>7} tokens")
    for label, size in WINDOWS.items():
        print(f"  fills {total / size:6.1%} of the {label} window")
    scale = 100_000
    print(f"\n  Scale it: 8 tickets -> {scale:,} tickets is about {total * scale // 8:,} tokens of ticket+order data.")
    print("  That does not fit in any window - so real systems RETRIEVE only what is relevant (Day 2).")


def part_c_agent_growth(count: Counter) -> None:
    """In an agent loop every step re-sends the whole history, so input tokens grow."""
    step_cost = 350  # rough tokens added per tool call + result (illustrative)
    base = count(dt.policy_text()) + 220
    print("\nC. AGENT LOOP: the history is re-sent on EVERY step")
    print(f"{'step':>5}{'input tokens this call':>26}{'running total billed':>24}")
    running = 0
    for step in range(1, 9):
        this_call = base + step_cost * (step - 1)
        running += this_call
        print(f"{step:>5}{this_call:>26,}{running:>24,}")
    print("  Cost grows faster than the number of steps. That is why step budgets matter (Level 5).")


def part_d_chunking(count: Counter) -> None:
    """Split the policy into small chunks - the first step of 'retrieval' (Day 2)."""
    chunks = [line.strip() for line in dt.policy_text().splitlines() if line.strip().startswith(tuple("1234567"))]
    print(f"\nD. CHUNKING the policy into {len(chunks)} pieces (one rule each)  [{count.label}]")
    for i, chunk in enumerate(chunks, 1):
        print(f"  chunk {i}: {count(chunk):>4} tokens  | {chunk[:70]}...")
    print("  Retrieval sends the 1-2 relevant chunks instead of the whole document.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tokens, words and context windows")
    parser.add_argument("--exact", action="store_true", help="use the API for exact token counts (needs a key)")
    args = parser.parse_args()

    if args.exact and not config.get_api_key():
        print("--exact needs ANTHROPIC_API_KEY in .env. Running the offline estimate instead.")
        args.exact = False

    count = Counter(args.exact)
    part_a_tokens_vs_words(count)
    part_b_context_budget(count)
    part_c_agent_growth(count)
    part_d_chunking(count)


if __name__ == "__main__":
    main()
