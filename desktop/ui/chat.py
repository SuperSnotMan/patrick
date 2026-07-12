"""Scrollable chat surface with one message widget per conversation item."""

from __future__ import annotations

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QPushButton,
)

from .markdown import render_markdown
from .theme import (
    BORDER,
    CODE_BG,
    CODE_TEXT,
    INLINE_CODE_BG,
    INLINE_CODE_TEXT,
    PADDING,
    PATRICK_BUBBLE,
    PATRICK_TEXT,
    RADIUS,
    TEXT_SECONDARY,
    USER_BUBBLE,
    USER_TEXT,
)


class MessageBubble(QFrame):
    def __init__(self, author: str, text: str) -> None:
        super().__init__()
        self.author = author
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setObjectName("message_bubble")

        is_user = author != "Patrick"

        container = QVBoxLayout(self)
        container.setContentsMargins(0, 0, 0, 0)
        container.setSpacing(4)

        body = QLabel()
        body.setTextFormat(Qt.TextFormat.RichText)
        body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        body.setWordWrap(True)
        body.setOpenExternalLinks(False)
        body.setText(render_markdown(text))
        body.setStyleSheet("margin: 0; padding: 0;")
        container.addWidget(body)

        if is_user:
            self.setStyleSheet(
                f"background: {USER_BUBBLE}; color: {USER_TEXT}; "
                f"border-radius: {RADIUS}px; padding: 10px 14px;"
            )
            body.setStyleSheet(
                f"color: {USER_TEXT}; background: transparent; margin: 0; padding: 0;"
            )
        else:
            self.setStyleSheet(
                f"background: {PATRICK_BUBBLE}; color: {PATRICK_TEXT}; "
                f"border: 1px solid {BORDER}; border-radius: {RADIUS}px; "
                f"padding: 10px 14px;"
            )
            controls = QHBoxLayout()
            controls.addStretch()
            copy_button = QPushButton("Copy")
            copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
            copy_button.setStyleSheet(
                f"background: transparent; color: {TEXT_SECONDARY}; "
                f"border: 1px solid {BORDER}; border-radius: {RADIUS // 2}px; "
                f"padding: 4px 10px;"
            )
            copy_button.clicked.connect(lambda: self._copy_text(text))
            controls.addWidget(copy_button)
            container.addLayout(controls)

        self.setMaximumWidth(560)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

    def _copy_text(self, text: str) -> None:
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)


class ChatWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setStyleSheet("background: transparent; border: none;")
        root.addWidget(self._scroll_area)

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._message_layout = QVBoxLayout(self._container)
        self._message_layout.setSpacing(16)
        self._message_layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        self._message_layout.addStretch()
        self._scroll_area.setWidget(self._container)

    def append_user_message(self, text: str) -> None:
        self._add_message("You", text)

    def append_assistant_message(self, text: str) -> None:
        self._add_message("Patrick", text)

    def clear(self) -> None:
        while self._message_layout.count() > 1:
            item = self._message_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _add_message(self, author: str, text: str) -> None:
        bubble = MessageBubble(author, text)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)
        if author == "Patrick":
            row_layout.addWidget(bubble)
            row_layout.addStretch()
        else:
            row_layout.addStretch()
            row_layout.addWidget(bubble)

        self._message_layout.insertWidget(self._message_layout.count() - 1, row)
        self._fade_in(bubble)
        self._scroll_area.verticalScrollBar().setValue(
            self._scroll_area.verticalScrollBar().maximum()
        )

    def _fade_in(self, widget: QWidget) -> None:
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(220)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
