# Day 1 take-home

Course repo: https://github.com/digibhatia/automation-to-agentic-spectrum (copied here with my changes).
The brief is `docs/assignments/Day1_Take_Home_Assignment.docx` and my answers are in `docs/Day1_Writeup.md`.

## What I changed

- `solutions/day1_ai_spectrum/dispute_tools.py` - the 14-day damage rule (Part B), and `money_amounts()` /
  `check_reply()` plus the check inside `draft_reply()` (Part C).
- `data/policy.md` - rule 2 now has the 14-day window, and I added rule 8 (replies only promise what was done).
- `data/orders.json` and `tickets.json` - three new tickets: T-09 (day-14 boundary), T-10 (fake tool result) and
  T-11 (Portuguese instruction).
- `level3_ai_agent.py`, `level4_multi_agent.py`, `level5_agentic_ai.py` - token totals for Part D, and blocked
  replies are listed.
- `context_and_tokens.py` - fixed the chunker, which was cutting off the second line of rules and ignoring rule 8.
- `tests/test_day1_assignment.py` - 14 new tests. I also moved three old tests from T-02 to T-09, because T-02
  isn't refundable any more under the new rule.
- `run_levels.py` - small helper that runs a level, times it, and saves the output to `outputs/day1_runs/`.
- `.env.example` - placeholder only. One of the course tests expects this file to exist.

Tests: 69 OK (55 from the course + my 14).

## Still to do (needs the API key)

1. `copy .env.example .env`, then put the key in `.env`. It's git-ignored, so it won't get committed.
2. The Part B "before" run for Level 3. The old rule is saved under the git tag `day1-partB-before`, so I can check
   it out into a separate folder:
   ```
   git worktree add ..\..\..\partB_before day1-partB-before
   copy .env ..\..\..\partB_before\week1\day1\
   cd ..\..\..\partB_before\week1\day1
   python run_levels.py 10_partB_before 3:T-02 3:T-09
   copy outputs\day1_runs\10_partB_before_* ..\..\..\genaiops-gitlab\week1\day1\outputs\day1_runs\
   cd ..\..\..\genaiops-gitlab\week1\day1
   git worktree remove --force ..\..\..\partB_before
   ```
3. Then back here:
   ```
   python run_levels.py 11_partB_after 3:T-02 3:T-09
   python run_levels.py 21_partC 2 3:T-10 3:T-11 5
   python run_levels.py 30_after 3all 4 5
   ```
4. Fill in the pending parts of the write-up, then export it to PDF.
