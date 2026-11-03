"""Before/after comparison: score every saved output for the weak and the improved prompts.

Reads outputs/<variant>/<task>/<case_id>_r<n>.txt, scores each with checks.py, and writes
output/comparison.csv (one row per task, variant, case and run) and output/comparison.md
(average score per task and variant, the improvement in points, and the lint score of each prompt).
"""
import csv  # noqa: F401
import json
from pathlib import Path

import checks  # noqa: F401
from prompt_lint import lint  # noqa: F401

ROOT = Path(__file__).resolve().parent
TASKS = {"t1": ("data/complaints.json", "t1_classify.md"),
         "t2": ("data/reply_cases.json", "t2_reply.md"),
         "t3": ("data/policy_snippets.json", "t3_summary.md")}
VARIANTS = ["weak", "improved"]


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main():  # M5
    """For each task and variant:
      - load every saved output for every case and run,
      - score it with the right check (t1 check_classification against the case label,
        t2 check_reply against the case, t3 check_summary against the snippet),
      - average the case scores, and count missing outputs.
    Print a table: task | weak score | improved score | improvement in points | lint weak | lint improved.
    Write output/comparison.csv and output/comparison.md.
    """
    cfg = load("config.json")
    rows = []
    averages = {}
    for task, (data_path, prompt_name) in TASKS.items():
      cases = load(data_path)
      for variant in VARIANTS:
        scores = []
        missing = 0
        for case in cases:
          for run in range(1, cfg["repeats"] + 1):
            path = ROOT / "outputs" / task / variant / f"{case['id']}_r{run}.txt"
            if not path.exists():
              missing += 1
              rows.append({"task": task, "variant": variant, "case_id": case["id"],
                     "run": run, "score": "", "missing": 1})
              continue
            output = path.read_text(encoding="utf-8")
            if task == "t1":
              result = checks.check_classification(output, case["label"], cfg)
            elif task == "t2":
              result = checks.check_reply(output, case, cfg)
            else:
              result = checks.check_summary(output, case, cfg)
            case_score = checks.score(result)
            scores.append(case_score)
            rows.append({"task": task, "variant": variant, "case_id": case["id"],
                   "run": run, "score": f"{case_score:.4f}", "missing": ""})
        averages[(task, variant)] = sum(scores) / len(scores) if scores else 0.0

    output_dir = ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    with (output_dir / "comparison.csv").open("w", newline="", encoding="utf-8") as handle:
      writer = csv.DictWriter(handle, fieldnames=["task", "variant", "case_id", "run", "score", "missing"])
      writer.writeheader()
      writer.writerows(rows)

    lines = ["# Before/after comparison", "", "| Task | Weak | Improved | Improvement | Lint weak | Lint improved |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    print(f"Comparing {', '.join(VARIANTS)} over tasks {', '.join(TASKS)} (repeats = {cfg['repeats']})")
    for task, (_, prompt_name) in TASKS.items():
      weak = averages[(task, "weak")]
      improved = averages[(task, "improved")]
      weak_lint = lint((ROOT / "prompts" / "weak" / prompt_name).read_text(encoding="utf-8"))["score"]
      improved_lint = lint((ROOT / "prompts" / "improved" / prompt_name).read_text(encoding="utf-8"))["score"]
      print(f"{task} | {weak:.3f} | {improved:.3f} | {improved - weak:+.3f} | {weak_lint}/4 | {improved_lint}/4")
      lines.append(f"| {task} | {weak:.3f} | {improved:.3f} | {improved - weak:+.3f} | {weak_lint}/4 | {improved_lint}/4 |")
    (output_dir / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
