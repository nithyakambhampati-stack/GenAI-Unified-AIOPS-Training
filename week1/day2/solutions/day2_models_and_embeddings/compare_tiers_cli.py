"""
In-lab exercise: compare Claude model tiers (Opus / Sonnet / Haiku) with Claude Code CLI
=========================================================================================
Send the SAME query to each tier through the Claude Code command line and compare:
quality of the answer, speed, tokens and cost.

How it talks to Claude Code
---------------------------
It runs this command once per tier (the prompt is piped in on stdin):

    claude -p --model <tier> --output-format json --max-turns 1 --tools ""

    -p                    "print" mode: answer once and exit (non-interactive)
    --model               opus | sonnet | haiku (aliases) or a full model ID
    --output-format json  machine-readable reply: answer text, cost, tokens, duration
    --max-turns 1         no multi-step loops - one answer
    --tools ""            no tools: a pure "model only" comparison (fair test)

The CLI does not read this project's .env file, so this script passes the key to the
child process through its environment (the key is never printed).

Run:
    python solutions/day2_models_and_embeddings/compare_tiers_cli.py                 # query Q1, all tiers
    python solutions/day2_models_and_embeddings/compare_tiers_cli.py --query Q3
    python solutions/day2_models_and_embeddings/compare_tiers_cli.py --tiers haiku,sonnet
    python solutions/day2_models_and_embeddings/compare_tiers_cli.py --prompt "your own question"
    python solutions/day2_models_and_embeddings/compare_tiers_cli.py --dry-run      # show commands only

A markdown report is saved in outputs/ so you can paste it into your lab notes.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # run from any folder

from common import config  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "data"


def load_query(query_id: str) -> dict:
    """Find a query by id (Q1, Q2, Q3) in data/queries.json and fill in its document."""
    spec = json.loads((DATA_DIR / "queries.json").read_text(encoding="utf-8"))
    candidates = [spec["primary"], *spec["extra"]]
    for item in candidates:
        if item["id"].lower() == query_id.lower():
            document = ""
            if item.get("document_file"):
                document = (DATA_DIR / item["document_file"]).read_text(encoding="utf-8")
            prompt = item["prompt_template"].replace("{document}", document)
            return {**item, "prompt": prompt}
    raise SystemExit(f"Unknown query {query_id!r}. Choose from: {', '.join(c['id'] for c in candidates)}")


def build_command(claude_path: str, model: str) -> list[str]:
    """The exact command line used for one tier (also shown by --dry-run)."""
    return [claude_path, "-p", "--model", model, "--output-format", "json", "--max-turns", "1", "--tools", ""]


def run_cli(prompt: str, model: str, timeout: int) -> dict:
    """
    Run Claude Code once and return a flat dict:
        ok, answer, seconds, cost_usd, input_tokens, output_tokens, served_by, error
    Never raises for ordinary failures - a failed tier is reported in the table instead.
    """
    claude_path = shutil.which("claude")
    if not claude_path:
        return {"ok": False, "error": "claude command not found - open a NEW terminal after installing"}

    env = dict(os.environ)
    key = config.get_api_key()
    if key:
        env["ANTHROPIC_API_KEY"] = key  # the CLI reads the key from the environment, not from .env

    try:
        proc = subprocess.run(
            build_command(claude_path, model),
            input=prompt,                 # prompt goes in on stdin (safe for long text and quotes)
            capture_output=True, text=True, timeout=timeout, env=env,
            cwd=str(config.output_dir()),  # neutral folder: do not let the CLI pick up repo files as context
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"timed out after {timeout}s"}

    if proc.returncode != 0:
        return {"ok": False, "error": (proc.stderr or proc.stdout).strip()[:300]}
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "CLI did not return JSON: " + proc.stdout[:200]}
    if data.get("is_error"):
        return {"ok": False, "error": str(data.get("result", "unknown error"))[:300]}

    usage = data.get("usage", {})
    served_by = ", ".join((data.get("modelUsage") or {}).keys()) or "unknown"  # the REAL model that answered
    return {
        "ok": True,
        "answer": str(data.get("result", "")).strip(),
        "seconds": round((data.get("duration_ms") or 0) / 1000, 1),
        "cost_usd": data.get("total_cost_usd"),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "served_by": served_by,
    }


def auto_check(answer: str, numbers: list[str]) -> str:
    """Crude automatic check: does the answer contain the key numbers? (Humans still judge quality.)"""
    if not numbers:
        return "n/a"
    hits = [n for n in numbers if n in answer]
    return f"{len(hits)}/{len(numbers)} key numbers"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Claude tiers via Claude Code CLI")
    parser.add_argument("--query", default="Q1", help="query id from data/queries.json (default Q1)")
    parser.add_argument("--prompt", help="use your own prompt instead of a prepared query")
    parser.add_argument("--tiers", default="opus,sonnet,haiku", help="comma-separated tiers (default: opus,sonnet,haiku)")
    parser.add_argument("--dry-run", action="store_true", help="print the commands without calling the model")
    parser.add_argument("--timeout", type=int, default=config.CLI_TIMEOUT_SECONDS)
    args = parser.parse_args()

    if args.prompt:
        query = {"id": "custom", "title": "Custom prompt", "prompt": args.prompt, "check_numbers": []}
    else:
        query = load_query(args.query)
    tiers = [t.strip() for t in args.tiers.split(",") if t.strip()]
    for tier in tiers:
        if tier not in config.CLI_TIERS:
            raise SystemExit(f"Unknown tier {tier!r}. Choose from: {', '.join(config.CLI_TIERS)}")

    print(f"Query {query['id']}: {query['title']}\n")
    if args.dry_run:
        for tier in tiers:
            print("DRY RUN:", " ".join(f'"{p}"' if p == "" else p for p in build_command("claude", config.CLI_TIERS[tier])), " < prompt")
        print("\nPrompt that would be sent:\n" + query["prompt"])
        return

    results: dict[str, dict] = {}
    for tier in tiers:
        print(f"Running {tier} ...", flush=True)
        results[tier] = run_cli(query["prompt"], config.CLI_TIERS[tier], args.timeout)

    # ---- Console table -------------------------------------------------------------------
    print(f"\n{'tier':<8}{'ok':<5}{'secs':>6}{'cost $':>10}{'in/out tokens':>16}  {'key numbers':<18}served by")
    print("-" * 90)
    for tier, r in results.items():
        if r["ok"]:
            tokens = f"{r['input_tokens']}/{r['output_tokens']}"
            cost = f"{r['cost_usd']:.4f}" if r["cost_usd"] is not None else "-"
            print(f"{tier:<8}{'yes':<5}{r['seconds']:>6}{cost:>10}{tokens:>16}  "
                  f"{auto_check(r['answer'], query.get('check_numbers', [])):<18}{r['served_by']}")
        else:
            print(f"{tier:<8}{'NO':<5}  {r['error']}")

    # ---- Markdown report ---------------------------------------------------------------------
    lines = [f"# Tier comparison - {query['id']}: {query['title']}", "", "## Prompt", "```", query["prompt"], "```", ""]
    if query.get("expected_facts"):
        lines += ["## Reference answer (for the human judge)"] + [f"- {f}" for f in query["expected_facts"]] + [""]
    for tier, r in results.items():
        lines += [f"## {tier}", ""]
        if r["ok"]:
            cost = f"{r['cost_usd']:.4f}" if r["cost_usd"] is not None else "n/a"
            lines += [f"*{r['seconds']}s, cost ${cost}, tokens in/out {r['input_tokens']}/{r['output_tokens']}, "
                      f"served by {r['served_by']}*", "", r["answer"], ""]
        else:
            lines += [f"FAILED: {r['error']}", ""]
    lines += ["## Your scoring (fill in)", "", "| Tier | Correct? (0-3) | Followed length limit? | Would you trust it unchecked? |",
              "|---|---|---|---|"] + [f"| {t} |  |  |  |" for t in tiers]
    path = config.output_dir() / f"tier_comparison_{query['id']}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nReport saved: {path}")
    print("Discuss: Is the most expensive tier always worth it? Which tier would you use for this task in production?")


if __name__ == "__main__":
    main()
