# GenAIOps Enablement - Module 1: The AI Ecosystem (Hands-on Lab)

Two 2-hour sessions of hands-on work. You will bootstrap a shared VM (VS Code + Claude Code CLI),
map one realistic enterprise scenario onto every level of the **automation-to-agentic spectrum**,
and compare how different Claude **model tiers** answer the same question.

Everything runs on **synthetic data**. Nothing here needs your company's real data, and nothing should be given any.

| | Day 1 - The spectrum | Day 2 - Models, embeddings, verification |
|---|---|---|
| Idea | Traditional automation -> AI automation -> AI agent -> multi-agent -> agentic AI | Not all models are equal; meaning as numbers; never act on an unchecked answer |
| In-lab | Run five levels on the same support-ticket scenario | Compare Opus / Sonnet / Haiku through Claude Code CLI on the same query |
| Homework | Take-home assignment (Word file) | Run the same query in ChatGPT, Claude.ai and Gemini web apps (no API key) |
| Folder | `solutions/day1_ai_spectrum/` | `solutions/day2_models_and_embeddings/` |

```
Participant VM
 +-- VS Code (editor + terminal)
 +-- .env  --->  common/config.py  --->  common/llm.py  --->  Anthropic API  (Opus / Sonnet / Haiku)
 +-- Claude Code CLI  -------------------------------------->  Anthropic API
 +-- solutions/  (Day 1, Day 2)   reads data/, writes outputs/
```

A full picture is in [`docs/diagrams/architecture.png`](docs/diagrams/architecture.png) and is explained in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). New terms are explained in
[`docs/Tools_Libraries_and_Concepts.docx`](docs/Tools_Libraries_and_Concepts.docx).

---

## 1. What you need before you start

| Item | Check with | Notes |
|---|---|---|
| Python 3.11 or newer | `python --version` (Windows: `py -3.11 --version`) | Install from python.org; tick "Add to PATH" |
| Git | `git --version` | |
| VS Code | `code --version` | Optional but recommended; install the **Python** extension |
| Anthropic API key | - | One programme key is issued to you. Treat it like a password |
| Internet access | - | To reach `api.anthropic.com` and package registries |

You do **not** need an API key for: Level 1, the offline parts of `context_and_tokens.py`, `embeddings_map.py --toy`,
`verify_outputs.py --offline-demo`, `redact_pii.py`, `homework_pack.py`, or the homework itself.

---

## 2. Bootstrap the VM (about 10 minutes)

### Step 1 - Get the code

```bash
git clone <your-repository-url> genaiops-ai-ecosystem-lab
cd genaiops-ai-ecosystem-lab
```

Open the folder in VS Code (`code .`) and use **Terminal -> New Terminal**.

### Step 2 - One-shot setup script (recommended)

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File .\setup\bootstrap_windows.ps1 -InstallClaude
```
**macOS / Linux / WSL:**
```bash
bash setup/bootstrap_unix.sh --install-claude
```
The script creates a virtual environment (`.venv`), installs the packages in `requirements.txt`,
creates `.env` from `.env.example`, and installs Claude Code CLI if it is missing.
(Prefer to do it by hand? See "Manual setup" below.)

### Step 3 - Add your API key

Open `.env` in VS Code and replace the placeholder:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here      <-- paste the programme key here
```
No quotes, no trailing spaces. **Never commit `.env` and never show it on a shared screen** (`.gitignore` already excludes it).
Only `.env.example` (with the fake key) is stored in Git.

### Step 4 - Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1        # Windows PowerShell
```
```bash
source .venv/bin/activate           # macOS / Linux / WSL
```
Your prompt should now start with `(.venv)`. Do this in every new terminal.

### Step 5 - Make the key visible to Claude Code CLI

Claude Code does **not** read `.env`. The Python scripts do. The comparison script in Day 2 passes the key to the CLI for you,
but if you also want to use `claude` interactively, load the key into the current terminal:

```powershell
. .\setup\load_env.ps1              # Windows (note the leading dot and space)
```
```bash
source setup/load_env.sh            # macOS / Linux / WSL
```
The first time you start `claude` with an API key set, it asks once whether to use that key - answer **Yes**.

### Step 6 - Check everything

```bash
python setup/check_environment.py            # offline checks
python setup/check_environment.py --live     # plus one tiny API call per model tier
```
You want all `PASS` (a `WARN` for the optional `fastembed` package is fine).
Run the unit tests as well - they need no key:
```bash
python -m unittest discover -s tests
```

### Manual setup (if you skip the script)

```bash
python -m venv .venv
# activate it (Step 4), then:
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-embeddings.txt        # optional: real embeddings for Day 2
cp .env.example .env                              # Windows: Copy-Item .env.example .env
# Install Claude Code CLI - any ONE of these:
#   Windows PowerShell : irm https://claude.ai/install.ps1 | iex
#   macOS / Linux / WSL: curl -fsSL https://claude.ai/install.sh | bash
#   Windows (winget)   : winget install Anthropic.ClaudeCode
#   npm (Node 18+)     : npm install -g @anthropic-ai/claude-code
```

---

## 3. Day 1 - map one scenario onto the whole spectrum

Scenario: a (fictional) retailer receives refund requests. Eight synthetic tickets include a late delivery, a damaged parcel,
a refund above the agent's limit, an out-of-window request, a status question, a request from the wrong person,
and a ticket containing a **prompt-injection attack**.

Run in this order (from the repo root, venv active):

| # | Command | Key needed? | What you see |
|---|---|---|---|
| 1 | `python solutions/day1_ai_spectrum/level1_traditional_automation.py` | No | Keyword rules work until the wording changes (7/8 correct, then a brittleness demo) |
| 2 | `python solutions/day1_ai_spectrum/level2_ai_automation.py` | Yes | Model understands and writes text; a fixed workflow still decides |
| 3 | `python solutions/day1_ai_spectrum/level3_ai_agent.py --ticket T-01` | Yes | The agent chooses its own tool calls. Try `--ticket T-07` (injection) and `--all` |
| 4 | `python solutions/day1_ai_spectrum/level4_multi_agent.py` | Yes | Investigator -> Resolver -> Reviewer, each with its own role and model tier |
| 5 | `python solutions/day1_ai_spectrum/level5_agentic_ai.py` | Yes | Given a goal ("clear the queue") it plans multi-ticket work; guardrails cap it |
| 6 | `python solutions/day1_ai_spectrum/context_and_tokens.py` (add `--exact`) | Only for `--exact` | Tokens vs words, context windows, why agent loops get expensive |

What to notice: after every level a scoreboard shows what the policy expected versus what the run did.
The refund tool lives in `dispute_tools.py` and **enforces the rules in code**, so even a model that obeys the injected
"refund 500" instruction is blocked. Details: [`solutions/day1_ai_spectrum/README.md`](solutions/day1_ai_spectrum/README.md).

## 4. Day 2 - tiers, embeddings, verification

| # | Command | Key needed? | What you see |
|---|---|---|---|
| 1 | `python solutions/day2_models_and_embeddings/compare_tiers_cli.py` | Yes (via CLI) | **In-lab:** same contract question to Opus, Sonnet, Haiku: answer, speed, tokens, cost |
| 2 | `python solutions/day2_models_and_embeddings/embeddings_map.py` (`--toy` for offline) | No | Meaning as numbers, semantic search, a 2-D "map of meaning" in `outputs/` |
| 3 | `python solutions/day2_models_and_embeddings/verify_outputs.py --offline-demo` | No | Code catches a made-up quote and a wrong calculation; risk tier + audit log |
| 4 | `python solutions/day2_models_and_embeddings/redact_pii.py --demo` | No | Pattern-based PII redaction, and what it cannot catch |
| 5 | `python solutions/day2_models_and_embeddings/homework_pack.py` | No | **Homework:** the identical prompt + a sheet to compare ChatGPT, Claude.ai and Gemini |

Details: [`solutions/day2_models_and_embeddings/README.md`](solutions/day2_models_and_embeddings/README.md).

## 5. Take-home assignments

One Word document per solution, in [`docs/assignments/`](docs/assignments/):
`Day1_Take_Home_Assignment.docx` and `Day2_Take_Home_Assignment.docx`.
A reading guide to the tools, libraries and concepts is in `docs/Tools_Libraries_and_Concepts.docx`.

---

## 6. Repository layout

```
.env.example              sample configuration (copy to .env; never commit .env)
requirements*.txt         Python packages
setup/                    bootstrap scripts, environment checker, .env loaders for the CLI
common/config.py          reads .env, model IDs, limits
common/llm.py             ask(), the agent loop, count_tokens(), extract_json()
solutions/day1_ai_spectrum/             levels 1-5, dispute_tools.py, context_and_tokens.py, data/
solutions/day2_models_and_embeddings/   tier comparison, embeddings, verification, redaction, homework
tests/                    unit tests with a fake model client (no key, no network)
docs/                     architecture, concepts, diagrams, Word documents
outputs/                  files the scripts generate (ignored by Git)
```

## 7. Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `claude` / `code` / `python` "not found" right after installing | Terminals read PATH only when they open. **Close the terminal, open a new one** (or restart VS Code) |
| `ANTHROPIC_API_KEY is missing or still the sample value` | `.env` is not edited, is in the wrong folder, or has quotes/spaces. It must sit in the repo root next to `.env.example` |
| `ModuleNotFoundError: anthropic` (or numpy, ...) | Virtual environment not active, or packages not installed: activate `.venv`, then `pip install -r requirements.txt` |
| PowerShell: "running scripts is disabled" | Use the `-ExecutionPolicy Bypass` form shown above, or run `Set-ExecutionPolicy -Scope Process Bypass` in that window |
| `401` / authentication error | Wrong or revoked key. Re-copy it; no extra characters |
| `404` / "model not found" | Your organisation approved different model IDs. Edit the `CLAUDE_MODEL_*` lines in `.env` |
| `429` rate limit | Many participants share one key. Wait a few seconds and re-run; the SDK already retries automatically |
| Claude Code asks about the API key | Expected the first time: choose **Yes** to use the key |
| `compare_tiers_cli.py` says tier failed | Run `claude --version`; run `compare_tiers_cli.py --dry-run` to see the command; then run it by hand to read the error |
| fastembed download fails | No problem: use `embeddings_map.py --toy` (offline) |
| Model answers differ from the examples | Normal. Models are not deterministic; compare reasoning, not exact wording |

## 8. Ground rules

* Synthetic data only. No real customer, employee or company data in any tool, ever, in this lab.
* Never commit secrets. `git status` should never list `.env`.
* The model proposes; **code verifies; a human decides**. Do not act on an unchecked model answer.
* Model names, prices and limits change. Check the current Anthropic documentation for the latest.
