"""Thin wrapper around the Anthropic Claude API.

Degrades gracefully: when AI is disabled or the API key is missing, callers
receive a rule-based fallback string instead of an error. The model default is
the latest, most capable Claude model (see config.AI_MODEL).
"""
from __future__ import annotations

from app.config import settings
from app.logging_config import get_logger

log = get_logger("ai.client")


class AIClient:
    def __init__(self) -> None:
        self._client = None
        self._enabled = settings.ai_enabled and bool(settings.anthropic_api_key)
        if self._enabled:
            try:
                from anthropic import Anthropic

                self._client = Anthropic(api_key=settings.anthropic_api_key)
            except Exception as exc:  # noqa: BLE001  # pragma: no cover
                log.warning("Anthropic client init failed; AI disabled: %s", exc)
                self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    def complete(self, system: str, prompt: str, max_tokens: int = 600) -> str | None:
        if not self._enabled or self._client is None:
            return None
        try:
            msg = self._client.messages.create(
                model=settings.ai_model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            parts = [b.text for b in msg.content if getattr(b, "type", None) == "text"]
            return "\n".join(parts).strip()
        except Exception as exc:  # noqa: BLE001
            log.warning("AI completion failed: %s", exc)
            return None


_ai: AIClient | None = None


def get_ai() -> AIClient:
    global _ai
    if _ai is None:
        _ai = AIClient()
    return _ai
