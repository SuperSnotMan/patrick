"""Sidebar workspace for the Patrick desktop client."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from .icons import ICON_MEMORY, ICON_NEW_CHAT, ICON_RECENT, ICON_SETTINGS
from .theme import (
    ACCENT,
    ACCENT_HOVER,
    BACKGROUND,
    BORDER,
    FONT_HEADING,
    PADDING,
    RADIUS,
    SURFACE,
    TEXT,
    TEXT_SECONDARY,
)


class SidebarButton(QPushButton):
    """Sidebar navigation button with icon, hover and active states."""

    def __init__(self, icon: str, text: str) -> None:
        super().__init__()
        self.setObjectName("sidebar_button")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText(f"{icon}  {text}")
        self.setCheckable(True)
        self.setStyleSheet(
            f"""
            QPushButton#sidebar_button {{
                background: {SURFACE};
                color: {TEXT};
                border: 1px solid transparent;
                border-radius: {RADIUS // 2}px;
                padding: 10px 12px;
                text-align: left;
                font-size: 12px;
            }}
            QPushButton#sidebar_button:hover {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                color: {TEXT};
            }}
            QPushButton#sidebar_button:checked {{
                background: {ACCENT};
                color: {BACKGROUND};
                border: 1px solid {ACCENT};
                font-weight: bold;
            }}
            QPushButton#sidebar_button:checked:hover {{
                background: {ACCENT_HOVER};
                border: 1px solid {ACCENT_HOVER};
            }}
            """
        )


class SidebarWidget(QFrame):
    """Workspace navigation. Buttons either perform an action or surface an
    informative dialog for features that are not yet implemented."""

    new_chat_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("panel")
        self.setStyleSheet(
            f"background: {SURFACE}; border: 1px solid {BORDER}; border-radius: {RADIUS}px;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        layout.setSpacing(PADDING // 2)

        title = QLabel("Patrick")
        title.setStyleSheet(
            f"font: {FONT_HEADING[2]} {FONT_HEADING[0]} {FONT_HEADING[1]}; color: {TEXT};"
        )
        layout.addWidget(title)

        self.new_chat_button = SidebarButton(ICON_NEW_CHAT, "New Chat")
        self.new_chat_button.clicked.connect(self._on_new_chat)
        layout.addWidget(self.new_chat_button)

        self.recent_button = SidebarButton(ICON_RECENT, "Recent Conversations")
        self.recent_button.clicked.connect(self._show_recent)
        layout.addWidget(self.recent_button)

        self.memory_button = SidebarButton(ICON_MEMORY, "Memory Graph")
        self.memory_button.clicked.connect(self._show_memory)
        layout.addWidget(self.memory_button)

        self.settings_button = SidebarButton(ICON_SETTINGS, "Settings")
        self.settings_button.clicked.connect(self._show_settings)
        layout.addWidget(self.settings_button)

        layout.addStretch()

    def _on_new_chat(self) -> None:
        self._set_active(self.new_chat_button)
        self.new_chat_requested.emit()

    def _set_active(self, button: SidebarButton) -> None:
        for btn in (
            self.new_chat_button,
            self.recent_button,
            self.memory_button,
            self.settings_button,
        ):
            btn.setChecked(btn is button)

    def _show_recent(self) -> None:
        self._set_active(self.recent_button)
        QMessageBox.information(
            self,
            "Recent Conversations",
            "Conversation history is not available yet.\n\n"
            "Patrick will remember past chats in a future update.",
        )
        self._set_active(self.new_chat_button)

    def _show_memory(self) -> None:
        self._set_active(self.memory_button)
        QMessageBox.information(
            self,
            "Memory Graph",
            "The Memory Graph is not available yet.\n\n"
            "Once enabled, it will visualise connections between your notes.",
        )
        self._set_active(self.new_chat_button)

    def _show_settings(self) -> None:
        self._set_active(self.settings_button)
        QMessageBox.information(
            self,
            "Settings",
            "Settings are configured in the Obsidian plugin and the server .env file.\n\n"
            "• Patrick Core URL: Obsidian → Patrick settings\n"
            "• AI provider: server/.env",
        )
        self._set_active(self.new_chat_button)