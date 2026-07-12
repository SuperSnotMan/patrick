#!/usr/bin/env python3
"""Lightweight bridge state provider for the Patrick desktop app and Obsidian launcher."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


STATE_FILE = Path(
    os.environ.get(
        "PATRICK_STATE_PATH",
        Path.home() / ".config" / "patrick" / "bridge_state.json",
    )
)
DEFAULT_SERVER_URL = "http://localhost:8000"
DEFAULT_CONTEXT = {
    "vault": "Local Workspace",
    "vault_path": "",
    "note": {
        "title": "No Active Note",
        "path": "",
        "content": "No active note is currently selected. Open Obsidian or choose a note to enable context-aware replies.",
        "cursor_line": 0,
        "selection": "",
    },
}


def default_state() -> dict[str, object]:
    return {
        "server_url": DEFAULT_SERVER_URL,
        "context": DEFAULT_CONTEXT,
    }


def read_state() -> dict[str, object]:
    if not STATE_FILE.exists():
        return default_state()

    try:
        payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default_state()

    if not isinstance(payload, dict):
        return default_state()

    merged = default_state()
    merged.update(payload)
    if isinstance(payload.get("context"), dict):
        merged["context"] = {**DEFAULT_CONTEXT, **payload["context"]}
    return merged


def write_state(state: dict[str, object]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--get", action="store_true")
    parser.add_argument("--context-file", dest="context_file")
    parser.add_argument("--server-url", dest="server_url")
    args = parser.parse_args()

    if args.context_file:
        context_path = Path(args.context_file)
        if context_path.exists():
            context_payload = json.loads(context_path.read_text(encoding="utf-8"))
            state = read_state()
            state["context"] = context_payload
            if args.server_url:
                state["server_url"] = args.server_url
            write_state(state)

    if args.get:
        print(json.dumps(read_state()))
        return 0

    print(json.dumps(read_state()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
