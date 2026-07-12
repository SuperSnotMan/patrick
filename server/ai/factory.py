from __future__ import annotations

import os

from .base import AiProvider
from .gemma import GemmaProvider
from .openai_compatible import OpenAiCompatibleProvider


def build_provider() -> AiProvider:
    """Construct the active AI provider.

    Default is the local Gemma 3 1B model. If it is unavailable (not running)
    and a remote model is configured via .env, fall back to the
    OpenAI-compatible provider. Retrieval is never part of this decision.
    """
    gemma = GemmaProvider()
    if gemma.is_available():
        return gemma

    remote = OpenAiCompatibleProvider()
    if remote.is_available():
        return remote

    # Prefer the local default even if not yet running; callers surface the
    # unavailability clearly rather than silently using a remote model.
    return gemma