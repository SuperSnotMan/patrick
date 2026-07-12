from __future__ import annotations

import re
from pathlib import Path

from .base import KnowledgeSource, RetrievalContext

# How many related notes to pull in alongside the active note.
MAX_RELATED_NOTES = 5
# Cap on characters of note material sent to the model to control token usage.
MAX_NOTE_CHARS = 12000


def _read_vault_files(vault_path: str, max_files: int = 200) -> dict[str, str]:
    """Return a mapping of relative path -> text content for markdown notes.

    Hidden directories (e.g. .obsidian, .trash) are skipped to avoid scanning
    configuration and binary attachment caches.
    """
    result: dict[str, str] = {}
    root = Path(vault_path)
    if not root.exists():
        return result
    for path in root.rglob("*.md"):
        if len(result) >= max_files:
            break
        if any(part.startswith(".") for part in path.relative_to(root).parts[:-1]):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        result[str(path.relative_to(root))] = text
    return result


def _wikilinks(content: str) -> list[str]:
    """Extract [[wikilink]] targets from note content."""
    return re.findall(r"\[\[([^\]|#]+)", content)


def _keyword_tokens(content: str, limit: int = 12) -> list[str]:
    """Cheap keyword extraction: drop markdown/punctuation, keep meaningful words."""
    words = re.findall(r"[A-Za-z][A-Za-z'-]{3,}", content.lower())
    stop = {
        "the", "and", "for", "with", "that", "this", "from", "into", "your",
        "have", "are", "was", "but", "not", "you", "our", "they", "will",
        "can", "all", "any", "out", "who", "why", "how", "what", "when",
    }
    seen: list[str] = []
    for word in words:
        if word not in stop and word not in seen:
            seen.append(word)
        if len(seen) >= limit:
            break
    return seen


def gather_notes(vault_path: str, note_path: str, note_content: str) -> dict[str, str]:
    """Collect the current note, related notes (via wikilinks + keyword overlap) and journal."""
    files = _read_vault_files(vault_path)
    collected: dict[str, str] = {}

    # Current note first.
    if note_content.strip():
        collected["current"] = note_content

    # Related notes: wikilinks take priority, then keyword overlap.
    candidates: list[str] = []
    for link in _wikilinks(note_content):
        target = link.strip()
        for rel, text in files.items():
            base = Path(rel).stem
            if base == target or rel == target or rel == f"{target}.md":
                candidates.append(rel)
                break

    if not candidates:
        keywords = set(_keyword_tokens(note_content))
        scored = sorted(
            files.items(),
            key=lambda item: sum(1 for kw in keywords if kw in item[1].lower()),
            reverse=True,
        )
        candidates = [rel for rel, _ in scored[:MAX_RELATED_NOTES] if rel != note_path]

    for rel in candidates[:MAX_RELATED_NOTES]:
        if rel not in collected:
            collected[rel] = files[rel]

    # Journal: a top-level Journal folder or a journal note named after the vault owner.
    for rel, text in files.items():
        name = Path(rel)
        if name.parent.name.lower() == "journal" or name.stem.lower() == "journal":
            collected.setdefault(rel, text)

    return collected


def _truncate_notes(notes: dict[str, str]) -> str:
    parts: list[str] = []
    total = 0
    for name, text in notes.items():
        if total + len(text) > MAX_NOTE_CHARS:
            text = text[: max(0, MAX_NOTE_CHARS - total)]
        if not text.strip():
            continue
        parts.append(f"--- {name} ---\n{text}")
        total += len(text)
        if total >= MAX_NOTE_CHARS:
            break
    return "\n\n".join(parts)


class LocalNotesSource(KnowledgeSource):
    """Retrieves relevant Obsidian notes from the local vault on disk."""

    name = "local_notes"

    def is_available(self) -> bool:
        return True

    def retrieve(self, query: str, context: RetrievalContext) -> str:
        notes = gather_notes(context.vault_path, context.note_path, context.note_content)
        return _truncate_notes(notes)