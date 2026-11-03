"""Check a prompt against the Good-Prompt Formula.

Usage: python prompt_lint.py prompts/weak/*.md
"""
import re
import sys
from pathlib import Path

INGREDIENTS = {
    "context": ("context",),
    "constraints": ("constraints",),
    "priority": ("priority", "weightage"),
    "output": ("output", "desired output"),
}


def lint(prompt_text):  # M4
    """Return what the prompt contains:

    {"context": bool, "constraints": bool, "priority": bool, "output": bool,
     "shots": "zero-shot" | "one-shot" | "few-shot", "role": bool, "persona": bool, "score": int}

    Rules (the linter is strict on purpose: an ingredient counts only if it is explicit):
    - An ingredient is present when a markdown heading line (one or more '#') starts with one of its
      names in INGREDIENTS (any case), AND at least one non-empty line follows it before the next
      heading. HTML comment lines (<!-- ... -->) do not count as content.
    - shots: count lines starting with 'Input:' (any case). 0 -> zero-shot, 1 -> one-shot, 2 or more
      -> few-shot. The placeholder {{EXAMPLES}} counts as few-shot (examples are inserted at run time).
    - role: some line starts with 'You are' (any case).
    - persona: some line starts with 'Persona:' or a heading starts with 'Persona' (any case).
    - score: how many of the four ingredients are present (0 to 4).
    """
    lines = prompt_text.splitlines()
    headings = re.compile(r"^\s*#+\s*(.+?)\s*$")
    found = {}
    current = None
    content = []

    def finish():
        if current is not None:
            found[current] = any(
                line.strip() and not line.lstrip().startswith("<!--")
                for line in content
            )

    for line in lines:
        match = headings.match(line)
        if match:
            finish()
            title = match.group(1).lower()
            current = next(
                (name for name, aliases in INGREDIENTS.items()
                 if any(title.startswith(alias) for alias in aliases)),
                None,
            )
            content = []
        elif current is not None:
            content.append(line)
    finish()

    inputs = sum(bool(re.match(r"^\s*input:", line, re.I)) for line in lines)
    shots = "few-shot" if "{{EXAMPLES}}" in prompt_text or inputs >= 2 else (
        "one-shot" if inputs == 1 else "zero-shot"
    )
    role = any(re.match(r"^\s*You are\b", line, re.I) for line in lines)
    persona = any(
        re.match(r"^\s*Persona:", line, re.I) or
        re.match(r"^\s*#+\s*Persona\b", line, re.I)
        for line in lines
    )
    result = {name: found.get(name, False) for name in INGREDIENTS}
    result.update({"shots": shots, "role": role, "persona": persona})
    result["score"] = sum(result[name] for name in INGREDIENTS)
    return result


def main(paths):
    for p in paths:
        try:
            r = lint(Path(p).read_text(encoding="utf-8"))
        except NotImplementedError as e:
            raise SystemExit(str(e))
        have = [k for k in INGREDIENTS if r[k]]
        missing = [k for k in INGREDIENTS if not r[k]]
        print(f"{p}: {r['score']}/4  has {have or '-'}  missing {missing or '-'}  "
              f"{r['shots']}  role={r['role']}  persona={r['persona']}")


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(str(p) for p in Path(__file__).resolve().parent.glob("prompts/*/*.md")))
