from __future__ import annotations

from .base import (
    KnowledgeSource,
    RetrievedKnowledge,
    RetrievalContext,
)
from .local_notes import LocalNotesSource
from .patrick_server import PatrickServerSource
from .internet import InternetSearchSource
from .cache import CachedResultsSource


class KnowledgeManager:
    """Decides which knowledge sources to consult and merges their results.

    Priority for every prompt:
        1. Local Notes (always)
        2. Patrick Server (if available)
        3. Internet (if available)
        4. Cached Results (consulted first for repeat queries)

    The manager returns a single RetrievedKnowledge object. The AI provider
    receives ONLY that object and never performs retrieval itself.
    """

    def __init__(
        self,
        local: KnowledgeSource | None = None,
        server: KnowledgeSource | None = None,
        internet: KnowledgeSource | None = None,
        cache: CachedResultsSource | None = None,
    ) -> None:
        self.local = local or LocalNotesSource()
        self.server = server or PatrickServerSource()
        self.internet = internet or InternetSearchSource()
        self.cache = cache or CachedResultsSource()

    def retrieve(self, query: str, context: RetrievalContext) -> RetrievedKnowledge:
        knowledge = RetrievedKnowledge()

        # 1. Local notes are always the foundation.
        notes = self.local.retrieve(query, context)
        if notes.strip():
            knowledge.notes = notes
            knowledge.sources_used.append(self.local.name)

        # 4. Cache: reuse previously merged retrieval for this exact query+note.
        cached = self.cache.retrieve(query, context)
        if cached.strip():
            knowledge.cache = cached
            knowledge.sources_used.append(self.cache.name)

        # 2. Patrick Server, only if reachable.
        if self.server.is_available():
            server_text = self.server.retrieve(query, context)
            if server_text.strip():
                knowledge.server = server_text
                knowledge.sources_used.append(self.server.name)

        # 3. Internet, only if enabled and the above were insufficient.
        if not knowledge.has_content() or not knowledge.server.strip():
            if self.internet.is_available():
                internet_text = self.internet.retrieve(query, context)
                if internet_text.strip():
                    knowledge.internet = internet_text
                    knowledge.sources_used.append(self.internet.name)

        return knowledge