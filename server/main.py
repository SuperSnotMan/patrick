from fastapi import FastAPI
from pydantic import BaseModel
from vault import read_note

app = FastAPI(
    title="Patrick Core",
    description="The brain behind Swyft's assistant.",
    version="0.1.0"
)

class ChatRequest(BaseModel):
    message: str

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
    return {
        "response": f"You said: {request.message}"
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