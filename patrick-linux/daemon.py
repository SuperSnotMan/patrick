"""Linux context bridge. UI clients communicate over a user-private Unix socket."""
import json
import os
import socket
from pathlib import Path

SOCKET_PATH = Path.home() / ".cache" / "patrick-linux" / "context.sock"
state = {"contexts": {}, "active": None, "server_url": "http://localhost:8000"}


def send(connection, value):
    connection.sendall((json.dumps(value) + "\n").encode())


def handle(connection):
    request = json.loads(connection.makefile("r", encoding="utf8").readline())
    if request.get("type") == "update":
        context = request["context"]
        key = context.get("vault") or "unknown"
        state["contexts"][key] = context
        state["active"] = key
        state["server_url"] = request.get("server_url") or state["server_url"]
        send(connection, {"ok": True})
    elif request.get("type") == "get":
        active = state["contexts"].get(state["active"], {"vault": "", "note": {}})
        send(connection, {"context": active, "contexts": state["contexts"], "server_url": state["server_url"]})
    else:
        send(connection, {"error": "Unknown request."})


def main():
    SOCKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SOCKET_PATH.exists():
        try:
            probe = socket.socket(socket.AF_UNIX)
            probe.connect(str(SOCKET_PATH))
            return
        except OSError:
            SOCKET_PATH.unlink(missing_ok=True)
    server = socket.socket(socket.AF_UNIX)
    server.bind(str(SOCKET_PATH))
    os.chmod(SOCKET_PATH, 0o600)
    server.listen()
    while True:
        connection, _ = server.accept()
        with connection:
            try:
                handle(connection)
            except (json.JSONDecodeError, KeyError, OSError) as error:
                send(connection, {"error": str(error)})


if __name__ == "__main__":
    main()
