"""Keyboard-first input area for Patrick desktop chat."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QTextEdit

from .theme import ACCENT, ACCENT_HOVER, BACKGROUND, BORDER, INPUT, PADDING, RADIUS, SURFACE, TEXT


class InputEditor(QTextEdit):
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() == Qt.ShiftModifier:
                super().keyPressEvent(event)
                return
            parent = self.parent()
            if parent is not None and hasattr(parent, "_submit"):
                parent._submit()
                event.accept()
                return

        super().keyPressEvent(event)


class InputBar(QFrame):
    submitted = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("panel")
        self.setStyleSheet(
            f"background: {SURFACE}; border: 1px solid {BORDER}; border-radius: {RADIUS}px;"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(PADDING, PADDING // 2, PADDING, PADDING // 2)
        layout.setSpacing(PADDING // 2)

        self.editor = InputEditor()
        self.editor.setPlaceholderText("Message Patrick…  (Enter to send, Shift+Enter for newline)")
        self.editor.setMaximumHeight(120)
        self.editor.setObjectName("input_editor")
        self.editor.setStyleSheet(
            f"background: {INPUT}; color: {TEXT}; border: 1px solid {BORDER}; "
            f"border-radius: {RADIUS}px; padding: 10px 12px;"
        )
        layout.addWidget(self.editor, stretch=1)

        self.send_button = QPushButton("Send")
        self.send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_button.setStyleSheet(
            f"background: {ACCENT}; color: {BACKGROUND}; border: none; "
            f"border-radius: {RADIUS // 2}px; padding: 8px 18px; font-weight: bold;"
        )
        self.send_button.clicked.connect(self._submit)
        layout.addWidget(self.send_button)

    def set_busy(self, busy: bool) -> None:
        """Disable input while Patrick is replying."""
        self.editor.setDisabled(busy)
        self.send_button.setDisabled(busy)
        if busy:
            self.send_button.setText("…")
        else:
            self.send_button.setText("Send")

    def _submit(self) -> None:
        message = self.editor.toPlainText().strip()
        if not message:
            return

        self.submitted.emit(message)
        self.editor.clear()