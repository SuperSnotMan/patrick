from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

from .base import KnowledgeSource, RetrievalContext

# On-disk cache of previous retrieval results, keyed by a hash of the query
# plus the active note. Lets repeated questions reuse earlier context without
# re-hitting the vault, server, or internet.
CACHE_PATH = Path(
    os.environ.get(
        "PATRICK_CACHE_PATH",
        Path.home() / ".cache" / "patrick" / "retrieval_cache.json",
    )
)
CACHE_TTL_SECONDS = float(os.getenv("PATRICK_CACHE_TTL", "86400"))  # 24h default


class CachedResultsSource(KnowledgeSource):
    """Returns previously retrieved context for an identical query+note.

    Consulted first so that repeat questions are cheap and deterministic. The
    cache stores the *retrieved* text, never the model's answer.
    """

    name = "cache"

    def __init__(self, cache_path: Path = CACHE_PATH) -> None:
        self.cache_path = cache_path

    def is_available(self) -> bool:
        return self.cache_path.exists()

    def _key(self, query: str, context: RetrievalContext) -> str:
        raw = f"{query}|{context.vault_path}|{context.note_path}|{context.note_content}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _load(self) -> dict[str, object]:
        try:
            return json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def retrieve(self, query: str, context: RetrievalContext) -> str:
        store = self._load()
        entry = store.get(self._key(query, context))
        if not isinstance(entry, dict):
            return ""
        if time.time() - float(entry.get("ts", 0.0)) > CACHE_TTL_SECONDS:
            return ""
        value = entry.get("text", "")
        return value if isinstance(value, str) else ""

    def store(self, query: str, context: RetrievalContext, text: str) -> None:
        """Persist retrieved text so future identical queries hit the cache."""
        if not text.strip():
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        store = self._load()
        store[self._key(query, context)] = {"ts": time.time(), "text": text}
        self.cache_path.write_text(json.dumps(store), encoding="utf-8")