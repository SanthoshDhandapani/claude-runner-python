"""
claude-runner — The easiest way to build AI agents with Claude.

Example::

    from claude_runner import Runner

    runner = Runner(api_key="sk-ant-...")
    result = await runner.run("Analyze this codebase")
    print(result.text)
"""

from .runner import Runner
from .api_runner import ApiRunner
from .tools import define_tool
from .models import resolve_model
from .types import (
    RunnerOptions,
    RunResult,
    RunEvent,
    TextEvent,
    ToolStartEvent,
    ToolEndEvent,
    SessionInitEvent,
    McpStatusEvent,
    ErrorEvent,
    DoneEvent,
    ToolDefinition,
    ToolResult,
    ToolCallSummary,
    McpServerConfig,
    McpHttpConfig,
    McpConfig,
    PermissionRequest,
    PermissionPolicy,
    DockerConfig,
    E2bConfig,
)

__all__ = [
    "Runner",
    "ApiRunner",
    "define_tool",
    "resolve_model",
    "RunnerOptions",
    "RunResult",
    "RunEvent",
    "TextEvent",
    "ToolStartEvent",
    "ToolEndEvent",
    "SessionInitEvent",
    "McpStatusEvent",
    "ErrorEvent",
    "DoneEvent",
    "ToolDefinition",
    "ToolResult",
    "ToolCallSummary",
    "McpServerConfig",
    "McpHttpConfig",
    "McpConfig",
    "PermissionRequest",
    "PermissionPolicy",
    "DockerConfig",
    "E2bConfig",
]

__version__ = "0.1.1"
