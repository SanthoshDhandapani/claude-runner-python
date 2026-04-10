import asyncio
from claude_runner.tools import define_tool
from claude_runner.types import ToolResult


async def _handler(**kwargs):
    return ToolResult(content=[{"type": "text", "text": "ok"}])


def test_define_tool():
    tool = define_tool("test", "A test tool", {"input": {}}, _handler)
    assert tool.name == "test"
    assert tool.description == "A test tool"
    assert tool._is_runner_tool is True


def test_handler_returns_result():
    tool = define_tool("greet", "Greet", {}, _handler)
    result = asyncio.run(tool.handler())
    assert result.content == [{"type": "text", "text": "ok"}]
