"""
types.py — All public types for claude-runner.

Flat, simple, developer-friendly. Mirrors the TypeScript package API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Awaitable, Callable, Literal, Protocol


# ─── MCP ─────────────────────────────────────────────────────────────────────

@dataclass
class McpServerConfig:
    """Full MCP server configuration."""
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)


@dataclass
class McpHttpConfig:
    """HTTP/SSE MCP server configuration."""
    url: str
    type: Literal["http", "sse"] = "http"
    headers: dict[str, str] = field(default_factory=dict)


McpConfig = McpServerConfig | McpHttpConfig | str


# ─── Permissions ─────────────────────────────────────────────────────────────

@dataclass
class PermissionRequest:
    """A tool permission request."""
    tool: str
    id: str
    description: str
    input: dict[str, Any] | None = None


@dataclass
class PermissionPolicy:
    """Fine-grained permission policy."""
    allow: list[str] = field(default_factory=list)
    deny: list[str] = field(default_factory=list)
    prompt: list[str] = field(default_factory=list)


# ─── Sandbox ─────────────────────────────────────────────────────────────────

@dataclass
class DockerConfig:
    """Docker sandbox configuration."""
    image: str = "node:22-slim"
    mount: list[str] = field(default_factory=list)
    network: str | None = None


@dataclass
class E2bConfig:
    """E2B cloud sandbox configuration."""
    api_key: str | None = None
    template: str | None = None
    timeout: int | None = None


# ─── Tools ───────────────────────────────────────────────────────────────────

@dataclass
class ToolDefinition:
    """A custom in-process tool definition."""
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., Awaitable[ToolResult]]
    _is_runner_tool: bool = field(default=True, repr=False)


@dataclass
class ToolResult:
    """Result from a tool execution."""
    content: list[dict[str, str]]


# ─── Runner Options ──────────────────────────────────────────────────────────

@dataclass
class RunnerOptions:
    """Configuration for the Runner."""
    api_key: str | None = None
    """Anthropic API key. When set, uses API Mode (no CLI needed)."""

    model: str | None = None
    """Model to use. Default: 'claude-sonnet-4-6'. Shorthands: opus, sonnet, haiku."""

    cwd: str | None = None
    """Working directory. Default: current directory."""

    system_prompt: str | None = None
    """System prompt for the agent."""

    mcp: dict[str, McpConfig] | None = None
    """MCP server configurations. Shorthand strings supported."""

    tools: list[ToolDefinition] | None = None
    """Custom tools that run in-process."""

    sandbox: Literal["local", "e2b", "docker"] | None = None
    """Execution environment. Default: 'local'."""

    docker: DockerConfig | None = None
    """Docker config (when sandbox='docker')."""

    e2b: E2bConfig | None = None
    """E2B config (when sandbox='e2b')."""

    permissions: Literal["auto", "prompt", "deny-unknown"] | PermissionPolicy | None = None
    """Permission handling. Default: 'deny-unknown'."""

    on_permission: Callable[[PermissionRequest], Awaitable[bool]] | None = None
    """Permission callback."""

    max_turns: int | None = None
    """Max agentic turns."""

    max_budget: float | None = None
    """Max cost in USD."""


# ─── Run Result ──────────────────────────────────────────────────────────────

@dataclass
class ToolCallSummary:
    """Summary of a tool call."""
    tool: str
    id: str
    duration: float


@dataclass
class RunResult:
    """Final result from a run."""
    text: str
    session_id: str
    cost: float
    duration: float
    usage: dict[str, int]
    turns: int
    tool_calls: list[ToolCallSummary] = field(default_factory=list)
    error: str | None = None


# ─── Run Events ──────────────────────────────────────────────────────────────

@dataclass
class TextEvent:
    type: Literal["text"] = "text"
    text: str = ""

@dataclass
class ToolStartEvent:
    type: Literal["tool_start"] = "tool_start"
    tool: str = ""
    id: str = ""
    input: dict[str, Any] | None = None

@dataclass
class ToolEndEvent:
    type: Literal["tool_end"] = "tool_end"
    tool: str = ""
    id: str = ""
    duration: float = 0

@dataclass
class SessionInitEvent:
    type: Literal["session_init"] = "session_init"
    session_id: str = ""
    model: str = ""
    tools: list[str] = field(default_factory=list)

@dataclass
class McpStatusEvent:
    type: Literal["mcp_status"] = "mcp_status"
    server: str = ""
    status: str = ""

@dataclass
class ErrorEvent:
    type: Literal["error"] = "error"
    message: str = ""
    code: str | None = None

@dataclass
class DoneEvent:
    type: Literal["done"] = "done"
    result: RunResult | None = None


RunEvent = TextEvent | ToolStartEvent | ToolEndEvent | SessionInitEvent | McpStatusEvent | ErrorEvent | DoneEvent
