"""
common/config.py
================
Single place where the lab reads its configuration.

Why this file exists
--------------------
* Every script needs the same things: the API key, the model IDs, a safe step
  budget and an output folder. Reading them in one module avoids copy-paste.
* The .env file is loaded from the REPOSITORY ROOT using an explicit path.
  Calling ``load_dotenv()`` with no argument searches relative to the current
  working directory, so a correctly filled .env is silently ignored when you
  launch a script from another folder. The explicit path removes that trap.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# The repo root is the folder that contains common/, solutions/, setup/ and .env.
# __file__ is this file (common/config.py); parent is common/; parent.parent is the root.
REPO_ROOT: Path = Path(__file__).resolve().parent.parent

# Load <repo root>/.env into os.environ. Variables already set in the real
# environment win over the file (override=False is the default), which lets an
# administrator inject the key centrally if they prefer.
ENV_PATH: Path = REPO_ROOT / ".env"
load_dotenv(ENV_PATH)

# Values that mean "the participant has not replaced the sample key yet".
_PLACEHOLDER_PREFIXES = ("sk-ant-your", "your-api-key", "changeme")


def get_api_key() -> str | None:
    """Return the Anthropic API key, or None if it is missing or still a placeholder."""
    # Strip whitespace and stray quotes - the two most common copy/paste mistakes.
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip().strip('"').strip("'")
    if not key or key.lower().startswith(_PLACEHOLDER_PREFIXES):
        return None
    return key


# --- Model tiers used by the Python scripts (full model IDs, editable in .env) ----
TIERS: dict[str, str] = {
    "opus": os.environ.get("CLAUDE_MODEL_OPUS", "claude-opus-5-5"),
    "sonnet": os.environ.get("CLAUDE_MODEL_SONNET", "claude-sonnet-5-5"),
    "haiku": os.environ.get("CLAUDE_MODEL_HAIKU", "claude-haiku-5-5"),
}

# --- Model names/aliases passed to the Claude Code CLI (--model flag) ---------------
CLI_TIERS: dict[str, str] = {
    "opus": os.environ.get("CLAUDE_CLI_MODEL_OPUS", "opus"),
    "sonnet": os.environ.get("CLAUDE_CLI_MODEL_SONNET", "sonnet"),
    "haiku": os.environ.get("CLAUDE_CLI_MODEL_HAIKU", "haiku"),
}

# Default model for the scripts that do not compare tiers.
DEFAULT_MODEL: str = os.environ.get("CLAUDE_MODEL_DEFAULT", TIERS["sonnet"])


def _int_env(name: str, default: int) -> int:
    """Read an integer setting, falling back to a default if it is missing or invalid."""
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


# Safety / cost knobs. An agent that loops forever is a cost and safety problem,
# so every tool loop in this lab is bounded by AGENT_MAX_STEPS.
AGENT_MAX_STEPS: int = _int_env("AGENT_MAX_STEPS", 8)
LLM_MAX_TOKENS: int = _int_env("LLM_MAX_TOKENS", 1024)
CLI_TIMEOUT_SECONDS: int = _int_env("CLAUDE_CLI_TIMEOUT_SECONDS", 180)


def output_dir() -> Path:
    """Folder where scripts write reports, charts and logs (created on demand)."""
    path = REPO_ROOT / "outputs"
    path.mkdir(exist_ok=True)
    return path
