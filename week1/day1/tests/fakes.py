"""
tests/fakes.py
==============
A scripted stand-in for the Anthropic SDK client, so the tests run offline, for free,
and give the same result every time.

FakeClient.messages.create() returns the next prepared response. Each response looks
like the real SDK object closely enough for common/llm.py (content blocks, stop_reason,
usage, model).
"""
from __future__ import annotations

from types import SimpleNamespace


def text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def tool_block(name: str, tool_input: dict, block_id: str = "tu_1"):
    return SimpleNamespace(type="tool_use", name=name, input=tool_input, id=block_id)


def response(blocks, stop_reason="end_turn", tokens=(10, 5), model="fake-model"):
    return SimpleNamespace(content=blocks, stop_reason=stop_reason, model=model,
                           usage=SimpleNamespace(input_tokens=tokens[0], output_tokens=tokens[1]))


class FakeMessages:
    def __init__(self, scripted):
        self.scripted = list(scripted)
        self.calls = []                      # every kwargs dict the code passed in

    def create(self, **kwargs):
        # Copy the message list: the real code keeps appending to it after the call.
        self.calls.append({**kwargs, "messages": list(kwargs.get("messages", []))})
        if not self.scripted:
            raise AssertionError("FakeClient ran out of scripted responses")
        return self.scripted.pop(0)

    def count_tokens(self, **kwargs):
        return SimpleNamespace(input_tokens=42)


class FakeClient:
    def __init__(self, scripted):
        self.messages = FakeMessages(scripted)
