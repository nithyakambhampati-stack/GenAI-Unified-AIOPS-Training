# GenAI Ops training - assignments

Take-home and unguided-session assignments, organised **week → day**. Each day folder is a complete, runnable copy of
that day's course repository with my changes on top, so `python -m unittest discover -s tests` works inside it.

```
week1/
├── day1/   automation-to-agentic spectrum        write-up: day1/docs/Day1_Writeup.md   guide: day1/README_DAY1.md
├── day2/   model tiers, embeddings, verification  write-up: day2/docs/Day2_Writeup.md   guide: day2/README_DAY2.md
└── day3/   vector mathematics, cosine similarity  write-up: day3/docs/Day3_Writeup.md   guide: day3/README_DAY3.md
```

| Day | Course repo | My choices |
|---|---|---|
| 1 | digibhatia/automation-to-agentic-spectrum | Part A: employee IT access requests. Part B: 14-day damage-report window. Part C: forged tool-result and foreign-language injections; reply check (rule 8) as the code-level control |
| 2 | digibhatia/automation-to-agentic-spectrum | Part B: term-deposit premature-closure query. Part C: `facilities` topic. Part D: 1.5% late interest plus a right-clause check |
| 3 | digibhatia/cosine-vector-mathematics | Task C: Scenario 5, legacy modernization copilot. Task E: "retire" vs "keep" a legacy job |

| Day | Tests | Status |
|---|---|---|
| 1 | 69 OK | Live runs for Levels 2-5 pending (API key) |
| 2 | 66 OK, 1 skipped | Tier runs (API key) and consumer-app comparison (by hand) pending |
| 3 | 15/16 (the one failure needs the starter stubs, see write-up) | Complete except the photo of handwritten working |

**Hygiene:** all data is synthetic. No `.env`, API key, `.venv` or real customer, employee or company data is in this
repository; `.env.example` files hold a placeholder only.
