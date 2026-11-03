# Day 9 Assignment Understanding

## Purpose

This lab improves three unreliable prompts used by a retail bank complaint desk. The goal is to make each prompt explicit, testable, and aligned with the Good-Prompt Formula, then compare the weak and improved versions.

All case data is synthetic. Before a case is sent to a model, card and account numbers are masked so that only the last four digits remain visible.

## Good-Prompt Formula

Every improved prompt has four markdown sections:

- **Context** explains who uses the answer, what task is being performed, and what the input contains.
- **Constraints** states rules that must not be broken, including allowed values, limits, privacy rules, and grounding requirements.
- **Priority** states what wins when rules conflict. The desk uses compliance first, accuracy second, and brevity third.
- **Output** defines the exact response format.

The linter is intentionally strict. A section counts only when its name appears in a markdown heading and has real non-comment content before the next heading.

## Prompt Strategies

### t1: Complaint classification

`prompts/improved/t1_classify.md` uses few-shot prompting. The runner inserts examples from `data/fewshot_examples.json` into `{{EXAMPLES}}`, then inserts one complaint into `{{INPUT}}`. The model must return only JSON containing `category`, `severity`, and `escalate`.

Examples make the classification labels concrete and reduce ambiguity around fraud, severity, and escalation decisions.

### t2: Customer reply

`prompts/improved/t2_reply.md` uses a role and persona. The assistant acts as a retail bank complaint-desk officer with the persona of Asha, a calm, precise, and empathetic senior customer care officer. The reply must be no more than 120 words, include the complaint reference and timeline, avoid forbidden certainty phrases, and never expose a full card or account number.

### t3: Policy summary

`prompts/improved/t3_summary.md` uses zero-shot prompting with a strict JSON contract. The model must summarize only the supplied policy text and return `one_line_answer`, `fee_or_limit`, `applies_to`, and `source_id`. All numbers in the response must come from the policy text.

## Scoring

The checks in `checks.py` score each model output by boolean checks:

- **t1:** valid JSON, allowed category, correct category, severity, and escalation value.
- **t2:** word limit, no forbidden phrase, complaint reference, timeline, and no full card number.
- **t3:** valid JSON, required fields, correct source id, and grounded numbers.

The score for one case is the fraction of checks that pass. `compare.py` averages these scores by task and prompt variant and writes `output/comparison.csv` and `output/comparison.md`.

## Completed Work

- Added all three improved prompts.
- Implemented the strict prompt linter.
- Implemented comparison scoring and report generation.
- Fixed data/config inconsistencies: repeat count, priority order, allowed category, duplicate complaint id, and misleading few-shot label.
- Made classification checks case-insensitive as documented.
- Normalized comma-formatted numbers without treating digits inside identifiers such as `C31` as policy numbers.
- Completed the six worksheet answers.
- Added regression and data-hygiene tests in `tests/test_lab.py`.

## Verification

Run:

```text
python -m unittest discover -s tests
python check_by_hand.py
python prompt_lint.py
python compare.py
```

The test suite currently passes all 20 tests, and all 42 worksheet answers match the linter. The comparison report records missing model outputs until weak and improved runs are generated through Claude Code or manual mode.

## Repository Status

This folder is the complete Day 9 assignment. It is ready to be reviewed before publishing to GitHub, and later to GitLab after confirmation.