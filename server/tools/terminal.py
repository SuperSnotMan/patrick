import subprocess
from typing import Dict, List


def run_command(command: List[str]) -> Dict:
    if not command or not all(isinstance(part, str) and part for part in command):
        return {
            "success": False,
            "return_code": None,
            "stdout": "",
            "stderr": "No command was provided.",
        }

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
            shell=False,
        )

        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except Exception as e:  # noqa: BLE001 - surface the failure to the caller
        return {
            "success": False,
            "return_code": None,
            "stdout": "",
            "stderr": str(e),
        }
