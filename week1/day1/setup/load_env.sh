#!/usr/bin/env bash
# load_env.sh
# -----------
# Copies the values in .env into the CURRENT shell, so that Claude Code CLI
# (which does not read .env itself) can see ANTHROPIC_API_KEY.
#
# IMPORTANT: use "source" (or a leading dot), otherwise the variables vanish
# when the script ends:
#
#     source setup/load_env.sh
#
# The values live only in this terminal and vanish when you close it.

ENV_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "No .env found at $ENV_FILE - copy .env.example first."
  return 1 2>/dev/null || exit 1
fi

# 'set -a' marks every variable assigned while it is on for export to child
# processes (such as the claude command). Comments and blank lines are ignored by the shell.
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
echo "Loaded .env into this shell."
