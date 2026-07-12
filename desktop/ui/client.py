"""Thin HTTP client for Patrick desktop interactions."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import subprocess
import sys
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SERVER_URL = "http://localhost:8000"


@dataclass(slots=True)
class NoteContext:
    title: str = ""
    path: str = ""
    content: str = ""
    cursor_line: int = 0
    selection: str = ""


@dataclass(slots=True)
class PatrickContext:
    vault: str = ""
    vault_path: str = ""
    note: NoteContext = field(default_factory=NoteContext)


class PatrickClient:
    """Network-only wrapper that keeps UI code free of HTTP details."""

    def __init__(self, server_url: str = DEFAULT_SERVER_URL) -> None:
        self.server_url = server_url

    def _bridge_state(self) -> dict[str, Any]:
        bridge_path = ROOT / "bridge_client.py"
        if not bridge_path.exists():
            return {}

        try:
            raw = subprocess.check_output(
                [sys.executable, str(bridge_path), "--get"],
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {}

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def _base_url(self, path: str) -> str:
        return f"{self.server_url.rstrip('/')}{path}"

    def get_context(self) -> PatrickContext:
        state = self._bridge_state()
        self.server_url = str(state.get("server_url", self.server_url))

        context = state.get("context", {})
        note = context.get("note", {})

        return PatrickContext(
            vault=str(context.get("vault", "")),
            vault_path=str(context.get("vault_path", "")),
            note=NoteContext(
                title=str(note.get("title", "")),
                path=str(note.get("path", "")),
                content=str(note.get("content", "")),
                cursor_line=int(note.get("cursor_line", 0)),
                selection=str(note.get("selection", "")),
            ),
        )

    def send_message(self, message: str, context: PatrickContext) -> str:
        payload = {
            "message": message,
            "context": {
                "vault": context.vault,
                "vault_path": context.vault_path,
                "note": {
                    "title": context.note.title,
                    "path": context.note.path,
                    "content": context.note.content,
                    "cursor_line": context.note.cursor_line,
                    "selection": context.note.selection,
                },
            },
        }

        request = Request(
            self._base_url("/chat"),
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=90) as response:
                body = json.loads(response.read())
                return str(body.get("response", "Patrick did not return a response."))
        except URLError as error:
            return f"Patrick Core is unavailable.\\n\\n{error}"

    def ask(self, message: str, context: PatrickContext) -> str:
        return self.send_message(message, context)

    def ping(self) -> bool:
        try:
            request = Request(self._base_url("/"), method="GET")
            with urlopen(request, timeout=3):
                return True
        except Exception:
            return False

    def get_local_ai_settings(self) -> dict[str, object]:
        request = Request(self._base_url("/local-ai/settings"), method="GET")
        try:
            with urlopen(request, timeout=5) as response:
                return json.loads(response.read())
        except Exception:
            return {"enabled": False, "endpoint": "", "model": ""}

    def save_local_ai_settings(self, enabled: bool, endpoint: str, model: str) -> dict[str, object]:
        payload = {"enabled": enabled, "endpoint": endpoint, "model": model}
        request = Request(
            self._base_url("/local-ai/settings"),
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                return json.loads(response.read())
        except Exception:
            return {"enabled": enabled, "endpoint": endpoint, "model": model}

    def test_local_ai(self, endpoint: str, model: str) -> bool:
        payload = {"enabled": True, "endpoint": endpoint, "model": model}
        request = Request(
            self._base_url("/local-ai/test"),
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=8) as response:
                body = json.loads(response.read())
                return bool(body.get("reachable", False))
        except Exception:
            return False
