"""
mcp.py — MCP config normalization.

Accepts shorthand strings and normalizes to SDK-compatible format.
  'npx @mcp/server arg1'       → McpServerConfig(command='npx', args=['@mcp/server', 'arg1'])
  'https://api.example.com/mcp' → McpHttpConfig(url='...')
"""

from .types import McpConfig, McpHttpConfig, McpServerConfig


def normalize_mcp_config(
    configs: dict[str, McpConfig],
) -> dict[str, McpServerConfig | McpHttpConfig]:
    """Normalize MCP configs from shorthands to full objects."""
    result: dict[str, McpServerConfig | McpHttpConfig] = {}

    for name, config in configs.items():
        if isinstance(config, str):
            if config.startswith("http://") or config.startswith("https://"):
                result[name] = McpHttpConfig(url=config)
            else:
                parts = config.split()
                result[name] = McpServerConfig(
                    command=parts[0],
                    args=parts[1:],
                )
        else:
            result[name] = config

    return result
