from fastapi import FastAPI
from pydantic import BaseModel, Field

from vault import read_note
from assistant import ask
from local_ai_settings import (
    LocalAiSettings,
    load_settings,
    save_settings,
)
from ai.local_openai import LocalOpenAIProvider


app = FastAPI(
    title="Patrick Core",
    description="The brain behind Swyft's assistant.",
    version="0.1.0"
)

class NoteContext(BaseModel):
    title: str = ""
    path: str = ""
    content: str = ""
    cursor_line: int = 0
    selection: str = ""


class PatrickContext(BaseModel):
    vault: str = ""
    vault_path: str = ""
    note: NoteContext = Field(default_factory=NoteContext)


class ChatRequest(BaseModel):
    message: str
    context: PatrickContext = Field(default_factory=PatrickContext)

class NoteRequest(BaseModel):
    vault: str
    note: str

@app.get("/")
def root():
    return {
        "name": "Patrick",
        "status": "Online",
        "message": "Hello Aaron."
    }


@app.post("/chat")
def chat(request: ChatRequest):

    response = ask(
        request.message,
        vault_path=request.context.vault_path,
        note_title=request.context.note.title,
        note_path=request.context.note.path,
        note_content=request.context.note.content,
        selection=request.context.note.selection,
    )

    return {
        "response": response
    }

@app.post("/vault/read")
def vault_read(request: NoteRequest):

    content = read_note(request.vault, request.note)

    if content is None:
        return {
            "error": "Note not found."
        }

    return {
        "content": content
    }

class TerminalRequest(BaseModel):
    command: list[str]


from tool_manager import ToolManager

_TOOL_MANAGER = ToolManager()


@app.post("/tools/terminal")
def terminal(request: TerminalRequest):
    return _TOOL_MANAGER.execute("terminal", " ".join(request.command))


class LocalAiSettingsRequest(BaseModel):
    enabled: bool = False
    endpoint: str = ""
    model: str = ""


@app.get("/local-ai/settings")
def local_ai_settings():
    """Return the current local OpenAI-compatible provider settings."""
    settings = load_settings()
    return settings.to_dict()


@app.post("/local-ai/settings")
def update_local_ai_settings(request: LocalAiSettingsRequest):
    """Persist local OpenAI-compatible provider settings."""
    settings = LocalAiSettings(
        enabled=request.enabled,
        endpoint=request.endpoint,
        model=request.model,
    )
    save_settings(settings)
    return settings.to_dict()


@app.post("/local-ai/test")
def test_local_ai(request: LocalAiSettingsRequest):
    """Probe the configured endpoint to confirm the local runtime is reachable."""
    provider = LocalOpenAIProvider(model=request.model, endpoint=request.endpoint)
    reachable = provider.is_available()
    return {"reachable": reachable}
