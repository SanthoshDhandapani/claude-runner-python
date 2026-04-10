"""
models.py — Model shorthand resolver.

Accepts friendly names like 'sonnet', 'opus', 'haiku'
and resolves to the full model ID.
"""

MODEL_ALIASES: dict[str, str] = {
    # Claude 4.6 (latest)
    "opus": "claude-opus-4-6",
    "opus-4.6": "claude-opus-4-6",
    "sonnet": "claude-sonnet-4-6",
    "sonnet-4.6": "claude-sonnet-4-6",
    # Claude 4.5
    "opus-4.5": "claude-opus-4-5-20250918",
    "sonnet-4.5": "claude-sonnet-4-5-20250514",
    "haiku": "claude-haiku-4-5-20251001",
    "haiku-4.5": "claude-haiku-4-5-20251001",
}


def resolve_model(model: str | None) -> str | None:
    """Resolve a model shorthand to the full model ID."""
    if not model:
        return None
    return MODEL_ALIASES.get(model.lower(), model)
