"""
run_levels.py  -  run spectrum levels, time them, and keep the output as evidence.

    python run_levels.py LABEL LEVEL [LEVEL ...]

    python run_levels.py 30_after 1 2 3all 4 5     # final runs for Part D
    python run_levels.py 21_partC 2 3:T-10 3:T-11 5

LEVEL is 1, 2, 3all (level 3 --all), 3:T-xx (level 3 on one ticket), 4 or 5.
Each run is saved to outputs/day1_runs/<LABEL>_level<LEVEL>.txt with the wall time on the last line.
Levels 2-5 need ANTHROPIC_API_KEY in .env (never commit .env).
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "solutions" / "day1_ai_spectrum"
OUT = ROOT / "outputs" / "day1_runs"

COMMANDS = {
    "1": ["level1_traditional_automation.py"],
    "2": ["level2_ai_automation.py"],
    "3all": ["level3_ai_agent.py", "--all"],
    "4": ["level4_multi_agent.py"],
    "5": ["level5_agentic_ai.py"],
}


def command_for(level: str) -> list[str]:
    """Turn a LEVEL argument into the script and its arguments."""
    if level.startswith("3:"):
        return ["level3_ai_agent.py", "--ticket", level[2:]]
    if level not in COMMANDS:
        sys.exit(f"Unknown level {level!r}. Use 1, 2, 3all, 3:T-xx, 4 or 5.")
    return COMMANDS[level]


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    label, levels = sys.argv[1], sys.argv[2:]
    OUT.mkdir(parents=True, exist_ok=True)
    for level in levels:
        script, *args = command_for(level)
        start = time.perf_counter()
        run = subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", cwd=ROOT)
        seconds = time.perf_counter() - start
        path = OUT / f"{label}_level{level.replace(':', '_')}.txt"
        path.write_text(run.stdout + run.stderr + f"\nWALL_TIME_S={seconds:.1f}\n", encoding="utf-8")
        score = next((line for line in run.stdout.splitlines() if "handled as the policy expects" in line), "no scoreboard")
        print(f"level {level:<7} {seconds:6.1f}s  {score}  -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
