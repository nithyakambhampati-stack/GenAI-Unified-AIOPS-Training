"""
common/llm.py
=============
A deliberately small wrapper around the Anthropic Python SDK.

It gives the lab scripts four building blocks:

1. ``ask()``            - one prompt in, one answer out (plus token and latency numbers)
2. ``run_tool_loop()``  - the AGENT LOOP: the model asks for a tool, our code runs it,
                          the result goes back to the model, repeat until it answers
3. ``count_tokens()``   - exact token counts from the API (Day 1: words vs tokens)
4. ``extract_json()``   - pulls a JSON object out of a model reply (models sometimes
                          wrap JSON in prose or code fences)

Key idea for the agent loop
---------------------------
The model never executes anything itself. It only *requests* a tool call as
structured text. OUR code decides whether to run it, runs it, and returns the
result. That is why guardrails (limits, ownership checks, approvals) belong in
our tool code, not in the prompt.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from . import config

# The SDK client is created lazily (on first use) so that importing this module
# never fails on a machine where the key is not configured yet - for example
# while running the offline parts of the lab or the unit tests.
_client = None


def get_client():
    """Create (once) and return the Anthropic SDK client."""
    global _client
    if _client is None:
        key = config.get_api_key()
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is missing or still the sample value.\n"
                f"Open {config.ENV_PATH} and paste the programme key "
                "(no quotes, no trailing spaces), then run again."
            )
        import anthropic  # imported here so the rest of the lab works without the SDK

        # max_retries: the SDK retries transient errors (rate limits, 5xx) with backoff.
        # timeout: seconds before a hung request is abandoned.
        _client = anthropic.Anthropic(api_key=key, max_retries=3, timeout=120.0)
    return _client


# ----------------------------------------------------------------------------------
# 1. Plain call
# ----------------------------------------------------------------------------------
@dataclass
class LLMResult:
    """Everything we want to know about one model call."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_s: float
    stop_reason: str | None = None


def _text_of(content_blocks) -> str:
    """Join the text blocks of a reply (a reply can also contain tool_use blocks)."""
    return "".join(getattr(b, "text", "") for b in content_blocks if getattr(b, "type", None) == "text")


def ask(
    user: str,
    system: str = "",
    model: str | None = None,
    max_tokens: int | None = None,
) -> LLMResult:
    """Send one user message (optionally with a system prompt) and return the reply."""
    client = get_client()
    model = model or config.DEFAULT_MODEL
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens or config.LLM_MAX_TOKENS,
        "messages": [{"role": "user", "content": user}],
    }
    if system:
        kwargs["system"] = system  # the system prompt sets role and rules for the whole call

    started = time.perf_counter()
    response = client.messages.create(**kwargs)
    elapsed = time.perf_counter() - started

    return LLMResult(
        text=_text_of(response.content),
        model=getattr(response, "model", model),
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_s=elapsed,
        stop_reason=getattr(response, "stop_reason", None),
    )


# ----------------------------------------------------------------------------------
# 2. The agent loop (tool use)
# ----------------------------------------------------------------------------------
@dataclass
class ToolEvent:
    """One entry in the agent's trace, so participants can SEE what the agent did."""

    kind: str  # "tool_call" or "tool_result"
    name: str
    payload: Any


@dataclass
class AgentRun:
    """Outcome of one run of the agent loop."""

    final_text: str
    events: list[ToolEvent] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    stopped_reason: str = "end_turn"  # "end_turn" normally, "max_steps" if we cut it off


def run_tool_loop(
    user: str,
    system: str,
    tools: list[dict],
    handlers: dict[str, Callable[..., Any]],
    model: str | None = None,
    max_steps: int | None = None,
    max_tokens: int | None = None,
    on_event: Callable[[ToolEvent], None] | None = None,
) -> AgentRun:
    """
    Run the agent loop until the model gives a final answer or the step budget ends.

    tools     : JSON-schema descriptions of the tools the model may request
    handlers  : tool name -> Python function that really does the work
    on_event  : optional callback, called for every tool call/result (used to print a trace)
    """
    client = get_client()
    model = model or config.DEFAULT_MODEL
    max_steps = max_steps or config.AGENT_MAX_STEPS
    max_tokens = max_tokens or config.LLM_MAX_TOKENS

    messages: list[dict] = [{"role": "user", "content": user}]
    run = AgentRun(final_text="")

    def emit(event: ToolEvent) -> None:
        run.events.append(event)
        if on_event:
            on_event(event)

    for _step in range(max_steps):
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=messages,
        )
        run.input_tokens += response.usage.input_tokens
        run.output_tokens += response.usage.output_tokens

        # stop_reason == "tool_use" means: "I want you to run a tool and tell me the result".
        # Anything else means the model has finished and its text is the final answer.
        if response.stop_reason != "tool_use":
            run.final_text = _text_of(response.content)
            run.stopped_reason = response.stop_reason or "end_turn"
            return run

        # Keep the model's own turn in the history, exactly as received.
        messages.append({"role": "assistant", "content": response.content})

        # Run every tool the model asked for and collect the results.
        results = []
        for block in response.content:
            if getattr(block, "type", None) != "tool_use":
                continue
            emit(ToolEvent("tool_call", block.name, dict(block.input)))
            is_error = False
            try:
                handler = handlers[block.name]
                output = handler(**block.input)
            except Exception as exc:  # a bad tool call must not crash the whole agent
                output = {"error": f"{type(exc).__name__}: {exc}"}
                is_error = True
            emit(ToolEvent("tool_result", block.name, output))
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,  # ties the result to the request
                    "content": json.dumps(output, ensure_ascii=False),
                    "is_error": is_error,
                }
            )

        # Tool results go back to the model as a *user* message, then the loop repeats.
        messages.append({"role": "user", "content": results})

    # Step budget exhausted: stop rather than loop forever (cost + safety guard).
    run.final_text = "(Agent stopped: step budget exhausted before a final answer.)"
    run.stopped_reason = "max_steps"
    return run


# ----------------------------------------------------------------------------------
# 3. Token counting
# ----------------------------------------------------------------------------------
def count_tokens(text: str, model: str | None = None, system: str = "") -> int:
    """Exact number of input tokens the API would count for this text."""
    client = get_client()
    kwargs: dict[str, Any] = {
        "model": model or config.DEFAULT_MODEL,
        "messages": [{"role": "user", "content": text}],
    }
    if system:
        kwargs["system"] = system
    return client.messages.count_tokens(**kwargs).input_tokens


def estimate_tokens(text: str) -> int:
    """
    Offline rule of thumb: about 4 characters per token in English.
    Good enough to reason about limits; use count_tokens() for exact numbers.
    """
    return max(1, round(len(text) / 4))


# ----------------------------------------------------------------------------------
# 4. JSON extraction
# ----------------------------------------------------------------------------------
_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_json(text: str) -> Any:
    """
    Parse JSON from a model reply.

    Models often add a sentence before the JSON or wrap it in a ```json fence. We try
    the whole text first, then a fenced block, then the first {...} or [...] span.
    Raises ValueError if nothing parses - callers should treat that as "model did not
    follow the format" and fall back safely.
    """
    candidates = [text.strip()]
    candidates += [m.strip() for m in _FENCE.findall(text)]
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start, end = text.find(open_ch), text.rfind(close_ch)
        if start != -1 and end > start:
            candidates.append(text[start : end + 1])
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise ValueError(f"No valid JSON found in model reply: {text[:200]!r}")
