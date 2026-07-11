"""Tk implementation of Patrick's desktop UI; protocol is portable beyond Linux."""
import json
import subprocess
import sys
import tkinter as tk
from tkinter import ttk
from urllib.request import Request, urlopen
from pathlib import Path

ROOT = Path(__file__).parent


def bridge_state():
    output = subprocess.check_output([sys.executable, str(ROOT / "bridge_client.py"), "--get"], text=True)
    return json.loads(output)


class PatrickWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Patrick")
        self.geometry("620x680")
        self.minsize(420, 440)
        self.context, self.server_url = {}, "http://localhost:8000"
        self.configure(bg="#1e1e2e")
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self._build_ui()
        self.refresh_context()

    def _build_ui(self):
        header = tk.Frame(self, bg="#1e1e2e")
        header.pack(fill="x", padx=18, pady=(16, 8))
        tk.Label(header, text="Patrick", font=("Sans", 18, "bold"), fg="#cdd6f4", bg="#1e1e2e").pack(side="left")
        self.pin = tk.BooleanVar(value=False)
        ttk.Checkbutton(header, text="Always on top", variable=self.pin, command=lambda: self.attributes("-topmost", self.pin.get())).pack(side="right")
        self.context_label = tk.Label(self, anchor="w", fg="#a6adc8", bg="#313244", padx=12, pady=8)
        self.context_label.pack(fill="x", padx=18, pady=(0, 8))
        self.history = tk.Text(self, wrap="word", state="disabled", bg="#181825", fg="#cdd6f4", relief="flat", padx=12, pady=12)
        self.history.pack(fill="both", expand=True, padx=18)
        self.input = tk.Text(self, height=3, wrap="word", bg="#313244", fg="#cdd6f4", relief="flat", padx=10, pady=8)
        self.input.pack(fill="x", padx=18, pady=(10, 6))
        self.input.bind("<Return>", self.send_on_enter)
        controls = tk.Frame(self, bg="#1e1e2e")
        controls.pack(fill="x", padx=18, pady=(0, 12))
        ttk.Button(controls, text="Send", command=self.send).pack(side="right")
        ttk.Button(controls, text="Copy last response", command=self.copy_last).pack(side="right", padx=8)

    def refresh_context(self):
        try:
            state = bridge_state()
            self.context, self.server_url = state["context"], state["server_url"]
            note = self.context.get("note", {})
            self.context_label.config(text=f"Context   📖 {self.context.get('vault') or 'No vault'}   📄 {note.get('title') or 'No note'}")
        except Exception:
            self.context, self.server_url = {"vault": "", "note": {}}, "http://localhost:8000"
        self.after(1000, self.refresh_context)

    def append(self, label, text):
        self.history.config(state="normal")
        self.history.insert("end", f"{label}\n{text}\n\n")
        self.history.config(state="disabled")
        self.history.see("end")
        if label == "Patrick": self.last_response = text

    def send_on_enter(self, event):
        if not event.state & 0x1:
            self.send(); return "break"

    def send(self):
        message = self.input.get("1.0", "end").strip()
        if not message: return
        self.input.delete("1.0", "end")
        self.append("You", message)
        try:
            request = Request(self.server_url.rstrip("/") + "/chat", data=json.dumps({"message": message, "action": "ask", "context": self.context}).encode(), headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(request, timeout=60) as response:
                answer = json.loads(response.read())["response"]
            self.append("Patrick", answer)
        except Exception as error:
            self.append("Patrick", f"Could not contact Patrick Core: {error}")

    def copy_last(self):
        if hasattr(self, "last_response"):
            self.clipboard_clear(); self.clipboard_append(self.last_response)


if __name__ == "__main__":
    PatrickWindow().mainloop()
