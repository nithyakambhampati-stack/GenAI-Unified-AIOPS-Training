# Day 9 Assignment Understanding

## 1. What the Assignment Asked

The bank complaint desk had three weak prompts whose outputs were unreliable. The assignment was to:

1. Read the weak prompts and the synthetic input data.
2. Rewrite the prompts using the Good-Prompt Formula.
3. Implement a strict prompt linter.
4. Score weak and improved outputs.
5. Complete the worksheet and add tests proving the work.
6. Document the results.

The three tasks are complaint classification, customer-reply drafting, and policy summarization.

## 2. How the Files Were Created

The starter folder already contained the weak prompts, data, runner, checker skeletons, worksheet, and tests. The missing files and incomplete functions were identified from `MISSING_PIECES.md`.

The work was completed in these stages:

1. Read `README.md`, `MISSING_PIECES.md`, the worksheet, configuration, data, and existing tests.
2. Copied the prompt template into three improved prompt files and replaced the template comments with task-specific instructions.
3. Implemented `lint()` in `prompt_lint.py` according to its docstring.
4. Implemented `main()` in `compare.py` to read saved outputs, score them, print a table, and write CSV/Markdown reports.
5. Completed `by_hand/my_answers.json` using the strict linter rules.
6. Added `tests/test_lab.py` for the worksheet, improved prompts, fixed checks, and data hygiene.
7. Corrected discovered inconsistencies in configuration, test data, placeholders, and scoring logic.
8. Added this understanding document and copied the completed assignment to the GitHub repository under `week2/day9`.
9. Added `SUBMISSION_NOTES.md` to document the individual design choices in this variant.

## 3. How Each Prompt Was Modified

### t1: Complaint Classification

File: `prompts/improved/t1_classify.md`

Strategy: **few-shot prompting**.

- Context identifies the complaint desk, the classification task, and the complaint input.
- Constraints list the allowed categories, severities, escalation rule, JSON requirement, and no-invention rule.
- Priority states compliance first, accuracy second, and brevity third.
- Output requires only JSON with `category`, `severity`, and `escalate`.
- `{{EXAMPLES}}` receives examples from `data/fewshot_examples.json`.
- `{{INPUT}}` receives the current complaint from `data/complaints.json`.

The examples show the model what the expected labels look like and make similar categories easier to distinguish.

### t2: Customer Reply

File: `prompts/improved/t2_reply.md`

Strategy: **role plus persona**.

- The role is a retail bank complaint-desk officer.
- The persona is Asha, a calm, precise, and empathetic senior customer-care officer.
- Constraints enforce the 120-word limit, complaint reference, timeline, privacy protection, forbidden phrases, and no invented commitments.
- Priority again places compliance before accuracy and brevity.
- Output requires only the customer-facing reply and requires the complaint reference at the end.
- `{{INPUT}}` receives the reply case, including the bank action and timeline.

This makes the reply both professional and operationally complete without exposing sensitive numbers.

### t3: Policy Summary

File: `prompts/improved/t3_summary.md`

Strategy: **zero-shot with strict output**.

- Context identifies the bank agent and says that only the supplied policy may be used.
- Constraints prohibit invented facts and numbers and require the source id to be copied.
- Priority is compliance, accuracy, then brevity.
- Output requires valid JSON with `one_line_answer`, `fee_or_limit`, `applies_to`, and `source_id`.
- `{{INPUT}}` receives one policy snippet and its metadata.

The strict contract makes the summary easy to validate automatically.

## 4. How the Assignment Was Tested

The linter checks whether each ingredient has its own markdown heading with real content. It also detects shot type, role, persona, and the four-ingredient score.

The output checks work as follows:

- **t1:** valid JSON, allowed category, matching category, matching severity, and matching escalation.
- **t2:** word limit, no forbidden phrase, complaint reference, timeline, and no full card number.
- **t3:** valid JSON, required fields, correct source id, and numbers grounded in the policy text.

The runner masks card and account numbers before creating prompts. The comparison script reads output files from both variants and writes:

- `output/comparison.csv`: one row for each task, variant, case, and run.
- `output/comparison.md`: average before/after scores and lint scores.

## 5. Problems Found and Fixed

- Changed `repeats` from 1 to 3 to match the assignment instructions.
- Corrected configuration priority to compliance, accuracy, brevity.
- Added `fees_and_charges` to the allowed categories.
- Renamed the duplicate complaint id `CMP-04` to `CMP-05` so output files cannot overwrite each other.
- Corrected a misleading few-shot card-fraud example.
- Made category and severity comparisons case-insensitive as promised by the checker documentation.
- Normalized comma-formatted numbers and prevented digits inside identifiers such as `C31` from being counted as policy numbers.
- Corrected the weak t3 placeholder from `{{TEXT}}` to the documented `{{INPUT}}`.

## 6. Results

The final verification produced these results:

- **20 tests passed** with `python -m unittest discover -s tests`.
- **42 of 42 worksheet answers matched** with `python check_by_hand.py`.
- All three improved prompts lint at **4/4**.
- t1 is detected as few-shot; t2 is detected as role plus persona; t3 is detected as zero-shot.
- `output/comparison.csv` and `output/comparison.md` were generated successfully.

The comparison scores are currently `0.000` for both weak and improved variants because no Claude Code or manual model-output files were available at test time. The comparison report records those outputs as missing rather than pretending that model runs occurred. After outputs are generated, running `python compare.py` will calculate the real before/after scores.

## 7. Published Location

The completed assignment and this document were pushed to:

`week2/day9` in [GenAI-Unified-AIOPS-Training](https://github.com/nithyakambhampati-stack/GenAI-Unified-AIOPS-Training/tree/main/week2/day9)