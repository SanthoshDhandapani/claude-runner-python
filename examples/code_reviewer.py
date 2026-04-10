"""
Example: AI Code Reviewer

Usage:
    ANTHROPIC_API_KEY=sk-xxx python examples/code_reviewer.py
"""

import asyncio
import os

from claude_runner import Runner


async def main():
    runner = Runner(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        model="sonnet",
        system_prompt="You are a senior code reviewer. Be concise.",
    )

    print("🔍 Starting code review...\n")

    async for event in runner.stream("Review this project for bugs, security issues, and code quality. 3 key findings only."):
        if event.type == "text":
            print(event.text, end="", flush=True)
        elif event.type == "done" and event.result:
            print(f"\n\n✅ Cost: ${event.result.cost:.4f} | Turns: {event.result.turns}")


if __name__ == "__main__":
    asyncio.run(main())
