"""
cli.py — Claude Runner CLI.

Run AI agents from the command line:
  claude-runner "Analyze this codebase"
  claude-runner --model opus "Fix the tests"
  claude-runner --api-key sk-xxx "Summarize this data"
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from .runner import Runner


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="claude-runner",
        description="The easiest way to build AI agents with Claude.",
    )
    parser.add_argument("prompt", nargs="?", help="The prompt to run")
    parser.add_argument("--model", "-m", default=None, help="Model shorthand or full ID (default: sonnet)")
    parser.add_argument("--api-key", default=None, help="Anthropic API key (or set ANTHROPIC_API_KEY)")
    parser.add_argument("--permissions", "-p", default="prompt", choices=["auto", "prompt", "deny-unknown"])
    parser.add_argument("--system", default=None, help="Custom system prompt")
    parser.add_argument("--max-turns", type=int, default=None, help="Max agentic turns")
    parser.add_argument("--max-budget", type=float, default=None, help="Max cost in USD")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    if not args.prompt:
        parser.print_help()
        sys.exit(0)

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")

    runner = Runner(
        api_key=api_key,
        model=args.model,
        system_prompt=args.system,
        permissions=args.permissions,
        max_turns=args.max_turns,
        max_budget=args.max_budget,
    )

    asyncio.run(_run(runner, args.prompt, args.json))


async def _run(runner: Runner, prompt: str, json_mode: bool) -> None:
    if json_mode:
        import json
        result = await runner.run(prompt)
        print(json.dumps({
            "text": result.text,
            "session_id": result.session_id,
            "cost": result.cost,
            "duration": result.duration,
            "usage": result.usage,
            "turns": result.turns,
            "tool_calls": [{"tool": tc.tool, "id": tc.id, "duration": tc.duration} for tc in result.tool_calls],
        }, indent=2))
        return

    async for event in runner.stream(prompt):
        if event.type == "text":
            print(event.text, end="", flush=True)
        elif event.type == "tool_start":
            print(f"\033[36m[{event.tool}]\033[0m ", end="", file=sys.stderr, flush=True)
        elif event.type == "tool_end":
            print(f"\033[36m({event.duration / 1000:.1f}s)\033[0m", file=sys.stderr)
        elif event.type == "session_init":
            pass  # silent
        elif event.type == "error":
            print(f"\033[31mError: {event.message}\033[0m", file=sys.stderr)
        elif event.type == "done" and event.result:
            r = event.result
            print(
                f"\n\033[90m— {r.turns} turns, ${r.cost:.4f}, "
                f"{r.usage.get('input', 0)}/{r.usage.get('output', 0)} tokens"
                f"\033[0m",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
