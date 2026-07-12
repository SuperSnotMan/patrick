from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(slots=True)
class AiResponse:
    """A generated answer plus the transparency metadata shown to the user."""

    summary: str = ""
    sources_used: list[str] = field(default_factory=list)


class AiProvider(ABC):
    """Generates a response strictly from supplied context.

    Implementations must NOT search the web, read the vault, or call any
    knowledge source. All context arrives via `generate`.
    """

    # Stable id, e.g. "gemma3-1b", "openrouter:poolside/...".
    id: str = "provider"

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the model can be reached/loaded right now."""

    @abstractmethod
    def generate(self, prompt: str, context: str) -> str:
        """Produce a reply using only `prompt` + `context`."""