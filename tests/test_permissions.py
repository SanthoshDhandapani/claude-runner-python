from claude_runner.permissions import check_permission
from claude_runner.types import PermissionPolicy


def test_auto_allows_all():
    assert check_permission("Bash", {}, "auto") == "allow"
    assert check_permission("rm_everything", {}, "auto") == "allow"


def test_deny_unknown_allows_safe():
    for tool in ["Read", "Write", "Edit", "Glob", "Grep", "Agent", "Skill", "ToolSearch"]:
        assert check_permission(tool, {}, "deny-unknown") == "allow"


def test_deny_unknown_allows_mcp():
    assert check_permission("mcp__github__list_issues", {}, "deny-unknown") == "allow"


def test_deny_unknown_denies_unknown():
    assert check_permission("Bash", {}, "deny-unknown") == "deny"


def test_prompt_mode():
    assert check_permission("Bash", {}, "prompt") == "prompt"


def test_policy_deny():
    policy = PermissionPolicy(allow=["*"], deny=["Bash"])
    assert check_permission("Bash", {}, policy) == "deny"


def test_policy_allow():
    policy = PermissionPolicy(allow=["Read", "mcp__github__*"])
    assert check_permission("Read", {}, policy) == "allow"
    assert check_permission("mcp__github__list", {}, policy) == "allow"


def test_policy_prompt():
    policy = PermissionPolicy(prompt=["Bash"])
    assert check_permission("Bash", {}, policy) == "prompt"


def test_policy_deny_unmatched():
    policy = PermissionPolicy(allow=["Read"])
    assert check_permission("Write", {}, policy) == "deny"
