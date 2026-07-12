from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(slots=True)
class RetrievalContext:
    """Lightweight, serialisable description of the user's current note.

    Decouples retrieval from the HTTP/Pydantic models so sources can be tested
    and reused without importing server request types.
    """

    vault_path: str = ""
    note_title: str = ""
    note_path: str = ""
    note_content: str = ""
    selection: str = ""


@dataclass(slots=True)
class RetrievedKnowledge:
    """The complete, merged context handed to the AI provider.

    The AI provider receives ONLY this object. It never performs retrieval
    itself; every byte of context originates from a KnowledgeSource below.
    """

    notes: str = ""
    server: str = ""
    internet: str = ""
    cache: str = ""
    sources_used: list[str] = field(default_factory=list)

    def merge_text(self) -> str:
        """Flatten all retrieved material into a single labelled block."""
        parts: list[str] = []
        if self.notes.strip():
            parts.append(f"## My Notes\n{self.notes.strip()}")
        if self.server.strip():
            parts.append(f"## Patrick Server\n{self.server.strip()}")
        if self.internet.strip():
            parts.append(f"## Internet\n{self.internet.strip()}")
        if self.cache.strip():
            parts.append(f"## Cached Results\n{self.cache.strip()}")
        return "\n\n".join(parts)

    def has_content(self) -> bool:
        return any(
            source.strip()
            for source in (self.notes, self.server, self.internet, self.cache)
        )


class KnowledgeSource(ABC):
    """A pluggable retrieval backend.

    Implementations decide *how* to fetch knowledge. The KnowledgeManager
    decides *when* to use them. Adding a new source never requires touching the
    AI provider or the manager's merge logic beyond registration.
    """

    # Stable identifier used in transparency reporting and source lists.
    name: str = "source"

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this source can be queried right now."""

    @abstractmethod
    def retrieve(self, query: str, context: RetrievalContext) -> str:
        """Return retrieved material as plain text (may be empty)."""