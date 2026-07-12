"""Top-level header widget for the Patrick desktop client."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from .client import PatrickContext
from .icons import ICON_LOGO, ICON_NOTE, ICON_VAULT
from .theme import (
    ACCENT,
    BORDER,
    CONNECTING,
    FONT_BODY,
    FONT_TITLE,
    OFFLINE,
    ONLINE,
    PADDING,
    RADIUS,
    SURFACE,
    TEXT,
    TEXT_SECONDARY,
)


class StatusBadge(QLabel):
    """A pill-shaped connection indicator."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("status_badge")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_state("offline")

    def _set_state(self, state: str) -> None:
        mapping = {
            "online": ("🟢 Online", ONLINE),
            "connecting": ("🟡 Connecting", CONNECTING),
            "offline": ("🔴 Offline", OFFLINE),
        }
        label, color = mapping[state]
        self.setText(label)
        self.setStyleSheet(
            f"background: {SURFACE}; color: {color}; border: 1px solid {BORDER}; "
            f"border-radius: {RADIUS}px; padding: 4px 12px; font-weight: bold; "
            f"font-size: 11px;"
        )


class PatrickHeader(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("panel")
        self.setStyleSheet(
            f"background: {SURFACE}; border: 1px solid {BORDER}; border-radius: {RADIUS}px;"
        )
        self.setMinimumHeight(64)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(PADDING, PADDING // 2, PADDING, PADDING // 2)
        outer.setSpacing(PADDING)

        # Logo + title block
        logo = QLabel(ICON_LOGO)
        logo.setStyleSheet(f"color: {ACCENT}; font-size: 22px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(logo)

        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        self.title_label = QLabel("Patrick")
        self.title_label.setStyleSheet(
            f"font: {FONT_TITLE[2]} {FONT_TITLE[0]} {FONT_TITLE[1]}; color: {TEXT};"
        )
        title_block.addWidget(self.title_label)

        self.context_label = QLabel("No Vault  •  No Note")
        self.context_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font: {FONT_BODY[1]}px {FONT_BODY[0]};"
        )
        title_block.addWidget(self.context_label)
        outer.addLayout(title_block)

        outer.addStretch()

        # Connection status badge
        self.status_badge = StatusBadge()
        outer.addWidget(self.status_badge)

    def set_connection(self, state: str) -> None:
        """state is one of 'online', 'connecting', 'offline'."""
        self.status_badge._set_state(state)

    def update_context(self, context: PatrickContext) -> None:
        vault = context.vault or "No Vault"
        note = context.note.title or "No Note"
        self.context_label.setText(f"{ICON_VAULT} {vault}   •   {ICON_NOTE} {note}")