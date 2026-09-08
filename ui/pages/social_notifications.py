"""
ui/pages/social_notifications.py

Social Notifications: connect a Twitch application, add one or more
Twitch channels to watch, and pick which Discord channel gets an
embedded "went live" notification for each one. The bot polls Twitch
every couple of minutes in the background (see bot/discord_bot.py) and
posts a rich embed -- title, live game, viewer count, and stream
thumbnail -- the moment a tracked channel goes live.
"""

from __future__ import annotations

import uuid
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from storage.json_store import DataManager
from ui.widgets import Card, Toast, page_header, hline, labeled_field


class SocialNotificationsPage(QWidget):
    def __init__(
        self,
        data: DataManager,
        request_fetch_channels: Callable[[], None],
        request_fetch_roles: Callable[[], None],
        test_twitch_credentials: Callable[[Callable], None],
    ):
        super().__init__()
        self.data = data
        self.request_fetch_channels = request_fetch_channels
        self.request_fetch_roles = request_fetch_roles
        self.test_twitch_credentials = test_twitch_credentials
        self._channels_cache: list[dict] = []
        self._roles_cache: list[dict] = []

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        layout.addWidget(
            page_header("Social Notifications", "Twitch channel goes live alert")
        )

        # -------------------------------------------------------------- #
        # Twitch application credentials
        # -------------------------------------------------------------- #
        creds_card = Card()
        creds_card.add(QLabel("Twitch Application"))

        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Twitch Client ID")
        creds_card.add(labeled_field("Client ID", self.client_id_input))

        secret_row = QHBoxLayout()
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.client_secret_input.setPlaceholderText("Twitch Client Secret")
        self.reveal_btn = QPushButton("Show")
        self.reveal_btn.setFixedWidth(70)
        self.reveal_btn.clicked.connect(self._toggle_reveal)
        secret_row.addWidget(self.client_secret_input)
        secret_row.addWidget(self.reveal_btn)
        creds_card.add(labeled_field("Client Secret", self._wrap(secret_row)))

        creds_btn_row = QHBoxLayout()
        save_creds_btn = QPushButton("Save Credentials")
        save_creds_btn.setObjectName("primary")
        save_creds_btn.clicked.connect(self._save_credentials)
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self._handle_test)
        creds_btn_row.addWidget(save_creds_btn)
        creds_btn_row.addWidget(test_btn)
        creds_btn_row.addStretch(1)
        creds_card.add(self._wrap(creds_btn_row))

        layout.addWidget(creds_card)

        # -------------------------------------------------------------- #
        # Add a Twitch channel to watch
        # -------------------------------------------------------------- #
        add_card = Card()
        add_card.add(QLabel("Add Twitch Channel"))

        fetch_row = QHBoxLayout()
        fetch_channels_btn = QPushButton("Fetch Channels")
        fetch_channels_btn.clicked.connect(self.request_fetch_channels)
        fetch_roles_btn = QPushButton("Fetch Roles")
        fetch_roles_btn.clicked.connect(self.request_fetch_roles)
        fetch_row.addWidget(fetch_channels_btn)
        fetch_row.addWidget(fetch_roles_btn)
        fetch_row.addStretch(1)
        add_card.add(self._wrap(fetch_row))

        self.twitch_username_input = QLineEdit()
        self.twitch_username_input.setPlaceholderText("Twitch username, e.g. shroud")
        add_card.add(labeled_field("Twitch Channel", self.twitch_username_input))

        self.discord_channel_combo = QComboBox()
        add_card.add(labeled_field("Discord Notification Channel", self.discord_channel_combo))

        self.role_combo = QComboBox()
        self.role_combo.addItem("(no ping)", None)
        add_card.add(labeled_field("Role to Ping (optional)", self.role_combo))

        self.message_template_input = QTextEdit()
        self.message_template_input.setFixedHeight(64)
        self.message_template_input.setPlaceholderText(
            "(optional) Custom message. Use {username}, {title}, {game} -- "
            "defaults to the stream's own title if left blank."
        )
        add_card.add(labeled_field("Custom Message (optional)", self.message_template_input))

        self.delete_on_end_checkbox = QCheckBox("Delete the notification message once the stream ends")
        add_card.add(self.delete_on_end_checkbox)

        add_btn = QPushButton("Add Channel")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self._add_subscription)
        add_card.add(add_btn)

        layout.addWidget(add_card)
        layout.addWidget(hline())

        # -------------------------------------------------------------- #
        # Tracked channels
        # -------------------------------------------------------------- #
        list_card = Card()
        list_card.add(QLabel("Tracked Channels"))
        self.subscription_list = QListWidget()
        self.subscription_list.setFixedHeight(160)
        list_card.add(self.subscription_list)

        list_btn_row = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Status")
        refresh_btn.clicked.connect(self._refresh_list)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.setObjectName("danger")
        remove_btn.clicked.connect(self._remove_subscription)
        list_btn_row.addWidget(refresh_btn)
        list_btn_row.addWidget(remove_btn)
        list_btn_row.addStretch(1)
        list_card.add(self._wrap(list_btn_row))

        layout.addWidget(list_card)

        self.toast = Toast()
        layout.addWidget(self.toast)
        layout.addStretch(1)

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        self._load_credentials()
        self._load_from_cache()
        self._refresh_list()

    @staticmethod
    def _wrap(inner_layout) -> QWidget:
        w = QWidget()
        w.setLayout(inner_layout)
        return w

    def on_shown(self) -> None:
        # Live/offline state is updated by the background bot task, so
        # pick up any changes each time the user visits this page.
        self._refresh_list()

    def _toggle_reveal(self) -> None:
        if self.client_secret_input.echoMode() == QLineEdit.EchoMode.Password:
            self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.reveal_btn.setText("Hide")
        else:
            self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.reveal_btn.setText("Show")

    # ------------------------------------------------------------------ #
    def _load_credentials(self) -> None:
        social_cfg = self.data.social_notifications.load()
        self.client_id_input.setText(social_cfg.get("twitch_client_id", ""))
        self.client_secret_input.setText(social_cfg.get("twitch_client_secret", ""))

    def _save_credentials(self) -> None:
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()
        self.data.social_notifications.update(
            lambda d: {**d, "twitch_client_id": client_id, "twitch_client_secret": client_secret}
        )
        self.toast.show_message("Twitch credentials saved.", "success")

    def _handle_test(self) -> None:
        self._save_credentials()

        def _on_result(result):
            success, message = result if result else (False, "Could not reach Twitch.")
            self.toast.show_message(message, "success" if success else "error")

        self.test_twitch_credentials(_on_result)

    def _load_from_cache(self) -> None:
        channels_cfg = self.data.channels.load()
        self.populate_channels(channels_cfg.get("cached_channels", []))
        roles_cfg = self.data.roles.load()
        self.populate_roles(roles_cfg.get("cached_roles", []))

    def populate_channels(self, channels: list) -> None:
        self._channels_cache = channels
        current = self.discord_channel_combo.currentData()
        self.discord_channel_combo.clear()
        for ch in channels:
            self.discord_channel_combo.addItem(f"# {ch['name']}", ch["id"])
        if current:
            idx = self.discord_channel_combo.findData(current)
            if idx >= 0:
                self.discord_channel_combo.setCurrentIndex(idx)

    def populate_roles(self, roles: list) -> None:
        self._roles_cache = roles
        current = self.role_combo.currentData()
        self.role_combo.clear()
        self.role_combo.addItem("(no ping)", None)
        for role in roles:
            self.role_combo.addItem(role["name"], role["id"])
        if current:
            idx = self.role_combo.findData(current)
            if idx >= 0:
                self.role_combo.setCurrentIndex(idx)

    def _add_subscription(self) -> None:
        username = self.twitch_username_input.text().strip().lstrip("@")
        if not username:
            self.toast.show_message("Enter a Twitch username first.", "error")
            return
        if self.discord_channel_combo.count() == 0:
            self.toast.show_message("Fetch and select a Discord channel first.", "error")
            return

        channel_id = self.discord_channel_combo.currentData()
        role_id = self.role_combo.currentData()
        template = self.message_template_input.toPlainText().strip()
        delete_on_end = self.delete_on_end_checkbox.isChecked()

        entry = {
            "id": str(uuid.uuid4()),
            "twitch_username": username,
            "discord_channel_id": channel_id,
            "role_id": role_id,
            "message_template": template,
            "delete_on_end": delete_on_end,
            "is_live": False,
            "last_stream_id": None,
            "last_message_id": None,
        }

        def _mutate(d):
            subs = d.get("subscriptions", [])
            if any(s.get("twitch_username", "").lower() == username.lower() for s in subs):
                return d  # already tracked, no-op
            return {**d, "subscriptions": subs + [entry]}

        before = len(self.data.social_notifications.load().get("subscriptions", []))
        self.data.social_notifications.update(_mutate)
        after = len(self.data.social_notifications.load().get("subscriptions", []))

        if after == before:
            self.toast.show_message(f"{username} is already being tracked.", "error")
            return

        self.twitch_username_input.clear()
        self.message_template_input.clear()
        self.role_combo.setCurrentIndex(0)
        self.delete_on_end_checkbox.setChecked(False)
        self._refresh_list()
        self.toast.show_message(f"Now watching {username} for live notifications.", "success")

    def _refresh_list(self) -> None:
        self.subscription_list.clear()
        social_cfg = self.data.social_notifications.load()
        channel_lookup = {ch["id"]: ch["name"] for ch in self.data.channels.load().get("cached_channels", [])}
        role_lookup = {r["id"]: r["name"] for r in self.data.roles.load().get("cached_roles", [])}
        for sub in social_cfg.get("subscriptions", []):
            status = "🔴 Live" if sub.get("is_live") else "⚪ Offline"
            channel_name = channel_lookup.get(sub.get("discord_channel_id"), "unknown channel")
            role_name = role_lookup.get(sub.get("role_id"))
            role_part = f"  🔔 @{role_name}" if role_name else ""
            delete_part = "  🗑 auto-delete" if sub.get("delete_on_end") else ""
            text = f"{status} — {sub['twitch_username']}  →  # {channel_name}{role_part}{delete_part}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, sub)
            self.subscription_list.addItem(item)

    def _remove_subscription(self) -> None:
        item = self.subscription_list.currentItem()
        if not item:
            self.toast.show_message("Select a tracked channel to remove.", "error")
            return
        sub = item.data(Qt.ItemDataRole.UserRole)
        self.data.social_notifications.update(
            lambda d: {**d, "subscriptions": [s for s in d.get("subscriptions", []) if s["id"] != sub["id"]]}
        )
        self._refresh_list()
        self.toast.show_message(f"Stopped tracking {sub['twitch_username']}.", "success")
