# Vector Mathematics: The Internals (Hands-on Lab)

Compute **cosine similarity** and **Euclidean distance** by hand, then in Python with Claude Code, and understand why
"closer vectors" means "similar meaning". Small on purpose: plain Python, no API key needed for the lab code.

```
data/vectors.json         toy word/sentence vectors (synthetic, 4 numbers each, hand-assigned)
vector_math.py            ANSWER KEY: dot, norm, cosine_similarity, euclidean_distance + step-by-step printout
step1_by_hand_check.py    do the maths on paper, type your answers, get feedback
my_vector_math.py         YOUR file: Claude Code writes the four functions (stubs now)
step3_check_my_code.py    checks your functions against the answer key
step4_why_cosine.py       four experiments: direction vs length, ranking, unit vectors, numpy
scenario_matrix.py        unguided session: compare every item with every other in YOUR own mini scenario
CLAUDE_CODE_PROMPTS.md    prompts to paste into Claude Code
tests/                    unit tests for this repo
```

## Set up (5 minutes)

1. Python 3.11+ installed (`python --version`). Open this folder in VS Code and open a terminal.
2. (Optional) virtual environment: `python -m venv .venv`, then activate it
   (Windows: `.\.venv\Scripts\Activate.ps1`, macOS/Linux: `source .venv/bin/activate`).
3. (Optional) `pip install -r requirements.txt` - only needed for numpy in experiment 4.
4. Claude Code CLI installed and signed in with the programme API key (done in the Day 1 set-up). The lab code itself
   does not use the key and there is no `.env` file in this repo.

## Steps

| Step | Command | What you do |
|---|---|---|
| 0 | `python vector_math.py --list` then `python vector_math.py loan mortgage` | See one fully worked example |
| 1 | `python step1_by_hand_check.py` | Work four exercises on paper, type answers, get feedback (`--show` prints the working) |
| 2 | start `claude`, use `CLAUDE_CODE_PROMPTS.md` | Claude Code writes the four functions in `my_vector_math.py` |
| 3 | `python step3_check_my_code.py` | Check Claude's code. All four must say PASS |
| 4 | `python step4_why_cosine.py` | Read the four experiments; answer the question after each |
| 5 | `python -m unittest discover -s tests` | Run the repo's own tests |

## Rules
* Synthetic data only. Do not put real customer or bank data into any file or prompt.
* The checker is the judge, not Claude Code. If they disagree, trust the maths you did by hand.
* Do the hand calculations before you look at any answer.

## Troubleshooting
* `ModuleNotFoundError: vector_math`: run commands from this folder (the one containing `vector_math.py`).
* `python` not found: try `py` (Windows) or `python3` (macOS/Linux); open a NEW terminal after installing Python.
* Step 3 shows TODO: the functions in `my_vector_math.py` are still stubs - go to Step 2.
