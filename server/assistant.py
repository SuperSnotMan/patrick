from __future__ import annotations

from knowledge import KnowledgeManager
from knowledge.base import RetrievalContext
from ai.factory import build_provider
from ai.base import AiProvider
from ai.local_openai import LocalOpenAIProvider
from local_ai_settings import load_settings

# Re-exported for callers that still import `ask` from this module.
__all__ = ["ask", "KnowledgeManager", "build_provider"]

NOT_FOUND_RESPONSE = "I cannot find that information in your notes."

# Returned verbatim when the local provider is enabled but cannot be reached.
LOCAL_AI_UNAVAILABLE = "📱 Local AI unavailable."

# Human-readable labels for each transparency section.
SECTION_LABELS = {
    "local_notes": "📖 My Notes",
    "patrick_server": "🖥 Patrick Server",
    "internet": "🌐 Internet",
    "cache": "📱 Cached Results",
}


def _format_api_error(error: Exception) -> str:
    message = str(error)
    if "429" in message or "RateLimit" in message or "rate limit" in message.lower():
        return (
            "Patrick's AI provider is temporarily rate limited. "
            "Please wait a moment and try again."
        )
    return f"Patrick could not reach the AI provider.\n\n{message}"


def _build_retrieval_context(
    vault_path: str,
    note_title: str,
    note_path: str,
    note_content: str,
    selection: str,
) -> RetrievalContext:
    return RetrievalContext(
        vault_path=vault_path,
        note_title=note_title,
        note_path=note_path,
        note_content=note_content,
        selection=selection,
    )


def _transparency_sections(knowledge) -> str:
    """Render each retrieved source under its clearly labelled section."""
    sections: list[str] = []

    if knowledge.notes.strip():
        sections.append(f"{SECTION_LABELS['local_notes']}\n\n{knowledge.notes.strip()}")
    if knowledge.server.strip():
        sections.append(f"{SECTION_LABELS['patrick_server']}\n\n{knowledge.server.strip()}")
    if knowledge.internet.strip():
        sections.append(f"{SECTION_LABELS['internet']}\n\n{knowledge.internet.strip()}")
    if knowledge.cache.strip():
        sections.append(f"{SECTION_LABELS['cache']}\n\n{knowledge.cache.strip()}")

    return "\n\n".join(sections)


def _source_summary(knowledge) -> str:
    """List which sources were actually used, for the AI Summary header."""
    labels = [str(SECTION_LABELS.get(name, name)) for name in knowledge.sources_used]
    if not labels:
        return "No sources were available."
    return "Sources used: " + ", ".join(labels)


def ask(
    question: str,
    vault_path: str = "",
    note_title: str = "",
    note_path: str = "",
    note_content: str = "",
    selection: str = "",
    manager: KnowledgeManager | None = None,
    provider: AiProvider | None = None,
) -> str:
    """Answer a question using retrieved context only.

    The KnowledgeManager gathers context from the configured sources (local
    notes, Patrick Server, internet, cache). The AI provider then generates a
    reply strictly from that context. The model never retrieves on its own.

    When the local OpenAI-compatible provider is enabled in settings, Patrick
    talks to that runtime directly and skips retrieval entirely.
    """
    settings = load_settings()
    if settings.enabled:
        return _ask_local(question, settings)

    manager = manager or KnowledgeManager()
    provider = provider or build_provider()

    context = _build_retrieval_context(
        vault_path, note_title, note_path, note_content, selection
    )
    knowledge = manager.retrieve(question, context)

    if not knowledge.has_content():
        return (
            f"{SECTION_LABELS['local_notes']}\n\n{NOT_FOUND_RESPONSE}\n\n"
            f"📱 AI Summary\n\n{_source_summary(knowledge)}"
        )

    merged_context = knowledge.merge_text()
    try:
        summary = provider.generate(question, merged_context)
    except Exception as error:  # noqa: BLE001 - surface provider failures clearly
        return (
            f"{_transparency_sections(knowledge)}\n\n"
            f"📱 AI Summary\n\n{_format_api_error(error)}"
        )

    if not summary.strip():
        summary = NOT_FOUND_RESPONSE

    return (
        f"{_transparency_sections(knowledge)}\n\n"
        f"📱 AI Summary\n\n{summary.strip()}\n\n{_source_summary(knowledge)}"
    )


def _ask_local(question: str, settings) -> str:
    """Use the configured local OpenAI-compatible runtime directly.

    No retrieval is performed. If the runtime cannot be reached, the caller
    sees the explicit "Local AI unavailable" message.
    """
    provider = LocalOpenAIProvider(model=settings.model, endpoint=settings.endpoint)
    try:
        summary = provider.generate(question)
    except Exception:  # noqa: BLE001 - unreachable local runtime
        return LOCAL_AI_UNAVAILABLE
    if not summary.strip():
        return LOCAL_AI_UNAVAILABLE
    return summary.strip()
