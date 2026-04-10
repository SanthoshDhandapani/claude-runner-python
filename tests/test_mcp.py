from claude_runner.mcp import normalize_mcp_config
from claude_runner.types import McpServerConfig, McpHttpConfig


def test_command_shorthand():
    result = normalize_mcp_config({"github": "npx @mcp/server-github"})
    cfg = result["github"]
    assert isinstance(cfg, McpServerConfig)
    assert cfg.command == "npx"
    assert cfg.args == ["@mcp/server-github"]


def test_command_with_args():
    result = normalize_mcp_config({"db": "npx @mcp/postgres --host localhost"})
    cfg = result["db"]
    assert isinstance(cfg, McpServerConfig)
    assert cfg.args == ["@mcp/postgres", "--host", "localhost"]


def test_https_url():
    result = normalize_mcp_config({"api": "https://api.example.com/mcp"})
    cfg = result["api"]
    assert isinstance(cfg, McpHttpConfig)
    assert cfg.url == "https://api.example.com/mcp"


def test_http_url():
    result = normalize_mcp_config({"local": "http://localhost:3000/mcp"})
    cfg = result["local"]
    assert isinstance(cfg, McpHttpConfig)


def test_object_passthrough():
    config = McpServerConfig(command="node", args=["server.js"], env={"TOKEN": "abc"})
    result = normalize_mcp_config({"custom": config})
    assert result["custom"] is config


def test_multiple_servers():
    result = normalize_mcp_config({
        "github": "npx @mcp/github",
        "api": "https://example.com/mcp",
        "custom": McpServerConfig(command="node", args=["s.js"]),
    })
    assert len(result) == 3


def test_empty():
    assert normalize_mcp_config({}) == {}
