from __future__ import annotations

import os
import subprocess
import sys

from .base import AiProvider


class GemmaProvider(AiProvider):
    """Default local provider: Gemma 3 1B.

    Runs fully on-device. The model is loaded through a local inference engine
    (e.g. Ollama, llama.cpp, or transformers). This provider never retrieves
    anything; it only generates from the context it is handed.
    """

    id = "gemma3-1b"

    def __init__(
        self,
        model: str = "gemma3:1b",
        endpoint: str = "",
        backend: str = "ollama",
    ) -> None:
        self.model = model
        self.endpoint = endpoint or os.getenv("GEMMA_ENDPOINT", "http://localhost:11434")
        self.backend = backend or os.getenv("GEMMA_BACKEND", "ollama")

    def is_available(self) -> bool:
        if self.backend == "ollama":
            try:
                import urllib.request

                req = urllib.request.Request(self.endpoint, method="GET")
                with urllib.request.urlopen(req, timeout=3):
                    return True
            except Exception:  # noqa: BLE001
                return False
        # Non-Ollama backends are assumed available if the module is importable.
        return True

    def generate(self, prompt: str, context: str) -> str:
        if self.backend == "ollama":
            return self._generate_ollama(prompt, context)
        return self._generate_python(prompt, context)

    def _build_messages(self, prompt: str, context: str) -> list[dict]:
        system = (
            "You are Patrick, a long-term collaborator and assistant. "
            "Answer the user's question using ONLY the supplied context. "
            "Do not use any knowledge outside of that context. Be accurate "
            "and concise, and clearly state when the context is insufficient."
        )
        user = f"Context:\n{context}\n\nQuestion:\n{prompt}"
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    def _generate_ollama(self, prompt: str, context: str) -> str:
        import json
        import urllib.request

        payload = {
            "model": self.model,
            "messages": self._build_messages(prompt, context),
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.endpoint.rstrip('/')}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8", errors="ignore"))
        return result.get("message", {}).get("content", "").strip()

    def _generate_python(self, prompt: str, context: str) -> str:
        """Fallback local inference via the `transformers` package."""
        try:
            from transformers import pipeline  # type: ignore
        except ImportError:
            raise RuntimeError(
                "Gemma local backend requires 'transformers'. "
                "Install it or switch GEMMA_BACKEND to 'ollama'."
            )
        pipe = pipeline("text-generation", model=self.model)
        messages = self._build_messages(prompt, context)
        output = pipe(messages, max_new_tokens=512)
        text = output[0]["generated_text"]
        if isinstance(text, list):
            text = text[-1].get("content", "")
        return str(text).strip()