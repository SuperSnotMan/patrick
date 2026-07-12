"""Main desktop window for the Patrick client."""

from __future__ import annotations

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from .chat import ChatWidget
from .client import PatrickContext
from .header import PatrickHeader
from .input_bar import InputBar
from .sidebar import SidebarWidget
from .theme import (
    ACCENT,
    BACKGROUND,
    BORDER,
    CODE_BG,
    CODE_TEXT,
    FONT_MONO,
    INLINE_CODE_BG,
    INLINE_CODE_TEXT,
    INPUT,
    PADDING,
    RADIUS,
    SIDEBAR_WIDTH,
    SPACING,
    SURFACE,
    TEXT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


class PatrickWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Patrick")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(760, 600)
        self.setObjectName("patrick_window")

        self.sidebar = SidebarWidget()
        self.header = PatrickHeader()
        self.chat = ChatWidget()
        self.input_bar = InputBar()

        self._build_ui()
        self.apply_theme()
        self._restore_geometry()

    def _build_ui(self) -> None:
        container = QWidget(self)
        container.setObjectName("root")

        root_layout = QHBoxLayout(container)
        root_layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        root_layout.setSpacing(SPACING)

        self.sidebar.setFixedWidth(SIDEBAR_WIDTH)
        root_layout.addWidget(self.sidebar)

        main_panel = QWidget()
        main_layout = QVBoxLayout(main_panel)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(SPACING)

        main_layout.addWidget(self.header)
        main_layout.addWidget(self.chat, stretch=1)
        main_layout.addWidget(self.input_bar)

        root_layout.addWidget(main_panel, stretch=1)
        self.setCentralWidget(container)

    def apply_theme(self) -> None:
        self.setStyleSheet(
            f"""
            QMainWindow#patrick_window {{
                background: {BACKGROUND};
                color: {TEXT};
            }}
            QWidget#root {{
                background: {BACKGROUND};
            }}
            QWidget {{
                color: {TEXT};
            }}
            QFrame#panel {{
                background: {SURFACE};
                border: 1px solid {BORDER};
                border-radius: {RADIUS}px;
            }}
            QPushButton {{
                background: {SURFACE};
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: {RADIUS // 2}px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background: {INPUT};
            }}
            QLabel[class="code"] {{
                background: {CODE_BG};
                color: {CODE_TEXT};
            }}
            pre.codeblock {{
                background: {CODE_BG};
                color: {CODE_TEXT};
                border: 1px solid {BORDER};
                border-radius: {RADIUS // 2}px;
                padding: 10px 12px;
                font-family: '{FONT_MONO}';
                font-size: 11px;
                margin: 6px 0;
            }}
            code.inline {{
                background: {INLINE_CODE_BG};
                color: {INLINE_CODE_TEXT};
                border-radius: 4px;
                padding: 1px 5px;
                font-family: '{FONT_MONO}';
                font-size: 11px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 5px;
                min-height: 24px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {ACCENT};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            """
        )

    def _restore_geometry(self) -> None:
        settings = QSettings("Patrick", "Desktop")
        geometry = settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

    def closeEvent(self, event) -> None:
        settings = QSettings("Patrick", "Desktop")
        settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def update_context(self, context: PatrickContext) -> None:
        self.header.update_context(context)