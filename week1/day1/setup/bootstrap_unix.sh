#!/usr/bin/env bash
# bootstrap_unix.sh
# -----------------
# One-shot setup for macOS, Linux or WSL.
#
# Run from anywhere:
#     bash setup/bootstrap_unix.sh                 # set up Python environment and .env
#     bash setup/bootstrap_unix.sh --install-claude  # also install Claude Code CLI if missing
#
# What it does:
#   1. Checks Python 3.11+ and Git
#   2. Creates a virtual environment in .venv
#   3. Installs requirements.txt (and tries the optional embeddings package)
#   4. Creates .env from .env.example if you do not have one yet
#   5. Checks for the Claude Code CLI (installs it only with --install-claude)

# Stop on the first error, treat unset variables as errors, and fail a pipeline if any step fails.
set -euo pipefail

# Move to the repo root (the parent of the folder this script lives in).
cd "$(dirname "${BASH_SOURCE[0]}")/.."

INSTALL_CLAUDE=false
[[ "${1:-}" == "--install-claude" ]] && INSTALL_CLAUDE=true

echo "== 1/5  Checking Python and Git"
# Prefer python3.11+; fall back to python3.
PYTHON=$(command -v python3.12 || command -v python3.11 || command -v python3 || true)
[[ -z "$PYTHON" ]] && { echo "Python 3.11+ not found. Install it, then re-run."; exit 1; }
"$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' \
  || { echo "Python 3.11+ is required (found $($PYTHON --version))."; exit 1; }
command -v git >/dev/null || { echo "Git not found. Install Git, then re-run."; exit 1; }

echo "== 2/5  Creating virtual environment (.venv)"
[[ -d .venv ]] || "$PYTHON" -m venv .venv

echo "== 3/5  Installing Python packages"
# Use the venv's own pip so we do not depend on activation state.
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
# Optional package: failure is acceptable, the Day 2 demo has an offline fallback.
.venv/bin/python -m pip install -r requirements-embeddings.txt \
  || echo "Optional embeddings package not installed (demo will use the toy embedder)."

echo "== 4/5  Preparing .env"
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env - open it and paste the programme API key."
else
  echo ".env already exists - leaving it untouched."
fi

echo "== 5/5  Claude Code CLI"
if command -v claude >/dev/null; then
  echo "Found: $(claude --version)"
elif $INSTALL_CLAUDE; then
  # Official native installer for macOS / Linux / WSL (from the Claude Code documentation).
  curl -fsSL https://claude.ai/install.sh | bash
  echo "Done. Open a NEW terminal so PATH refreshes."
else
  echo "Claude Code CLI not found. Re-run with --install-claude, or run:"
  echo "  curl -fsSL https://claude.ai/install.sh | bash"
fi

echo
echo "Next:  source .venv/bin/activate   then   python setup/check_environment.py"
