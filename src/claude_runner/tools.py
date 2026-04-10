"""
tools.py — define_tool() helper for creating custom in-process tools.
"""

from typing import Any, Awaitable, Callable

from .types import ToolDefinition, ToolResult


def define_tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    handler: Callable[..., Awaitable[ToolResult]],
) -> ToolDefinition:
    """
    Define a custom tool that runs in-process.

    Example::

        weather = define_tool(
            "get_weather",
            "Get current weather for a city",
            {"city": {"type": "string"}},
            get_weather_handler,
        )
    """
    return ToolDefinition(
        name=name,
        description=description,
        input_schema=input_schema,
        handler=handler,
    )
