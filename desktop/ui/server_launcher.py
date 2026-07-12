"""Ensures the Patrick Core server is running before the desktop UI starts.

The desktop only ever talks to the server over HTTP; this helper launches the
server as a detached subprocess when it is not already reachable. No server
modules are imported into the desktop.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

DEFAULT_SERVER_URL = "http://localhost:8000"
SERVER_PORT = 8000
STARTUP_TIMEOUT = 15.0


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _server_dir() -> Path:
    return _repo_root() / "server"


def _python_bin() -> Path:
    venv_python = _server_dir() / ".venv" / "bin" / "python"
    return venv_python if venv_python.exists() else Path(sys.executable)


def is_running(url: str = DEFAULT_SERVER_URL) -> bool:
    try:
        with urlopen(Request(url + "/"), timeout=1):
            return True
    except (URLError, OSError):
        return False


def ensure_server(url: str = DEFAULT_SERVER_URL) -> None:
    """Start Patrick Core if it is not already responding, then wait until ready."""
    if is_running(url):
        return

    server_dir = _server_dir()
    if not (server_dir / "main.py").exists():
        return

    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(server_dir)

    try:
        subprocess.Popen(
            [
                str(_python_bin()),
                "-m",
                "uvicorn",
                "main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(SERVER_PORT),
            ],
            cwd=str(server_dir),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        return

    deadline = time.time() + STARTUP_TIMEOUT
    while time.time() < deadline:
        if is_running(url):
            return
        time.sleep(0.5)