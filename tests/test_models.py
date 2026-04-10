from claude_runner.models import resolve_model


def test_opus_shorthand():
    assert resolve_model("opus") == "claude-opus-4-6"


def test_sonnet_shorthand():
    assert resolve_model("sonnet") == "claude-sonnet-4-6"


def test_haiku_shorthand():
    assert resolve_model("haiku") == "claude-haiku-4-5-20251001"


def test_version_specific():
    assert resolve_model("opus-4.5") == "claude-opus-4-5-20250918"
    assert resolve_model("sonnet-4.5") == "claude-sonnet-4-5-20250514"
    assert resolve_model("opus-4.6") == "claude-opus-4-6"
    assert resolve_model("sonnet-4.6") == "claude-sonnet-4-6"


def test_case_insensitive():
    assert resolve_model("OPUS") == "claude-opus-4-6"
    assert resolve_model("Sonnet") == "claude-sonnet-4-6"


def test_passthrough():
    assert resolve_model("claude-opus-4-6") == "claude-opus-4-6"
    assert resolve_model("custom-model") == "custom-model"


def test_none():
    assert resolve_model(None) is None
    assert resolve_model("") is None
