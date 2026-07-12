from __future__ import annotations

import json
import urllib.request

from .base import AiProvider

# Sensible defaults for a local OpenAI-compatible runtime (e.g. Ollama's
# OpenAI shim). These are used whenever the persisted settings are empty.
DEFAULT_ENDPOINT = "http://127.0.0.1:11434/v1/chat/completions"
DEFAULT_MODEL = "gemma-3-1b"

SYSTEM_PROMPT = (
    "You are Patrick, a long-term collaborator and assistant. "
    "Answer the user's question using ONLY the supplied context. "
    "Do not use any knowledge outside of that context. Be accurate "
    "and concise, and clearly state when the context is insufficient."
)


class LocalOpenAIProvider(AiProvider):
    """Talks to any local runtime exposing the OpenAI Chat Completions API.

    Unlike the remote OpenAI-compatible provider this one never needs an API
    key and is meant for fully on-device runtimes (Ollama, llama.cpp, LM
    Studio, …). It only generates from the prompt it is handed and never
    retrieves anything.
    """

    id = "local-openai"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        endpoint: str = DEFAULT_ENDPOINT,
    ) -> None:
        self.model = model or DEFAULT_MODEL
        self.endpoint = endpoint or DEFAULT_ENDPOINT

    def is_available(self) -> bool:
        """Probe the endpoint with a tiny request to confirm reachability."""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "ping"}],
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status == 200
        except Exception:  # noqa: BLE001 - any failure means "not reachable"
            return False

    def generate(self, prompt: str, context: str = "") -> str:
        user_content = prompt if not context else f"Context:\n{context}\n\nQuestion:\n{prompt}"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8", errors="ignore"))
        except Exception as error:  # noqa: BLE001 - surface as unreachable
            raise RuntimeError(f"Local AI unreachable: {error}") from error

        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError(f"Unexpected Local AI response: {error}") from error

        return (content or "").strip()