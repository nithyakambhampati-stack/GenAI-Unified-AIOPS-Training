"""
run_experiment.py - BEFORE (one weak prompt, whole SOP pasted in) versus AFTER (your prompt chain), on the same questions.

    python run_experiment.py --mock     simulated model, no key needed
    python run_experiment.py --live     real Claude through the Claude Code CLI
Writes results/before_after.csv and results/report.md.
"""
import argparse
import csv
import json
from pathlib import Path

from chain import render_template, run_chain
from doc_store import load_sections
from evaluate import CFG, RUBRIC, SECTIONS, score
from llm_client import ask

ROOT = Path(__file__).resolve().parent


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def run(mock):
    qs = json.loads(read("data/questions.json"))
    examples = json.loads(read("data/examples.json"))
    system, template = read(CFG["prompts"]["system_message"]), read(CFG["prompts"]["extract"])
    weak = read(CFG["prompts"]["weak"])
    whole = "\n\n".join(f"[{s['id']}] {s['title']}\n{s['text']}" for s in SECTIONS)
    rows = []
    for q in qs:
        out = ask(render_template(weak, {"context": whole, "question": q["question"]}), q, mock=mock)          # BEFORE
        rows.append(row("before", q, out))
        res = run_chain(q["question"], SECTIONS, lambda p, c: ask(p, c, mock=mock), system, template, examples, CFG, case=q)   # AFTER
        final = json.dumps({k: res[k] for k in ("answer", "citations", "confidence")})
        rows.append(row("after", q, final, res["attempts"]))
    return rows


def row(version, q, out, attempts=1):
    s = score(out, q)
    return dict(version=version, question=q["id"], score=s["score"], safety=s["by_dimension"]["safety"], grounding=s["by_dimension"]["grounding"],
                accuracy=s["by_dimension"]["accuracy"], format=s["by_dimension"]["format"], attempts=attempts, failed="; ".join(s["failed"]), output=out.replace("\n", " ")[:240])


def summarise(rows):
    """Average score per version: {"before": x, "after": y}."""
    acc = {}
    for r in rows:
        acc.setdefault(r["version"], []).append(r["score"])
    return {k: round(sum(v) / len(v), 1) for k, v in acc.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    rows = run(mock=not args.live)
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with open(out / "before_after.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    avg = summarise(rows)
    dims = ["safety", "grounding", "accuracy", "format"]
    lines = ["# Before and after (average score out of 100)", "", "| | Before (one weak prompt) | After (your chain) |", "|---|---|---|", f"| Overall | {avg['before']} | {avg['after']} |"]
    for d in dims:
        b = round(100 * sum(r[d] for r in rows if r["version"] == "before") / len([r for r in rows if r["version"] == "before"]), 1)
        a = round(100 * sum(r[d] for r in rows if r["version"] == "after") / len([r for r in rows if r["version"] == "after"]), 1)
        lines.append(f"| {d} | {b} | {a} |")
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("Wrote results/before_after.csv and results/report.md")


if __name__ == "__main__":
    main()
