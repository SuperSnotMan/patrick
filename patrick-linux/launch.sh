#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DESKTOP_DIR="${REPO_ROOT}/desktop"
SERVER_DIR="${REPO_ROOT}/server"
PYTHON_BIN="${REPO_ROOT}/server/.venv/bin/python"

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
