from __future__ import annotations

import os
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .base import KnowledgeSource, RetrievalContext

# Optional dedicated Patrick knowledge server (separate from the local Core API).
# When set, the manager consults it before falling back to the internet.
PATRICK_SERVER_URL = os.getenv("PATRICK_SERVER_URL", "").strip().rstrip("/")
PATRICK_SERVER_TIMEOUT = float(os.getenv("PATRICK_SERVER_TIMEOUT", "10"))


class PatrickServerSource(KnowledgeSource):
    """Retrieves knowledge from a dedicated Patrick Server over HTTP.

    This is a separate backend from the local Core API. It is only consulted
    when configured and reachable, keeping retrieval independent of the AI
    model and of the local vault.
    """

    name = "patrick_server"

    def __init__(self, base_url: str = PATRICK_SERVER_URL) -> None:
        self.base_url = base_url

    def is_available(self) -> bool:
        if not self.base_url:
            return False
        try:
            request = Request(self.base_url + "/", method="GET")
            with urlopen(request, timeout=3):
                return True
        except (URLError, OSError):
            return False

    def retrieve(self, query: str, context: RetrievalContext) -> str:
        if not self.base_url:
            return ""
        params = urlencode(
            {
                "q": query,
                "vault_path": context.vault_path,
                "note_title": context.note_title,
                "note_path": context.note_path,
            }
        )
        url = f"{self.base_url}/search?{params}"
        try:
            request = Request(url, headers={"User-Agent": "Patrick/0.1"}, method="GET")
            with urlopen(request, timeout=PATRICK_SERVER_TIMEOUT) as response:
                body = response.read().decode("utf-8", errors="ignore")
        except (URLError, OSError, ValueError) as error:
            return f"(Patrick Server request failed: {error})"
        return body.strip()