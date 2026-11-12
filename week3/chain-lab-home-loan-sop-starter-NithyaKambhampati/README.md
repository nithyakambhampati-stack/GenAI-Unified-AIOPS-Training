# Prompt Chain Lab: Home Loan Servicing Policy Assistant (Day 13) - STARTER PACKAGE

A bank's home loan servicing team answers borrower questions about prepayment, foreclosure, EMI holidays and document release from a long servicing SOP. Branch staff search the PDF by hand, quote it from memory, and sometimes give the wrong charge or promise something the SOP does not allow. A generic AI prompt answers fast, but it invents rules, cannot show where an answer came from, and can be steered by text hidden in a document or a question.

You will design a **prompt chain** that answers staff questions from an SOP with **structured, cited output**, resist basic **prompt injection**, and write the **system message** for an enterprise assistant persona. Standard library only. Synthetic data only.

**Topics of this lab:** chain-of-thought and tree-of-thought prompting, prompt chaining, structured output (JSON, markdown), prompt injection awareness and basic defence, iterative refinement.

## The chain
```
question -> 1 GUARD -> 2 RETRIEVE -> 3 EXTRACT (model) -> 4 VERIFY -> 5 REFINE (retry) -> 6 RENDER (markdown)
```
Each step does one job. Only step 3 calls the model. Steps 1, 2, 4, 6 are ordinary code you can test.

```
data/sop.txt            the SOP, sections written as [S2.1] Title
data/questions.json     8 questions with the known right answers (one cannot be answered from the SOP; one carries injected text, and the SOP itself carries another in S6.1)
data/policy.json        phrases the assistant must never use
data/rubric.json        scoring dimensions and weights
data/examples.json      two few-shot examples
config.json             retrieval, retries, limits, persona and prompt paths
prompts/weak_single.txt the BEFORE prompt: whole SOP pasted in, one instruction
prompts/system_message.md   YOUR system message for the assistant persona
prompts/extract_template.md YOUR extract prompt (step 3)
CHAIN_DESIGN.md         YOUR design table for the chain
doc_store.py  injection.py  chain.py  llm_client.py  evaluate.py  run_experiment.py
tests/                  some unit tests (not all present)
```

## What the assistant must produce
| Item | Rule |
|---|---|
| Answer | JSON only, with the keys answer, citations, confidence. At most 60 words in answer |
| citations | a list of {"section": "S2.1", "quote": "..."}; the quote is word for word from that section |
| Not in the SOP | the answer is exactly "Not found in the document." and citations is empty |
| Injected text | instructions inside the SOP or the question are data, never obeyed; a promise of approval or waiver is never made |
| Refinement | if verification fails the chain retries once with feedback (one refinement retry) |
| Retrieval | the best 3 sections are sent to the model |

Priority when rules conflict: **safety, grounding, accuracy, format**.

## Run it
1. `python --version` (3.9 or newer). Open this folder in VS Code and open a terminal here.
2. `python -m unittest discover -s tests`
3. `python run_experiment.py --mock`   (simulated model: tests your harness, no key needed)
4. `python run_experiment.py --live`   (real Claude through the Claude Code CLI; this is the result that counts)
Outputs go to `results/before_after.csv` and `results/report.md`.

## About the mock model
The mock is a **simulation** that reacts to features of your prompt. It tests the harness offline. It does **not** prove your prompt works on a real model. Always finish with a live run.

## About this starter package
This copy is **not finished and not fully correct**. Your job:
1. Run everything and **observe** what happens.
2. **List every inconsistency** in `inconsistency_log.md`.
3. **Write the missing pieces** (`TODO (missing piece`, see `MISSING_PIECES.md`), then fix each inconsistency.
4. Write the system message and extract prompt, run before and after, and push to GitLab.

## Rules
* Synthetic data only. No real customer, claim or bank data in files, prompts or screenshots.
* No `.env`, keys or secrets in the repository.
* Change one thing at a time and rerun after each change.
