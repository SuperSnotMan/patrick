#!/usr/bin/env bash
# Canonical Patrick desktop companion launcher.
#
# Ensures Patrick Core (the FastAPI server) is running, then starts the
# PySide6 desktop UI. The desktop talks to the server over HTTP only and
# never imports server modules.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DESKTOP_DIR="${SCRIPT_DIR}"
SERVER_DIR="${REPO_ROOT}/server"
VENV_PYTHON="${REPO_ROOT}/server/.venv/bin/python"

# Prefer the project venv, but fall back to the system interpreter so the
# desktop still launches when the venv has not been provisioned.
if [ -x "${VENV_PYTHON}" ]; then
    PYTHON_BIN="${VENV_PYTHON}"
else
    PYTHON_BIN="$(command -v python3 || command -v python)"
fi

export PYTHONPATH="${DESKTOP_DIR}"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"

if ! "${PYTHON_BIN}" - <<'PY'
import sys
from urllib.request import Request, urlopen

try:
    with urlopen(Request("http://127.0.0.1:8000/"), timeout=1):
        sys.exit(0)
except Exception:
    sys.exit(1)
PY
then
    (cd "${SERVER_DIR}" && PYTHONPATH=. "${PYTHON_BIN}" -m uvicorn main:app --host 127.0.0.1 --port 8000 >/tmp/patrick-core.log 2>&1 &) >/dev/null 2>&1 || true
fi

exec "${PYTHON_BIN}" -m ui.app