"""Fill a prompt with each case and run it through Claude Code (or save it for manual runs).

Usage:
  python runner.py --task t1 --variant weak            # uses config.json "runner" (claude)
  python runner.py --task t2 --variant improved --mode manual

Modes
  claude  calls `claude -p` with the filled prompt on stdin, using your own Claude Code login.
  manual  writes each filled prompt to <case>_r<n>.prompt.md; paste it into Claude Code and save
          the answer as <case>_r<n>.txt in the same folder, then run compare.py.

Before anything is sent to the model, card and account numbers in the case are masked so that
only the last 4 digits remain (for example 'XXXX XXXX XXXX 4444').
"""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASK_DATA = {"t1": "data/complaints.json", "t2": "data/reply_cases.json", "t3": "data/policy_snippets.json"}
TASK_FILE = {"t1": "t1_classify.md", "t2": "t2_reply.md", "t3": "t3_summary.md"}


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def mask_pii(text):
    """Mask card and account numbers, keeping only the last 4 digits."""
    return re.sub(r"\b\d{8,15}(\d{4})\b", lambda m: "X" * (len(m.group(0)) - 4) + m.group(1), text)


def case_input(task, case):
    """The text that replaces {{INPUT}}: the case without its answer label."""
    visible = {k: v for k, v in case.items() if k != "label"}
    return mask_pii(json.dumps(visible, indent=2, ensure_ascii=False))


def examples_block():
    """Few-shot examples for {{EXAMPLES}}, one Input/Output pair per example."""
    lines = []
    for i, ex in enumerate(load("data/fewshot_examples.json"), 1):
        lines += [f"Example {i}", f"Input: {mask_pii(ex['text'])}", f"Output: {json.dumps(ex['label'])}", ""]
    return "\n".join(lines).strip()


def fill(template, task, case):
    """Replace {{EXAMPLES}} and {{INPUT}} in the prompt template."""
    out = template.replace("{{EXAMPLES}}", examples_block() if "{{EXAMPLES}}" in template else "")
    return out.replace("{{INPUT}}", case_input(task, case))


def out_dir(task, variant):
    return ROOT / "outputs" / task / variant


def run_claude(prompt, timeout):
    if shutil.which("claude") is None:
        raise RuntimeError("claude is not on your PATH: use --mode manual")
    res = subprocess.run(["claude", "-p"], input=prompt, capture_output=True, text=True, timeout=timeout)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or "claude -p failed")
    return res.stdout.strip()


def main():
    cfg = load("config.json")
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=list(TASK_DATA), required=True)
    ap.add_argument("--variant", choices=["weak", "improved"], required=True)
    ap.add_argument("--mode", choices=["claude", "manual"], default=cfg["runner"])
    args = ap.parse_args()

    template_path = ROOT / "prompts" / args.variant / TASK_FILE[args.task]
    if not template_path.exists():
        raise SystemExit(f"{template_path.relative_to(ROOT)} does not exist yet")
    template = template_path.read_text(encoding="utf-8")
    folder = out_dir(args.task, args.variant)
    folder.mkdir(parents=True, exist_ok=True)

    for case in load(TASK_DATA[args.task]):
        for r in range(1, cfg["repeats"] + 1):
            prompt = fill(template, args.task, case)
            stem = f"{case['id']}_r{r}"
            if args.mode == "manual":
                (folder / f"{stem}.prompt.md").write_text(prompt, encoding="utf-8")
                print(f"wrote {folder.relative_to(ROOT)}/{stem}.prompt.md -> save the answer as {stem}.txt")
                continue
            print(f"running {args.task}/{args.variant} {stem} ...", flush=True)
            (folder / f"{stem}.txt").write_text(run_claude(prompt, cfg["timeout_seconds"]), encoding="utf-8")


if __name__ == "__main__":
    main()
