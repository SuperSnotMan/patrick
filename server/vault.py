from pathlib import Path
from config import PERSONAL_VAULT, SWYFT_VAULT

VAULTS = {
    "personal": PERSONAL_VAULT,
    "swyft": SWYFT_VAULT
}


def read_note(vault: str, note: str):

    base = VAULTS[vault]

    path = base / note

    if not path.exists():
        return None

    return path.read_text(encoding="utf-8")