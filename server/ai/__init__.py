"""Patrick's AI provider layer.

Providers generate responses from supplied context ONLY. They never perform
retrieval; the KnowledgeManager is responsible for gathering context. This keeps
the model fully swappable without touching retrieval logic.
"""

from .base import AiProvider, AiResponse
from .gemma import GemmaProvider
from .openai_compatible import OpenAiCompatibleProvider
from .local_openai import LocalOpenAIProvider
from .factory import build_provider

__all__ = [
    "AiProvider",
    "AiResponse",
    "GemmaProvider",
    "OpenAiCompatibleProvider",
    "LocalOpenAIProvider",
    "build_provider",
]
