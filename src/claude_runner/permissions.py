"""
permissions.py — Permission policy adapter.

Translates simple permission modes into tool approval logic.
"""

import fnmatch
from typing import Any

from .types import PermissionPolicy, PermissionRequest

SAFE_TOOLS = {"Read", "Glob", "Grep", "Write", "Edit", "Agent", "Skill", "ToolSearch"}


def check_permission(
    tool_name: str,
    tool_input: dict[str, Any],
    permissions: str | PermissionPolicy,
) -> str:
    """
    Check if a tool is allowed.

    Returns: "allow", "deny", or "prompt"
    """
    if permissions == "auto":
        return "allow"

    if permissions == "deny-unknown":
        if tool_name in SAFE_TOOLS or tool_name.startswith("mcp__"):
            return "allow"
        return "deny"

    if permissions == "prompt":
        return "prompt"

    if isinstance(permissions, PermissionPolicy):
        for pattern in permissions.deny:
            if _match_pattern(pattern, tool_name):
                return "deny"
        for pattern in permissions.allow:
            if _match_pattern(pattern, tool_name):
                return "allow"
        for pattern in permissions.prompt:
            if _match_pattern(pattern, tool_name):
                return "prompt"
        return "deny"

    return "deny"


def _match_pattern(pattern: str, tool_name: str) -> bool:
    """Match a tool name against a pattern (supports * wildcards)."""
    if pattern == "*":
        return True
    return fnmatch.fnmatch(tool_name, pattern)
