"""
Example: Simple Chatbot with Custom Tools

Usage:
    ANTHROPIC_API_KEY=sk-xxx python examples/chatbot.py
"""

import asyncio
import os

from claude_runner import Runner, define_tool, ToolResult


async def get_weather(city: str) -> ToolResult:
    """Simulated weather lookup."""
    return ToolResult(content=[{"type": "text", "text": f'{{"city": "{city}", "temp": "72F", "condition": "sunny"}}'}])


async def lookup_user(email: str) -> ToolResult:
    """Simulated user lookup."""
    return ToolResult(content=[{"type": "text", "text": f'{{"email": "{email}", "name": "Alice", "plan": "pro"}}'}])


weather_tool = define_tool(
    "get_weather",
    "Get current weather for a city",
    {"city": {"type": "string", "description": "City name"}},
    get_weather,
)

user_tool = define_tool(
    "lookup_user",
    "Look up a user by email",
    {"email": {"type": "string", "description": "Email address"}},
    lookup_user,
)


async def main():
    runner = Runner(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        model="sonnet",
        tools=[weather_tool, user_tool],
        system_prompt="You are a helpful assistant with access to weather and user lookup tools.",
    )

    prompts = [
        "What's the weather in San Francisco?",
        "Look up the user alice@example.com",
    ]

    for prompt in prompts:
        print(f"\n💬 {prompt}\n")
        async for event in runner.stream(prompt):
            if event.type == "text":
                print(event.text, end="", flush=True)
            elif event.type == "tool_start":
                print(f"  → {event.tool}", flush=True)
            elif event.type == "tool_end":
                print(f"  ← {event.tool} ({event.duration:.0f}ms)", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())
