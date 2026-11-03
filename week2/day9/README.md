# Bank Complaint Desk: Prompt Engineering in Practice (Day 9)

A retail bank's complaint desk uses an AI assistant through three short prompts. The outputs are
unreliable. Your job is to rewrite the three prompts against the Good-Prompt Formula, run them before and
after, and prove the improvement with scores. All data is synthetic.

## The Good-Prompt Formula

Every improved prompt has four explicit sections, each a markdown heading:

1. `## Context`: who the output is for, what the task is, what the input is
2. `## Constraints`: the rules that must never be broken
3. `## Priority`: what wins when two rules pull in different directions
4. `## Output`: the exact format of the answer

Start from `prompts/improved/TEMPLATE.md`.

The desk's priority order, decided by the process owner, is: **compliance first, then accuracy, then brevity**.

## The three tasks

| Task | Weak prompt | Input data | Strategy to use |
| --- | --- | --- | --- |
| t1 classify a complaint | prompts/weak/t1_classify.md | data/complaints.json (10) | few-shot, examples from data/fewshot_examples.json |
| t2 draft a customer reply | prompts/weak/t2_reply.md | data/reply_cases.json (4) | role + persona |
| t3 summarise a policy for an agent | prompts/weak/t3_summary.md | data/policy_snippets.json (4) | zero-shot, strict output |

Placeholders in a prompt: `{{INPUT}}` is replaced by the case, `{{EXAMPLES}}` by the few-shot examples.

## How to run

```
python -m unittest discover -s tests                 # tests
python check_by_hand.py                              # compare by_hand/my_answers.json with the linter
python prompt_lint.py prompts/weak/t1_classify.md prompts/weak/t2_reply.md prompts/weak/t3_summary.md  # which ingredients does each prompt have?
python runner.py --task t1 --variant weak            # run a prompt over every case
python compare.py                                    # before/after scores, writes output/
```

The runner calls Claude Code in print mode (`claude -p`), using your own Claude Code login: no API key
is stored anywhere. If `claude` is not available on your machine, use `--mode manual`: the runner writes
each filled prompt to a file, you paste it into Claude Code, and save the answer next to it.

Every case is run `repeats` times (3), because model output varies between runs.
Outputs are saved to `outputs/<variant>/<task>/<case_id>_r<n>.txt`.

Before any text is sent to the model, card and account numbers are masked (only the last 4 digits kept).

## Scoring (checks.py)

- t1: valid JSON; category, severity and escalate match the label (case-insensitive); category is one of
  the allowed categories.
- t2: at most 150 words; no forbidden phrases; quotes the complaint reference; states the timeline;
  no unmasked card or account number.
- t3: valid JSON with the fields one_line_answer, fee_or_limit, applies_to and sources; the source id
  matches; every number in the answer appears in the policy text.

A case's score is the share of its checks that pass. compare.py averages scores per task and variant.

## Change note

I used few-shot examples for classification because the examples show the expected category, severity and escalation decisions; role plus persona for replies to keep the tone calm while preserving the desk's compliance rules; and zero-shot strict JSON for policy summaries because each policy must be grounded only in its supplied text. The improved prompts still cannot be scored against model behavior until output files are generated with Claude Code or manual runs; `compare.py` reports those missing outputs explicitly.
