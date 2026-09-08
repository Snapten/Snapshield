"""
ui/pages/server_sync.py

Server Sync: one-click refresh of roles/channels/guild info from
Discord, so dropdowns and lists across the app stay current without
restarting SnapShield.
"""

from __future__ import annotations

from typing import Callable

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from storage.json_store import DataManager
from ui.widgets import Card, Toast, page_header


class ServerSyncPage(QWidget):
    def __init__(self, data: DataManager, request_refresh_all: Callable[[], None]):
        super().__init__()
        self.data = data
        self.request_refresh_all = request_refresh_all

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        layout.addWidget(
            page_header(
                "Server Sync",
                "Server owners often add channels or roles while SnapShield is open — sync anytime, no restart needed",
            )
        )

        card = Card()
        card.add(QLabel("Pull the latest roles and channels from your connected Discord server."))

        btn_row = QHBoxLayout()
        self.fetch_channels_btn = QPushButton("Fetch Channels")
        self.fetch_channels_btn.clicked.connect(self.request_refresh_all)
        self.fetch_roles_btn = QPushButton("Fetch Roles")
        self.fetch_roles_btn.clicked.connect(self.request_refresh_all)
        self.refresh_btn = QPushButton("Refresh Discord Data")
        self.refresh_btn.setObjectName("primary")
        self.refresh_btn.clicked.connect(self._refresh)
        btn_row.addWidget(self.fetch_channels_btn)
        btn_row.addWidget(self.fetch_roles_btn)
        btn_row.addWidget(self.refresh_btn)
        btn_row.addStretch(1)
        row_widget = QWidget()
        row_widget.setLayout(btn_row)
        card.add(row_widget)

        layout.addWidget(card)

        self.toast = Toast()
        layout.addWidget(self.toast)
        layout.addStretch(1)

    def _refresh(self) -> None:
        self.request_refresh_all()
        self.toast.show_message("Refreshing roles, channels, and server info...", "info")
