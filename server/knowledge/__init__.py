"""Patrick's retrieval layer.

Knowledge sources are pluggable backends (local notes, Patrick Server, the
internet, a local cache). The KnowledgeManager decides *when* to consult each
one; the AI provider never retrieves and only consumes the merged result.
"""

from .base import KnowledgeSource, RetrievedKnowledge, RetrievalContext
from .manager import KnowledgeManager
from .local_notes import LocalNotesSource
from .patrick_server import PatrickServerSource
from .internet import InternetSearchSource
from .cache import CachedResultsSource

__all__ = [
    "KnowledgeSource",
    "RetrievedKnowledge",
    "RetrievalContext",
    "KnowledgeManager",
    "LocalNotesSource",
    "PatrickServerSource",
    "InternetSearchSource",
    "CachedResultsSource",
]