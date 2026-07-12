from __future__ import annotations

import os
from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .base import KnowledgeSource, RetrievalContext

# Internet retrieval is opt-in via .env to avoid surprise network calls.
INTERNET_ENABLED = os.getenv("PATRICK_INTERNET", "false").strip().lower() in {
    "1", "true", "yes", "on"
}
INTERNET_TIMEOUT = float(os.getenv("PATRICK_INTERNET_TIMEOUT", "10"))


class InternetSearchSource(KnowledgeSource):
    """Best-effort web search used only when local and server sources are empty."""

    name = "internet"

    def is_available(self) -> bool:
        return INTERNET_ENABLED

    def retrieve(self, query: str, context: RetrievalContext) -> str:
        if not INTERNET_ENABLED:
            return ""
        return self._search(query)

    @staticmethod
    def _search(query: str) -> str:
        try:
            url = "https://html.duckduckgo.com/html/?q=" + quote(query)
            req = Request(url, headers={"User-Agent": "Patrick/0.1"})
            with urlopen(req, timeout=INTERNET_TIMEOUT) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            snippets: list[str] = []

            class SnippetParser(HTMLParser):
                def __init__(self) -> None:
                    super().__init__()
                    self.capture = False
                    self.buffer = ""

                def handle_starttag(self, tag, attrs):
                    if tag == "a" and ("result__snippet", "") in attrs:
                        self.capture = True
                        self.buffer = ""

                def handle_endtag(self, tag):
                    if self.capture and tag == "a":
                        self.capture = False
                        if self.buffer.strip():
                            snippets.append(self.buffer.strip())

                def handle_data(self, data):
                    if self.capture:
                        self.buffer += data

            SnippetParser().feed(html)
            return "\n".join(snippets[:5])
        except Exception as error:  # noqa: BLE001 - search is best-effort
            return f"(Internet search failed: {error})"