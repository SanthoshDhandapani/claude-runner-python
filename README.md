# claude-runner

[![PyPI version](https://img.shields.io/pypi/v/claude-runner.svg)](https://pypi.org/project/claude-runner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

**The easiest way to build AI agents with Claude in Python.** 5 lines to start.

The official SDK is an engine 🔧 — claude-runner is the car 🚗.

A thin, clean wrapper around the Anthropic SDK. Zero required dependencies.

```python
from claude_runner import Runner

runner = Runner(api_key="sk-ant-...")
result = await runner.run("Analyze this codebase and suggest improvements")
print(result.text)
```

Also available as a [TypeScript/npm package](https://github.com/SanthoshDhandapani/claude-runner).

## Install

```bash
# API Mode — no CLI needed, deploys anywhere
pip install claude-runner[api]

# Agent Mode — full Claude Code power (needs CLI)
pip install claude-runner[agent]

# Everything
pip install claude-runner[all]
```

## Quick Start

### Simple await

```python
import asyncio
from claude_runner import Runner

async def main():
    runner = Runner(api_key="sk-ant-...")
    result = await runner.run("Fix the failing tests in this project")

    print(result.text)
    print(f"Cost: ${result.cost:.4f}")
    print(f"Turns: {result.turns}")

asyncio.run(main())
```

### Streaming

```python
async for event in runner.stream("Refactor the auth module"):
    match event.type:
        case "text":
            print(event.text, end="", flush=True)
        case "tool_start":
            print(f"  → {event.tool}")
        case "tool_end":
            print(f"  ← {event.tool} ({event.duration:.0f}ms)")
        case "done":
            print(f"\nCost: ${event.result.cost:.4f}")
```

### Custom Tools

```python
from claude_runner import Runner, define_tool, ToolResult

async def get_weather(city: str) -> ToolResult:
    return ToolResult(content=[{"type": "text", "text": f"72°F and sunny in {city}"}])

weather = define_tool(
    "get_weather",
    "Get current weather for a city",
    {"city": {"type": "string"}},
    get_weather,
)

runner = Runner(api_key="sk-ant-...", tools=[weather])
result = await runner.run("What's the weather in San Francisco?")
```

## CLI

```bash
# With API key
ANTHROPIC_API_KEY=sk-xxx claude-runner "Analyze this codebase"
claude-runner --api-key sk-xxx "Fix the tests"

# Choose model
claude-runner -m opus "Refactor the auth module"

# JSON output
claude-runner --json "What files are in this project?"
```

## API Mode vs Agent Mode

| | API Mode | Agent Mode |
|---|---|---|
| **Requires** | API key only | Claude CLI |
| **Built-in tools** | Bring your own | Read, Write, Bash, Edit |
| **Custom tools** | `define_tool()` | `define_tool()` |
| **Deploys to** | Anywhere | Machines with CLI |
| **Cost model** | Pay-per-token | Claude subscription |

## Models

```python
Runner(model="opus")       # claude-opus-4-6
Runner(model="sonnet")     # claude-sonnet-4-6
Runner(model="haiku")      # claude-haiku-4-5
Runner(model="opus-4.5")   # claude-opus-4-5-20250918
Runner(model="sonnet-4.5") # claude-sonnet-4-5-20250514
```

## Real-World Use Cases

### FastAPI endpoint

```python
@app.post("/chat")
async def chat(message: str):
    runner = Runner(api_key=os.environ["ANTHROPIC_API_KEY"])
    result = await runner.run(message)
    return {"reply": result.text, "cost": result.cost}
```

### Data analysis

```python
runner = Runner(api_key=key, model="haiku")
result = await runner.run(f"Analyze this CSV:\n{csv_data}")
```

### Slack bot

```python
@app.event("message")
async def handle(event):
    runner = Runner(api_key=key, tools=[search_docs, query_db])
    result = await runner.run(event["text"])
    await say(result.text)
```

## Examples

| Example | Description | Run |
|---|---|---|
| [Code Reviewer](./examples/code_reviewer.py) | Reviews codebase for bugs | `python examples/code_reviewer.py` |
| [Chatbot](./examples/chatbot.py) | Chat with custom tools | `python examples/chatbot.py` |
| [FastAPI Agent](./examples/fastapi_agent.py) | REST API endpoint | `uvicorn examples.fastapi_agent:app` |

## API Reference

### `Runner`

```python
class Runner:
    def __init__(self, **kwargs) -> None
    async def run(self, prompt: str) -> RunResult
    async def stream(self, prompt: str) -> AsyncIterator[RunEvent]
    @property
    def last_session_id(self) -> str | None
```

### `RunResult`

```python
@dataclass
class RunResult:
    text: str
    session_id: str
    cost: float          # USD
    duration: float      # ms
    usage: dict          # {"input": N, "output": N}
    turns: int
    tool_calls: list[ToolCallSummary]
    error: str | None
```

### `RunEvent` types

| Type | Fields | When |
|---|---|---|
| `text` | `text` | Each streamed chunk |
| `tool_start` | `tool`, `id`, `input` | Tool begins |
| `tool_end` | `tool`, `id`, `duration` | Tool ends |
| `session_init` | `session_id`, `model`, `tools` | Session started |
| `error` | `message`, `code` | Error occurred |
| `done` | `result` | Run complete |

### `RunnerOptions`

| Option | Type | Default | Description |
|---|---|---|---|
| `api_key` | `str` | — | Anthropic API key (enables API Mode) |
| `model` | `str` | `sonnet` | Model shorthand or full ID |
| `system_prompt` | `str` | — | System prompt |
| `tools` | `list` | — | Custom tools via `define_tool()` |
| `mcp` | `dict` | — | MCP servers (shorthand strings supported) |
| `permissions` | `str` | `deny-unknown` | `auto`, `prompt`, `deny-unknown` |
| `max_turns` | `int` | 50 | Max agentic turns |
| `max_budget` | `float` | — | Max cost in USD |

## Links

- **TypeScript version:** [github.com/SanthoshDhandapani/claude-runner](https://github.com/SanthoshDhandapani/claude-runner)
- **npm:** [npmjs.com/package/claude-runner](https://www.npmjs.com/package/claude-runner)

## License

MIT
