# Day 1 take-home - what is here and how to finish it

Course repo: `https://github.com/digibhatia/automation-to-agentic-spectrum` (full copy, with my changes).
Brief: `docs/assignments/Day1_Take_Home_Assignment.docx`. Write-up: **`docs/Day1_Writeup.md`**.

## Files changed or added

| File | Part | Change |
|---|---|---|
| `solutions/day1_ai_spectrum/dispute_tools.py` | B, C | `DAMAGE_REPORT_DAYS` rule; `money_amounts()`, `check_reply()` and the reply check in `draft_reply()` |
| `solutions/day1_ai_spectrum/data/policy.md` | B, C | Rule 2 (14-day damage window), new rule 8 (replies only promise what was done) |
| `solutions/day1_ai_spectrum/data/orders.json`, `tickets.json` | B, C | ORD-1009/T-09 (boundary), ORD-1010/T-10 (forged tool result), ORD-1011/T-11 (Portuguese instruction) |
| `solutions/day1_ai_spectrum/level3_ai_agent.py` | D | `--all` prints total tokens; lists blocked replies |
| `solutions/day1_ai_spectrum/level4_multi_agent.py` | D | Token tally per role |
| `solutions/day1_ai_spectrum/level5_agentic_ai.py` | C | Lists blocked replies with blocked refunds |
| `solutions/day1_ai_spectrum/context_and_tokens.py` | B | Chunker keeps continuation lines and rules numbered above 7 |
| `tests/test_day1_assignment.py` | B, C | 14 new tests |
| `tests/test_core.py`, `tests/test_levels.py` | B, C | Three tests moved from T-02 to T-09; Level 1 now also misses T-11 |
| `run_levels.py` | D | Runs levels, times them, saves the output to `outputs/day1_runs/` |
| `.env.example` | - | Placeholder key only (missing from the course repo; a test needs it) |

`python -m unittest discover -s tests` → **69 tests OK** (55 course + 14 new).

## Still to do (needs the programme API key)

1. `copy .env.example .env` and put the key in `.env` (git-ignored - never commit it).
2. Part B, Level 3 *before* the rule change. The course code plus the T-09 test data (old rule) is the git tag
   `day1-partB-before`. From this folder (PowerShell):
   ```
   git worktree add ..\..\..\partB_before day1-partB-before
   copy .env ..\..\..\partB_before\week1\day1\
   cd ..\..\..\partB_before\week1\day1
   python run_levels.py 10_partB_before 3:T-02 3:T-09
   copy outputs\day1_runs\10_partB_before_* ..\..\..\genaiops-gitlab\week1\day1\outputs\day1_runs\
   cd ..\..\..\genaiops-gitlab\week1\day1
   git worktree remove --force ..\..\..\partB_before
   ```
3. Back in this folder:
   ```
   python run_levels.py 11_partB_after 3:T-02 3:T-09
   python run_levels.py 21_partC 2 3:T-10 3:T-11 5
   python run_levels.py 30_after 3all 4 5
   ```
4. Fill in the [PENDING LIVE RUN] sections of `docs/Day1_Writeup.md` from those files, then export it to PDF/Word.
