"""Send current Obsidian context to the background bridge or read it for the UI."""
import argparse
import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

SOCKET_PATH = Path.home() / ".cache" / "patrick-linux" / "context.sock"
ROOT = Path(__file__).parent


def request(payload):
    connection = socket.socket(socket.AF_UNIX)
    connection.connect(str(SOCKET_PATH))
    with connection:
        connection.sendall((json.dumps(payload) + "\n").encode())
        return json.loads(connection.makefile("r", encoding="utf8").readline())


def ensure_daemon():
    try:
        return request({"type": "get"})
    except OSError:
        subprocess.Popen([sys.executable, str(ROOT / "daemon.py")], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(20):
            time.sleep(0.05)
            try:
                return request({"type": "get"})
            except OSError:
                continue
        raise RuntimeError("Patrick background bridge did not start.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context-file")
    parser.add_argument("--server-url", default="http://localhost:8000")
    parser.add_argument("--get", action="store_true")
    args = parser.parse_args()
    ensure_daemon()
    if args.get:
        print(json.dumps(request({"type": "get"})))
        return
    if not args.context_file:
        parser.error("--context-file is required unless --get is used")
    context_path = Path(args.context_file)
    try:
        context = json.loads(context_path.read_text(encoding="utf8"))
        request({"type": "update", "context": context, "server_url": args.server_url})
    finally:
        shutil.rmtree(context_path.parent, ignore_errors=True)


if __name__ == "__main__":
    main()
