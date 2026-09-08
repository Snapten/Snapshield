"""
ui/pages/moderation.py

Moderation Channel Control: choose exactly which text channels are
watched by the word-filter / strike engine. Channels are fetched live
from Discord and shown as a checkbox list.
"""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from storage.json_store import DataManager
from ui.widgets import Card, Toast, page_header


class ModerationPage(QWidget):
    def __init__(self, data: DataManager, request_fetch_channels: Callable[[], None]):
        super().__init__()
        self.data = data
        self.request_fetch_channels = request_fetch_channels

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        layout.addWidget(page_header("Moderation", "Choose exactly which channels SnapShield monitors"))

        card = Card()
        btn_row = QHBoxLayout()
        self.fetch_btn = QPushButton("Fetch Channels")
        self.fetch_btn.clicked.connect(self.request_fetch_channels)
        self.refresh_btn = QPushButton("Refresh Channels")
        self.refresh_btn.clicked.connect(self.request_fetch_channels)
        btn_row.addWidget(self.fetch_btn)
        btn_row.addWidget(self.refresh_btn)
        btn_row.addStretch(1)
        row_widget = QWidget()
        row_widget.setLayout(btn_row)
        card.add(row_widget)

        self.channel_list = QListWidget()
        card.add(self.channel_list)

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("primary")
        self.save_btn.clicked.connect(self._save)
        card.add(self.save_btn)

        layout.addWidget(card)

        self.toast = Toast()
        layout.addWidget(self.toast)
        layout.addStretch(1)

        self._load_from_cache()

    def _load_from_cache(self) -> None:
        channels_cfg = self.data.channels.load()
        self.populate_channels(channels_cfg.get("cached_channels", []))

    def populate_channels(self, channels: list) -> None:
        selected_ids = set(self.data.channels.load().get("moderated_channel_ids", []))
        self.channel_list.clear()
        for ch in channels:
            item = QListWidgetItem(f"# {ch['name']}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setData(Qt.ItemDataRole.UserRole, ch["id"])
            item.setCheckState(
                Qt.CheckState.Checked if ch["id"] in selected_ids else Qt.CheckState.Unchecked
            )
            self.channel_list.addItem(item)

    def _save(self) -> None:
        selected = []
        for i in range(self.channel_list.count()):
            item = self.channel_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.data(Qt.ItemDataRole.UserRole))
        self.data.channels.update(lambda d: {**d, "moderated_channel_ids": selected})
        self.toast.show_message(f"Now monitoring {len(selected)} channel(s).", "success")
