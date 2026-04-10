"""
runner.py — The Runner class. The core of claude-runner.

5 lines to start:
    runner = Runner()
    result = await runner.run("Analyze this codebase")
    print(result.text)
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from .api_runner import ApiRunner
from .models import resolve_model
from .types import (
    DoneEvent,
    ErrorEvent,
    RunEvent,
    RunnerOptions,
    RunResult,
)


class Runner:
    """
    The main entry point for claude-runner.

    Supports two modes:
    - **API Mode**: Pass `api_key` — uses Anthropic Messages API directly. No CLI needed.
    - **Agent Mode**: No `api_key` — uses Claude Agent SDK (requires CLI installed).

    Example::

        # API Mode
        runner = Runner(api_key="sk-ant-...")
        result = await runner.run("Analyze this data")
        print(result.text)

        # Streaming
        async for event in runner.stream("Fix the tests"):
            if event.type == "text":
                print(event.text, end="")
    """

    def __init__(self, **kwargs: Any) -> None:
        self.options = RunnerOptions(**kwargs)
        self._last_session_id: str | None = None

    async def run(self, prompt: str) -> RunResult:
        """
        Run a prompt and return the complete result.

        Example::

            result = await runner.run("Fix the failing tests")
            print(result.text)
            print(f"Cost: ${result.cost:.4f}")
        """
        result: RunResult | None = None
        async for event in self.stream(prompt):
            if isinstance(event, DoneEvent) and event.result:
                result = event.result

        if result is None:
            raise RuntimeError("Agent run completed without a result")

        self._last_session_id = result.session_id
        return result

    async def stream(self, prompt: str) -> AsyncIterator[RunEvent]:
        """
        Stream a prompt and yield events in real time.

        Example::

            async for event in runner.stream("Refactor the auth module"):
                if event.type == "text":
                    print(event.text, end="")
                elif event.type == "tool_start":
                    print(f"  → {event.tool}")
                elif event.type == "done":
                    print(f"Cost: ${event.result.cost:.4f}")
        """
        opts = self.options

        if opts.api_key:
            # API Mode
            api_runner = ApiRunner(opts)
            async for event in api_runner.run(prompt):
                if isinstance(event, DoneEvent) and event.result:
                    self._last_session_id = event.result.session_id
                yield event
        else:
            # Agent Mode — requires claude-agent-sdk
            async for event in self._run_agent_mode(prompt):
                yield event

    async def _run_agent_mode(self, prompt: str) -> AsyncIterator[RunEvent]:
        """Run using the Claude Agent SDK (requires CLI)."""
        try:
            from claude_agent_sdk import query, ClaudeAgentOptions
        except ImportError:
            raise ImportError(
                "Agent Mode requires the 'claude-agent-sdk' package. "
                "Install it with: pip install claude-runner[agent]\n\n"
                "Or use API Mode instead:\n"
                "  runner = Runner(api_key='your-key')"
            )

        opts = self.options
        model = resolve_model(opts.model)

        options = ClaudeAgentOptions(
            system_prompt=opts.system_prompt or "",
            cwd=opts.cwd or ".",
            model=model,
            max_turns=opts.max_turns,
            permission_mode="bypassPermissions" if opts.permissions == "auto" else None,
        )

        async for message in query(prompt=prompt, options=options):
            # Basic event mapping — extend as needed
            msg = dict(message) if hasattr(message, "__iter__") else {"type": "unknown"}
            msg_type = msg.get("type", "")

            if msg_type == "assistant":
                content = msg.get("message", {}).get("content", [])
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        from .types import TextEvent
                        yield TextEvent(text=block["text"])

        yield ErrorEvent(message="Agent Mode event parsing is minimal — use API Mode for full support")

    @property
    def last_session_id(self) -> str | None:
        """Session ID from the last completed run."""
        return self._last_session_id
