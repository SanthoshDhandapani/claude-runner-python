from claude_runner import Runner


def test_create_default():
    runner = Runner()
    assert runner.last_session_id is None


def test_create_with_api_key():
    runner = Runner(api_key="sk-test", model="sonnet")
    assert runner.options.api_key == "sk-test"
    assert runner.last_session_id is None


def test_create_with_options():
    runner = Runner(
        model="opus",
        max_turns=10,
        max_budget=5.0,
        permissions="auto",
    )
    assert runner.options.model == "opus"
    assert runner.options.max_turns == 10
