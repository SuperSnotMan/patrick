from fastapi import FastAPI
from pydantic import BaseModel, Field
from vault import read_note
from ai import ask

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

    response = ask(request.message, request.context.note.content)

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
