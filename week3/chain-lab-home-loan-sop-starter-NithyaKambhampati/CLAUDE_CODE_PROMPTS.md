# Using Claude Code well in this lab

Start `claude` in this folder. You are the engineer; Claude Code is the assistant. After EVERY answer: read it, run it, check it.

## Good uses
```
Read prompts/weak_single.txt and compare it with the chain steps (guard, retrieve, extract, verify, refine, render). List what is missing. Do NOT rewrite the prompt.
```
```
Here is my draft prompt and the output it produced for question Q08. List every rule from data/policy.json that the output
breaks, and which ingredient of my prompt should have prevented it. Do not rewrite the prompt.
```
```
Open doc_store.py. Implement the function marked TODO (missing piece M1) from its docstring and comments only.
Standard library only. Then explain your code line by line.
```
```
Read config.json, data/rubric.json, data/examples.json and README.md. List every place where two of them disagree about the same
fact (numbers, orders, names). Show file and value for each. Do not fix anything yet.
```
```
Write five unittest cases for evaluate.py, including edge cases (empty answer, a quote with extra spaces, an unknown section).
Run them and tell me which fail and why.
```

## Habits that matter
* Ask for a critique before you ask for a rewrite; you learn more and own the result.
* Change one ingredient at a time, rerun, and note the effect.
* A confident answer is not a correct one. The tests and the evaluator are the judges.


## Extra for this lab
```
Here is a question and the JSON my assistant returned. Check each citation against data/sop.txt and tell me which are not word for word. Do not fix anything.
```
```
Suggest five injected sentences that my injection.py patterns would MISS. Do not change the code. I will decide which defence to add.
```
