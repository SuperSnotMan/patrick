"""Local AI settings panel for the Patrick desktop client."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from .client import PatrickClient
from .theme import (
    ACCENT,
    ACCENT_HOVER,
    BACKGROUND,
    BORDER,
    INPUT,
    PADDING,
    RADIUS,
    SURFACE,
    TEXT,
    TEXT_SECONDARY,
)

DEFAULT_ENDPOINT = "http://127.0.0.1:11434/v1/chat/completions"
DEFAULT_MODEL = "gemma-3-1b"


class LocalAiSettingsDialog(QDialog):
    """Lets the user configure the local OpenAI-compatible provider."""

    def __init__(self, client: PatrickClient) -> None:
        super().__init__()
        self.client = client
        self.setWindowTitle("Local AI Settings")
        self.setMinimumWidth(460)
        self.setObjectName("local_ai_settings")
        self.setStyleSheet(f"QDialog {{ background: {BACKGROUND}; color: {TEXT}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        layout.setSpacing(PADDING)

        # Enabled toggle
        self.enabled_box = QCheckBox("Enable Local AI")
        self.enabled_box.setStyleSheet(f"color: {TEXT}; font-weight: bold;")
        layout.addWidget(self.enabled_box)

        hint = QLabel(
            "Use a local runtime that exposes the OpenAI Chat Completions API "
            "(e.g. Ollama, llama.cpp, LM Studio)."
        )
        hint.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # Endpoint + model fields
        form = QFormLayout()
        form.setSpacing(PADDING // 2)

        self.endpoint_field = QLineEdit()
        self.endpoint_field.setPlaceholderText(DEFAULT_ENDPOINT)
        self.endpoint_field.setStyleSheet(self._field_style())

        self.model_field = QLineEdit()
        self.model_field.setPlaceholderText(DEFAULT_MODEL)
        self.model_field.setStyleSheet(self._field_style())

        form.addRow("Endpoint URL", self.endpoint_field)
        form.addRow("Model Name", self.model_field)
        layout.addLayout(form)

        # Test button + status
        test_row = QHBoxLayout()
        self.test_button = QPushButton("Test Connection")
        self.test_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.test_button.setStyleSheet(self._accent_button_style())
        self.test_button.clicked.connect(self._on_test)
        test_row.addWidget(self.test_button)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        test_row.addWidget(self.status_label, stretch=1)
        layout.addLayout(test_row)

        layout.addStretch()

        # Save / Cancel
        actions = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(self._plain_button_style())
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet(self._accent_button_style())
        self.save_button.clicked.connect(self._on_save)
        actions.addStretch()
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.save_button)
        layout.addLayout(actions)

        self._load_settings()

    def _field_style(self) -> str:
        return (
            f"background: {INPUT}; color: {TEXT}; border: 1px solid {BORDER}; "
            f"border-radius: {RADIUS // 2}px; padding: 8px 10px;"
        )

    def _accent_button_style(self) -> str:
        return (
            f"background: {ACCENT}; color: {BACKGROUND}; border: none; "
            f"border-radius: {RADIUS // 2}px; padding: 8px 16px; font-weight: bold;"
        )

    def _plain_button_style(self) -> str:
        return (
            f"background: {SURFACE}; color: {TEXT}; border: 1px solid {BORDER}; "
            f"border-radius: {RADIUS // 2}px; padding: 8px 16px;"
        )

    def _load_settings(self) -> None:
        data = self.client.get_local_ai_settings()
        self.enabled_box.setChecked(bool(data.get("enabled", False)))
        self.endpoint_field.setText(str(data.get("endpoint", "") or ""))
        self.model_field.setText(str(data.get("model", "") or ""))

    def _current_endpoint(self) -> str:
        return self.endpoint_field.text().strip() or DEFAULT_ENDPOINT

    def _current_model(self) -> str:
        return self.model_field.text().strip() or DEFAULT_MODEL

    def _on_test(self) -> None:
        self.status_label.setText("Testing…")
        reachable = self.client.test_local_ai(self._current_endpoint(), self._current_model())
        if reachable:
            self.status_label.setText("✅ Connected")
            self.status_label.setStyleSheet(f"color: {ACCENT}; font-size: 11px;")
        else:
            self.status_label.setText("❌ Unreachable")
            self.status_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")

    def _on_save(self) -> None:
        self.client.save_local_ai_settings(
            self.enabled_box.isChecked(),
            self._current_endpoint(),
            self._current_model(),
        )
        self.accept()