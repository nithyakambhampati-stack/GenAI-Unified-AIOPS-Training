"""Compare your paper answers (by_hand/my_answers.json) with what prompt_lint.lint() says.

If they disagree, decide who is wrong: you, the linter, or the rule.
"""
import json
from pathlib import Path

from prompt_lint import lint

ROOT = Path(__file__).resolve().parent
FIELDS = ["context", "constraints", "priority", "output", "shots", "role", "persona"]


def main():
    snippets = json.loads((ROOT / "by_hand" / "snippets.json").read_text(encoding="utf-8"))
    mine = json.loads((ROOT / "by_hand" / "my_answers.json").read_text(encoding="utf-8"))
    ok = total = 0
    for sid, text in snippets.items():
        try:
            code = lint(text)
        except NotImplementedError as e:
            print(f"Cannot check yet: {e}")
            return
        for f in FIELDS:
            total += 1
            good = mine.get(sid, {}).get(f) == code[f]
            ok += good
            if not good:
                print(f"DIFFERS  {sid}.{f:<12} yours={mine.get(sid, {}).get(f)!s:<10} linter={code[f]}")
    print(f"\n{ok} of {total} answers match.")
    if ok == total:
        print("Every answer matches.")


if __name__ == "__main__":
    main()
