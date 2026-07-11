
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL") or os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.getenv("MODEL")

if not API_KEY:
    raise RuntimeError("No API key found in .env")
if not MODEL:
    raise RuntimeError("MODEL not set in .env")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

NOT_FOUND_RESPONSE = "I cannot find that information in the current note."

def build_messages(question: str, note_content: str):
    return [
        {
            "role": "system",
            "content": (
                "You are Patrick. Answer using the supplied Obsidian note. "
                f"If the answer is not present reply exactly: {NOT_FOUND_RESPONSE}\n\n"
                "If the user explicitly asks you to execute a terminal command, respond ONLY with:\n"
                "TOOL:terminal\nCOMMAND:<command>"
            ),
        },
        {
            "role": "user",
            "content": f"Question:\n{question}\n\nCurrent note:\n{note_content}",
        },
    ]

def call_model(messages):
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=messages,
    )
    return response.choices[0].message.content or ""

def ask(question: str, note_content: str) -> str:
    if not note_content.strip():
        return NOT_FOUND_RESPONSE
    return call_model(build_messages(question, note_content))
