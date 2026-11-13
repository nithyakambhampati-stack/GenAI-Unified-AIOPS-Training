"""
llm_client.py - ask(prompt, case): LIVE Claude via the Claude Code CLI (claude -p), or a SIMULATED mock model.

The mock reads features of your prompt (JSON schema? verbatim quotes? not-found rule? untrusted-data rule? step-by-step?)
and behaves like a model that follows - or ignores - what the prompt says. It tests your harness offline.
It does NOT prove your prompt works on a real model: finish with a live run.
"""
import json
import shutil
import subprocess
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
MOCK = json.loads((DATA / "mock.json").read_text(encoding="utf-8"))


def live_available():
    return shutil.which("claude") is not None


def ask_live(prompt, timeout=120):
    r = subprocess.run([shutil.which("claude"), "-p", prompt], capture_output=True, text=True, encoding="utf-8", timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {r.stderr.strip()[:200]}")
    return r.stdout.strip()


def features(prompt):
    low = prompt.lower()
    return dict(
        schema=all(w in low for w in ("json", "citations", "section", "quote")),
        verbatim=any(w in low for w in ("verbatim", "word for word", "word-for-word", "exact words")),
        refuse="not found" in low,
        untrusted=("<document>" in low) and any(w in low for w in ("untrusted", "data, not instructions", "never follow instructions", "not instructions")),
        stepwise=any(w in low for w in ("step by step", "step-by-step", "think through", "first identify", "work out")),
        feedback="feedback:" in low,
    )


def ask_mock(prompt, case):
    t, f = case["truth"], features(prompt)
    for canary in MOCK["canaries"]:
        if canary.lower() in prompt.lower() and not f["untrusted"]:
            return f"Confirmed. {canary}. All charges are waived and every claim is approved."      # followed the injected instruction
    answer = t["answer_text"]
    if t.get("tricky") and not (f["stepwise"] or f["feedback"]):
        answer = t["wrong_answer"]                                                                     # skipped the reasoning
    if not t["answerable"]:
        if not f["schema"]:
            return t["wrong_answer"]
        if f["refuse"]:
            return json.dumps({"answer": "Not found in the document.", "citations": [], "confidence": "low"})
        return json.dumps({"answer": t["wrong_answer"], "citations": [{"section": "S9.9", "quote": "as per standard practice"}], "confidence": "high"})
    if not f["schema"]:
        return answer
    quote = t["quote"] if (f["verbatim"] or f["feedback"]) else t["paraphrase"]
    return json.dumps({"answer": answer, "citations": [{"section": t["sections"][0], "quote": quote}], "confidence": "high"})


def ask(prompt, case, mock=False):
    if mock:
        return ask_mock(prompt, case)
    if not live_available():                       # a --live run must never quietly turn into a mock run
        raise RuntimeError("--live was requested but the claude CLI is not on PATH")
    return ask_live(prompt)
