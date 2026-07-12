"""Controller layer for the desktop MVC layout."""

from __future__ import annotations

from PySide6.QtCore import QTimer

from .client import PatrickClient, PatrickContext
from .window import PatrickWindow


class PatrickController:
    def __init__(self, window: PatrickWindow) -> None:
        self.window = window
        self.client = PatrickClient()
        self.context = PatrickContext()
        self.refresh_timer = QTimer(self.window)
        self.refresh_timer.setInterval(1000)

        self.window.input_bar.submitted.connect(self.handle_submit)
        self.window.sidebar.new_chat_requested.connect(self.handle_new_chat)
        self.window.header.set_connection("connecting")
        self.refresh_context()
        self.refresh_status()

        self.refresh_timer.timeout.connect(self.refresh_context)
        self.refresh_timer.timeout.connect(self.refresh_status)
        self.refresh_timer.start()

    def refresh_status(self) -> None:
        connected = self.client.ping()
        self.window.header.set_connection("online" if connected else "offline")
        self.window.input_bar.send_button.setEnabled(connected)

    def refresh_context(self) -> None:
        self.context = self.client.get_context()
        self.window.update_context(self.context)

    def handle_submit(self, message: str) -> None:
        if not message.strip():
            return

        if not self.window.input_bar.send_button.isEnabled():
            self.window.chat.append_assistant_message("Patrick Core is unavailable.")
            return

        self.window.input_bar.set_busy(True)
        self.window.chat.append_user_message(message)
        response = self.client.send_message(message, self.context)
        self.window.chat.append_assistant_message(response)
        self.window.input_bar.set_busy(False)
        self.refresh_context()
        self.refresh_status()

    def handle_new_chat(self) -> None:
        self.window.chat.clear()
