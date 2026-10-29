# Day 2 take-home - what is here and how to finish it

Course repo: `https://github.com/digibhatia/automation-to-agentic-spectrum` (full copy, with my changes).
Brief: `docs/assignments/Day2_Take_Home_Assignment.docx`. Write-up: **`docs/Day2_Writeup.md`**.
Part E: **`docs/Approved_Tools_Guideline_DRAFT.md`**.

## Files changed or added

| File | Part | Change |
|---|---|---|
| `solutions/day2_models_and_embeddings/verify_outputs.py` | D | New item `late_interest_pct_month`; rounding fix; whole-number match; unsupported number → HIGH; quote must come from the right clause |
| `solutions/day2_models_and_embeddings/embeddings_map.py` | C | Fix: a 5th topic was silently left off the map; `--query` option |
| `solutions/day2_models_and_embeddings/data/sentences.json` | C | New topic `facilities` (8 sentences) |
| `solutions/day2_models_and_embeddings/data/own_query_term_deposit.txt`, `own_query_answers.md` | B | My query and its reference answers |
| `tests/test_day2.py` | C, D | 11 new tests; one course check relaxed to top-2, with the reason |
| `.env.example` | - | Placeholder key only |

`python -m unittest discover -s tests` → **66 tests OK, 1 skipped** (real-model embedding test; fastembed cannot load here).

## Still to do

Needs the API key in `.env` (`copy .env.example .env`, never commit it) and Claude Code CLI:
```
python solutions/day2_models_and_embeddings/compare_tiers_cli.py --query Q1
python solutions/day2_models_and_embeddings/compare_tiers_cli.py --query Q2
python solutions/day2_models_and_embeddings/compare_tiers_cli.py --query Q3
python solutions/day2_models_and_embeddings/compare_tiers_cli.py --prompt "<paste data/own_query_term_deposit.txt>"
python solutions/day2_models_and_embeddings/verify_outputs.py          # live Part D run
```
By hand, in a browser: the Q1 prompt from `outputs/day2_runs/partB_homework_pack.txt` in ChatGPT, Claude.ai and
Gemini (new chat each time), then fill in `outputs/homework_comparison.md` and the settings table in the write-up.

Optional: install the Microsoft Visual C++ Redistributable so `onnxruntime` loads, then run
`python solutions/day2_models_and_embeddings/embeddings_map.py` for the real-model map.
