from __future__ import annotations

import os
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL") or os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.getenv("MODEL")

# Optional internet search. Disabled unless explicitly enabled via .env.
INTERNET_ENABLED = os.getenv("PATRICK_INTERNET", "false").strip().lower() in {"1", "true", "yes", "on"}

if not API_KEY:
    raise RuntimeError("No API key found in .env")
if not MODEL:
    raise RuntimeError("MODEL not set in .env")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

NOT_FOUND_RESPONSE = "I cannot find that information in your notes."

# How many related notes to pull in alongside the active note.
MAX_RELATED_NOTES = 5
# Cap on characters of note material sent to the model to control token usage.
MAX_NOTE_CHARS = 12000


def _read_vault_files(vault_path: str, max_files: int = 200) -> dict[str, str]:
    """Return a mapping of relative path -> text content for markdown notes in the vault.

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


def _build_note_messages(question: str, notes_text: str, selection: str) -> list[dict]:
    focus = f"\n\nThe user's current selection (prioritise this):\n{selection}" if selection.strip() else ""
    return [
        {
            "role": "system",
            "content": (
                "You are Patrick, a long-term collaborator and assistant. "
                "Answer the user's question using ONLY the supplied Obsidian notes. "
                "Be accurate and cite which note the information came from where useful. "
                "If the notes do not contain enough information to answer, reply exactly: "
                f"{NOT_FOUND_RESPONSE}\n\n"
                "Do not use outside knowledge unless the notes are insufficient."
            ),
        },
        {
            "role": "user",
            "content": f"Question:\n{question}{focus}\n\nYour notes:\n{notes_text}",
        },
    ]


def _build_internet_messages(question: str, notes_text: str, search_snippet: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": (
                "You are Patrick, a long-term collaborator and assistant. "
                "The user's own notes were insufficient, so supplement them with the "
                "provided internet search results. Clearly distinguish what comes from the "
                "notes versus the internet. Be accurate and concise."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Question:\n{question}\n\n"
                f"The user's notes (for context):\n{notes_text}\n\n"
                f"Internet search results:\n{search_snippet}"
            ),
        },
    ]


def _build_synthesis_messages(question: str, note_answer: str, internet_answer: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": (
                "You are Patrick. Combine the answer derived from the user's notes and the "
                "answer derived from the internet into a single, coherent reply. Keep the two "
                "perspectives distinct and label them clearly."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Question:\n{question}\n\n"
                f"Answer from notes:\n{note_answer}\n\n"
                f"Answer from internet:\n{internet_answer}"
            ),
        },
    ]


def call_model(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=messages,
    )
    return response.choices[0].message.content or ""


def _internet_search(query: str) -> str:
    """Best-effort web search using DuckDuckGo's HTML endpoint. Returns a short snippet."""
    try:
        import urllib.parse
        import urllib.request
        from html.parser import HTMLParser

        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={"User-Agent": "Patrick/0.1"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        snippets: list[str] = []

        class SnippetParser(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.capture = False
                self.buffer = ""

            def handle_starttag(self, tag, attrs):
                if tag == "a" and ("result__snippet", "") in attrs:
                    self.capture = True
                    self.buffer = ""

            def handle_endtag(self, tag):
                if self.capture and tag == "a":
                    self.capture = False
                    if self.buffer.strip():
                        snippets.append(self.buffer.strip())

            def handle_data(self, data):
                if self.capture:
                    self.buffer += data

        SnippetParser().feed(html)
        return "\n".join(snippets[:5])
    except Exception as error:  # noqa: BLE001 - search is best-effort
        return f"(Internet search failed: {error})"


def ask(
    question: str,
    vault_path: str = "",
    note_title: str = "",
    note_path: str = "",
    note_content: str = "",
    selection: str = "",
) -> str:
    notes = gather_notes(vault_path, note_path, note_content)
    notes_text = _truncate_notes(notes)

    if not notes_text.strip():
        return NOT_FOUND_RESPONSE

    try:
        note_answer = call_model(_build_note_messages(question, notes_text, selection))
    except Exception as error:  # noqa: BLE001 - surface API/network failures to the user
        return _format_api_error(error)

    if NOT_FOUND_RESPONSE not in note_answer:
        return f"📖 Your Notes\n\n{note_answer.strip()}"

    # Notes were insufficient. Try the internet if enabled.
    if not INTERNET_ENABLED:
        return (
            f"📖 Your Notes\n\n{note_answer.strip()}\n\n"
            "🌐 Internet\n\nInternet search is disabled. "
            "Enable it in Patrick's configuration to supplement your notes."
        )

    search = _internet_search(question)
    if not search.strip() or search.startswith("(Internet search failed"):
        return (
            f"📖 Your Notes\n\n{note_answer.strip()}\n\n"
            f"🌐 Internet\n\n{search or 'No results were returned.'}"
        )

    try:
        internet_answer = call_model(_build_internet_messages(question, notes_text, search))
    except Exception as error:  # noqa: BLE001
        return (
            f"📖 Your Notes\n\n{note_answer.strip()}\n\n"
            f"🌐 Internet\n\n{_format_api_error(error)}"
        )

    try:
        synthesis = call_model(_build_synthesis_messages(question, note_answer, internet_answer))
    except Exception as error:  # noqa: BLE001
        synthesis = (
            f"📖 Your Notes\n\n{note_answer.strip()}\n\n"
            f"🌐 Internet\n\n{internet_answer.strip()}"
        )

    return f"📖 Your Notes\n\n{note_answer.strip()}\n\n🌐 Internet\n\n{internet_answer.strip()}\n\n🧠 Patrick\n\n{synthesis.strip()}"


def _format_api_error(error: Exception) -> str:
    message = str(error)
    if "429" in message or "RateLimit" in message or "rate limit" in message.lower():
        return (
            "Patrick's AI provider is temporarily rate limited. "
            "Please wait a moment and try again."
        )
    return f"Patrick could not reach the AI provider.\n\n{message}"