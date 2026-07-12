from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ai.local_openai import DEFAULT_ENDPOINT, DEFAULT_MODEL

# Persisted alongside the server so the desktop can read/write it over HTTP.
SETTINGS_PATH = Path(__file__).resolve().parent / "local_ai_settings.json"


@dataclass(slots=True)
class LocalAiSettings:
    """User-configured local OpenAI-compatible provider settings."""

    enabled: bool = False
    endpoint: str = DEFAULT_ENDPOINT
    model: str = DEFAULT_MODEL

    def to_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "endpoint": self.endpoint,
            "model": self.model,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "LocalAiSettings":
        return cls(
            enabled=bool(data.get("enabled", False)),
            endpoint=str(data.get("endpoint", DEFAULT_ENDPOINT)),
            model=str(data.get("model", DEFAULT_MODEL)),
        )


def load_settings() -> LocalAiSettings:
    """Load persisted settings, falling back to defaults if absent/corrupt."""
    if not SETTINGS_PATH.exists():
        return LocalAiSettings()
    try:
        raw = SETTINGS_PATH.read_text(encoding="utf-8")
        return LocalAiSettings.from_dict(json.loads(raw))
    except (json.JSONDecodeError, OSError):
        return LocalAiSettings()


def save_settings(settings: LocalAiSettings) -> None:
    """Persist settings to disk atomically-ish (single write)."""
    SETTINGS_PATH.write_text(
        json.dumps(settings.to_dict(), indent=2),
        encoding="utf-8",
    )