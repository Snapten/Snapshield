"""
ui/pages/bot_settings.py

Bot Settings page: token / client id / guild id entry, connect /
disconnect / test-connection controls, and a masked, validated token
field.
"""

from __future__ import annotations

import re
from typing import Callable

from PyQt6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from storage.json_store import DataManager
from ui.widgets import Card, Toast, page_header

# Discord bot tokens are structured, base64-like strings. This is a
# light sanity check only -- real validation happens when we actually
# attempt to log in.
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_\-\.]{20,}$")


class BotSettingsPage(QWidget):
    def __init__(self, data: DataManager, on_connect: Callable[[str, str], None], on_disconnect: Callable[[], None]):
        super().__init__()
        self.data = data
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        layout.addWidget(page_header("Bot Settings", "Connect SnapShield to your Discord bot application"))

        card = Card()
        form = QFormLayout()
        form.setSpacing(10)

        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setPlaceholderText("Paste your bot token")
        self.reveal_btn = QPushButton("Show")
        self.reveal_btn.setFixedWidth(70)
        self.reveal_btn.clicked.connect(self._toggle_reveal)

        token_row = QHBoxLayout()
        token_row.addWidget(self.token_input)
        token_row.addWidget(self.reveal_btn)
        token_row_widget = QWidget()
        token_row_widget.setLayout(token_row)
        form.addRow("Bot Token", token_row_widget)

        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Application / Client ID")
        form.addRow("Client ID", self.client_id_input)

        self.guild_id_input = QLineEdit()
        self.guild_id_input.setPlaceholderText("Server (Guild) ID")
        form.addRow("Guild ID", self.guild_id_input)

        card.add(self._wrap(form))

        self.auto_connect_checkbox = QCheckBox("Auto-connect on startup")
        self.auto_connect_checkbox.stateChanged.connect(lambda _state: self._save_settings())
        card.add(self.auto_connect_checkbox)

        layout.addWidget(card)

        # Status row
        status_card = Card()
        status_layout = QHBoxLayout()
        self.status_label = QLabel("❌ Offline")
        self.status_label.setObjectName("statusOffline")
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch(1)
        status_card.add(self._wrap(status_layout))
        layout.addWidget(status_card)

        # Buttons
        btn_row = QHBoxLayout()
        self.connect_btn = QPushButton("Connect Bot")
        self.connect_btn.setObjectName("primary")
        self.connect_btn.clicked.connect(self._handle_connect)

        self.disconnect_btn = QPushButton("Disconnect Bot")
        self.disconnect_btn.setObjectName("danger")
        self.disconnect_btn.clicked.connect(self._handle_disconnect)

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self._handle_test)

        btn_row.addWidget(self.connect_btn)
        btn_row.addWidget(self.disconnect_btn)
        btn_row.addWidget(self.test_btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        self.toast = Toast()
        layout.addWidget(self.toast)
        layout.addStretch(1)

        self._load_settings()

    @staticmethod
    def _wrap(inner_layout) -> QWidget:
        w = QWidget()
        if isinstance(inner_layout, QFormLayout) or isinstance(inner_layout, QHBoxLayout):
            w.setLayout(inner_layout)
        return w

    def _toggle_reveal(self) -> None:
        if self.token_input.echoMode() == QLineEdit.EchoMode.Password:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.reveal_btn.setText("Hide")
        else:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.reveal_btn.setText("Show")

    def _load_settings(self) -> None:
        settings = self.data.settings.load()
        self.token_input.setText(settings.get("bot_token", ""))
        self.client_id_input.setText(settings.get("client_id", ""))
        self.guild_id_input.setText(settings.get("guild_id", ""))
        self.auto_connect_checkbox.setChecked(settings.get("auto_connect", False))

    def _save_settings(self) -> None:
        self.data.settings.save({
            "bot_token": self.token_input.text().strip(),
            "client_id": self.client_id_input.text().strip(),
            "guild_id": self.guild_id_input.text().strip(),
            "auto_connect": self.auto_connect_checkbox.isChecked(),
        })

    def _validate_token_format(self, token: str) -> bool:
        return bool(TOKEN_PATTERN.match(token))

    def _handle_connect(self) -> None:
        token = self.token_input.text().strip()
        guild_id = self.guild_id_input.text().strip()

        if not token:
            self.toast.show_message("Enter a bot token before connecting.", "error")
            return
        if not self._validate_token_format(token):
            self.toast.show_message("That token doesn't look valid. Double-check it and try again.", "error")
            return

        self._save_settings()
        self.set_status(False, "Connecting...")
        self.on_connect(token, guild_id)

    def _handle_disconnect(self) -> None:
        self.on_disconnect()

    def attempt_auto_connect(self) -> None:
        """Called once at startup by MainWindow if the user has enabled
        'Auto-connect on startup' and a token is already saved."""
        token = self.token_input.text().strip()
        if not token or not self._validate_token_format(token):
            return
        self.set_status(False, "Auto-connecting...")
        self.on_connect(token, self.guild_id_input.text().strip())

    def _handle_test(self) -> None:
        token = self.token_input.text().strip()
        if not token:
            self.toast.show_message("Enter a bot token to test.", "error")
            return
        if not self._validate_token_format(token):
            self.toast.show_message("Token format looks invalid.", "error")
            return
        self.toast.show_message(
            "Token format looks valid. Click 'Connect Bot' to verify it against Discord.", "info"
        )

    def set_status(self, online: bool, message: str = "") -> None:
        if online:
            self.status_label.setText("✅ Online")
            self.status_label.setObjectName("statusOnline")
        else:
            self.status_label.setText("❌ Offline")
            self.status_label.setObjectName("statusOffline")
        # Re-apply stylesheet so objectName change takes visual effect.
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        if message:
            self.toast.show_message(message, "success" if online else "info")

    def show_error(self, message: str) -> None:
        self.toast.show_message(message, "error")
