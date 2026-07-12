from __future__ import annotations

import os

from openai import OpenAI

from .base import AiProvider


class OpenAiCompatibleProvider(AiProvider):
    """Remote/OpenAI-compatible provider (e.g. OpenRouter).

    Used as a fallback when the local Gemma model is unavailable. Like every
    provider it only generates from supplied context and never retrieves.
    """

    def __init__(
        self,
        model: str = "",
        api_key: str = "",
        base_url: str = "",
    ) -> None:
        self.model = model or os.getenv("MODEL", "")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("API_KEY") or ""
        self.base_url = base_url or os.getenv("OPENROUTER_BASE_URL") or os.getenv(
            "BASE_URL", "https://openrouter.ai/api/v1"
        )
        self.id = f"openai:{self.model}" if self.model else "openai"
        self._client: OpenAI | None = None

    def is_available(self) -> bool:
        return bool(self.model and self.api_key)

    def generate(self, prompt: str, context: str) -> str:
        if not self.is_available():
            raise RuntimeError("OpenAI-compatible provider is not configured (missing MODEL/API_KEY).")
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are Patrick, a long-term collaborator and assistant. "
                    "Answer the user's question using ONLY the supplied context. "
                    "Do not use any knowledge outside of that context."
                ),
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{prompt}"},
        ]
        response = self._client.chat.completions.create(
            model=self.model, temperature=0, messages=messages  # type: ignore[arg-type]
        )
        return (response.choices[0].message.content or "").strip()