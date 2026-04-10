"""
api_runner.py — Anthropic Messages API runner.

Uses the `anthropic` SDK directly. No CLI needed — just an API key.
Implements an agentic tool loop:
  1. Send messages to Claude
  2. If Claude requests tool_use → execute tool → send tool_result
  3. Repeat until stop_reason is "end_turn" or max turns reached
"""

from __future__ import annotations

import asyncio
import random
import string
import time
from typing import Any, AsyncIterator

from .models import resolve_model
from .types import (
    DoneEvent,
    ErrorEvent,
    RunEvent,
    RunResult,
    RunnerOptions,
    SessionInitEvent,
    TextEvent,
    ToolCallSummary,
    ToolEndEvent,
    ToolStartEvent,
)

# Approximate pricing per million tokens
PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-6": {"input": 15, "output": 75},
    "claude-opus-4-5-20250918": {"input": 15, "output": 75},
    "claude-sonnet-4-6": {"input": 3, "output": 15},
    "claude-sonnet-4-5-20250514": {"input": 3, "output": 15},
    "claude-haiku-4-5-20251001": {"input": 0.8, "output": 4},
}


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    price = PRICING.get(model, {"input": 3, "output": 15})
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1_000_000


def _random_id(prefix: str = "api") -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}-{int(time.time())}-{suffix}"


class ApiRunner:
    """Runs Claude agents using the raw Anthropic Messages API."""

    def __init__(self, options: RunnerOptions) -> None:
        self.options = options
        self._aborted = False

    async def run(self, prompt: str) -> AsyncIterator[RunEvent]:
        """Run a prompt and yield events."""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "API Mode requires the 'anthropic' package. "
                "Install it with: pip install claude-runner[api]"
            )

        opts = self.options
        client = anthropic.AsyncAnthropic(api_key=opts.api_key)
        model = resolve_model(opts.model) or "claude-sonnet-4-6"
        max_turns = opts.max_turns or 50

        # Build tool specs + handlers
        tool_specs: list[dict[str, Any]] = []
        tool_handlers: dict[str, Any] = {}

        for tool in opts.tools or []:
            if getattr(tool, "_is_runner_tool", False):
                tool_specs.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": {
                        "type": "object",
                        "properties": tool.input_schema,
                    },
                })
                tool_handlers[tool.name] = tool.handler

        # Messages history
        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]

        # Metrics
        start_ms = time.time() * 1000
        total_input = 0
        total_output = 0
        turns = 0
        full_text = ""
        tool_calls: list[ToolCallSummary] = []
        session_id = _random_id()

        # Emit session init
        yield SessionInitEvent(
            session_id=session_id,
            model=model,
            tools=[t["name"] for t in tool_specs],
        )

        # Agentic loop
        for _ in range(max_turns):
            if self._aborted:
                break

            # Budget check
            cost_so_far = _estimate_cost(model, total_input, total_output)
            if opts.max_budget and cost_so_far >= opts.max_budget:
                yield ErrorEvent(message=f"Budget exceeded: ${cost_so_far:.4f} >= ${opts.max_budget}")
                break

            turns += 1

            # Build request
            request: dict[str, Any] = {
                "model": model,
                "max_tokens": 8192,
                "messages": messages,
            }
            if opts.system_prompt:
                request["system"] = opts.system_prompt
            if tool_specs:
                request["tools"] = tool_specs

            # Stream response
            assistant_content: list[dict[str, Any]] = []
            stop_reason = ""

            async with client.messages.stream(**request) as stream:
                async for text in stream.text_stream:
                    if self._aborted:
                        break
                    full_text += text
                    yield TextEvent(text=text)

                response = await stream.get_final_message()
                stop_reason = response.stop_reason
                # Serialize content blocks — only keep API-safe fields
                for block in response.content:
                    if block.type == "text":
                        assistant_content.append({"type": "text", "text": block.text})
                    elif block.type == "tool_use":
                        assistant_content.append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        })

                # Track usage
                if response.usage:
                    total_input += response.usage.input_tokens
                    total_output += response.usage.output_tokens

            # Emit tool_start events
            for block in assistant_content:
                if block.get("type") == "tool_use":
                    yield ToolStartEvent(
                        tool=block["name"],
                        id=block["id"],
                        input=block.get("input"),
                    )

            # Add assistant message to history
            messages.append({"role": "assistant", "content": assistant_content})

            # If no tool calls, we're done
            if stop_reason != "tool_use":
                break

            # Execute tool calls
            tool_results: list[dict[str, Any]] = []

            for block in assistant_content:
                if block.get("type") != "tool_use":
                    continue

                tool_name = block["name"]
                tool_id = block["id"]
                tool_input = block.get("input", {})
                tool_start = time.time() * 1000

                handler = tool_handlers.get(tool_name)
                if not handler:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": f"Error: Unknown tool '{tool_name}'",
                    })
                else:
                    try:
                        result = await handler(**tool_input)
                        result_text = "\n".join(
                            c.get("text", f"[{c.get('type')}]")
                            for c in result.content
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": result_text,
                        })
                    except Exception as e:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": f"Error: {e}",
                        })

                elapsed = time.time() * 1000 - tool_start
                tool_calls.append(ToolCallSummary(tool=tool_name, id=tool_id, duration=elapsed))
                yield ToolEndEvent(tool=tool_name, id=tool_id, duration=elapsed)

            # Send tool results
            messages.append({"role": "user", "content": tool_results})

        # Final result
        total_cost = _estimate_cost(model, total_input, total_output)
        result = RunResult(
            text=full_text,
            session_id=session_id,
            cost=total_cost,
            duration=time.time() * 1000 - start_ms,
            usage={"input": total_input, "output": total_output},
            turns=turns,
            tool_calls=tool_calls,
        )

        yield DoneEvent(result=result)

    def abort(self) -> None:
        """Stop the running agent."""
        self._aborted = True
