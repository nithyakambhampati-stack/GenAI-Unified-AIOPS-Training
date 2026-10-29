"""
setup/check_environment.py
==========================
Bootstrap check for the shared lab VM. Run this FIRST, and again after every fix.

    python setup/check_environment.py            # fast, offline checks
    python setup/check_environment.py --live     # also makes one tiny API call per tier

What it verifies
----------------
* Python 3.11+, Git, VS Code command line (``code``), Claude Code CLI (``claude``)
* The Python packages from requirements.txt are importable
* .env exists, and ANTHROPIC_API_KEY is set to something other than the sample value
* (--live) the key really works and each model tier answers

Result: a PASS / WARN / FAIL table. Exit code 0 only if nothing FAILED.

Most common surprise
--------------------
A tool you just installed shows "not found". Terminals read PATH once when they open,
so a terminal that was already open does not see new installs. Close it, open a NEW
terminal (or restart VS Code), and run this check again.
"""
from __future__ import annotations

import argparse
import importlib
import shutil
import subprocess
import sys
from pathlib import Path

# Make the repo root importable when this file is run as a script from any folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common import config  # noqa: E402  (import after sys.path tweak, on purpose)

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
results: list[tuple[str, str, str]] = []  # (status, check name, detail)


def record(status: str, name: str, detail: str) -> None:
    """Remember one check result and print it immediately."""
    results.append((status, name, detail))
    print(f"[{status}] {name:<28} {detail}")


def run_version(cmd: list[str]) -> str | None:
    """Run '<tool> --version' and return the first line of output, or None if it fails."""
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        text = (out.stdout or out.stderr).strip()
        return text.splitlines()[0] if out.returncode == 0 and text else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def check_python() -> None:
    v = sys.version_info
    ok = (v.major, v.minor) >= (3, 11)
    record(PASS if ok else FAIL, "Python 3.11+", f"{v.major}.{v.minor}.{v.micro}")


def check_tool(name: str, exe: str, required: bool, hint: str) -> None:
    """shutil.which also finds Windows shims such as code.cmd, so we do not hard-code '.exe'."""
    path = shutil.which(exe)
    if not path:
        record(FAIL if required else WARN, name, f"not found on PATH. {hint}")
        return
    version = run_version([path, "--version"])
    record(PASS, name, version or path)


def check_packages() -> None:
    # (import name, pip name, required?)
    packages = [
        ("anthropic", "anthropic", True),
        ("dotenv", "python-dotenv", True),
        ("numpy", "numpy", True),
        ("sklearn", "scikit-learn", True),
        ("matplotlib", "matplotlib", True),
        ("fastembed", "fastembed", False),  # optional: real embeddings for Day 2
    ]
    for import_name, pip_name, required in packages:
        try:
            module = importlib.import_module(import_name)
            record(PASS, f"package {pip_name}", getattr(module, "__version__", "importable"))
        except ImportError:
            if required:
                record(FAIL, f"package {pip_name}", "missing. Activate the venv, then: pip install -r requirements.txt")
            else:
                record(WARN, f"package {pip_name}", "optional. Day 2 demo will use the offline toy embedder")


def check_env_file() -> None:
    if not config.ENV_PATH.exists():
        record(FAIL, ".env file", f"missing. Copy .env.example to {config.ENV_PATH}")
        return
    record(PASS, ".env file", str(config.ENV_PATH))
    key = config.get_api_key()
    if not key:
        record(FAIL, "ANTHROPIC_API_KEY", "missing or still the sample value")
        return
    # Show only the first and last characters - never print a full key.
    masked = f"{key[:7]}...{key[-4:]}"
    status = PASS if key.startswith("sk-ant-") else WARN
    note = "set" if status == PASS else "set, but does not start with sk-ant- (check for typos)"
    record(status, "ANTHROPIC_API_KEY", f"{note} ({masked})")


def check_live() -> None:
    """One tiny request per tier: proves the key, the network path and the model IDs."""
    from common import llm  # imported late: needs the SDK and a key

    for tier, model_id in config.TIERS.items():
        try:
            reply = llm.ask("Reply with the single word: ready", model=model_id, max_tokens=16)
            record(PASS, f"live call: {tier}", f"{model_id} -> {reply.text.strip()!r} ({reply.latency_s:.1f}s)")
        except Exception as exc:  # report, do not crash: we want to see all tiers
            record(FAIL, f"live call: {tier}", f"{model_id}: {type(exc).__name__}: {str(exc)[:120]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the lab VM is ready.")
    parser.add_argument("--live", action="store_true", help="also make one tiny API call per model tier")
    args = parser.parse_args()

    print("GenAIOps lab - environment check\n" + "-" * 60)
    check_python()
    check_tool("Git", "git", True, "Install Git, then open a NEW terminal.")
    check_tool("VS Code CLI (code)", "code", False, "In VS Code: Ctrl+Shift+P -> 'Shell Command: Install code command' (or reopen the terminal).")
    check_tool("Claude Code CLI (claude)", "claude", True, "See README step 4, then open a NEW terminal.")
    check_packages()
    check_env_file()
    if args.live:
        check_live()
    else:
        print("[INFO] live API check skipped (add --live to run it)")

    failed = [r for r in results if r[0] == FAIL]
    warned = [r for r in results if r[0] == WARN]
    print("-" * 60)
    print(f"{len(results) - len(failed) - len(warned)} passed, {len(warned)} warnings, {len(failed)} failed")
    if failed:
        print("Fix the FAIL items above, open a NEW terminal, and run this check again.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
