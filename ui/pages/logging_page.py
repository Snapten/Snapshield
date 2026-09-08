"""
ui/pages/logging_page.py

Logging: pick a Discord channel to receive moderation event logs, plus
toggle which event categories get logged. Also shows a live local
history of recent events for quick reference inside the app.
"""

from __future__ import annotations

from typing import Callable

from PyQt6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from storage.json_store import DataManager
from ui.widgets import Card, Toast, page_header

EVENT_LABELS = {
    "joins": "Joins",
    "leaves": "Leaves",
    "deleted_messages": "Deleted Messages",
    "edited_messages": "Edited Messages",
    "strikes": "Strikes",
    "timeouts": "Timeouts",
    "kicks": "Kicks",
    "bans": "Bans",
    "auto_roles": "Auto Roles",
    "social_notifications": "Social Notifications",
}


class LoggingPage(QWidget):
    def __init__(self, data: DataManager, request_fetch_channels: Callable[[], None]):
        super().__init__()
        self.data = data
        self.request_fetch_channels = request_fetch_channels
        self.checkboxes: dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        layout.addWidget(page_header("Logging", "Send moderation events to a log channel"))

        card = Card()
        btn_row = QHBoxLayout()
        self.fetch_btn = QPushButton("Fetch Channels")
        self.fetch_btn.clicked.connect(self.request_fetch_channels)
        btn_row.addWidget(self.fetch_btn)
        btn_row.addStretch(1)
        row_widget = QWidget()
        row_widget.setLayout(btn_row)
        card.add(row_widget)

        card.add(QLabel("Log Channel"))
        self.channel_combo = QComboBox()
        card.add(self.channel_combo)

        card.add(QLabel("Events to Log"))
        for key, label in EVENT_LABELS.items():
            cb = QCheckBox(f"✅ {label}")
            self.checkboxes[key] = cb
            card.add(cb)

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("primary")
        self.save_btn.clicked.connect(self._save)
        card.add(self.save_btn)

        layout.addWidget(card)

        history_card = Card()
        history_card.add(QLabel("Recent Activity"))
        self.history_list = QListWidget()
        history_card.add(self.history_list)
        layout.addWidget(history_card)

        self.toast = Toast()
        layout.addWidget(self.toast)

        self._load()

    def _load(self) -> None:
        logs_cfg = self.data.logs.load()
        channels_cfg = self.data.channels.load()

        self.channel_combo.clear()
        cached = channels_cfg.get("cached_channels", [])
        selected_id = logs_cfg.get("log_channel_id", "")
        for ch in cached:
            self.channel_combo.addItem(f"# {ch['name']}", ch["id"])
        if selected_id:
            idx = self.channel_combo.findData(selected_id)
            if idx >= 0:
                self.channel_combo.setCurrentIndex(idx)

        events = logs_cfg.get("events", {})
        for key, cb in self.checkboxes.items():
            cb.setChecked(events.get(key, True))

        self.history_list.clear()
        for entry in reversed(logs_cfg.get("history", [])[-50:]):
            self.history_list.addItem(QListWidgetItem(f"[{entry['time']}] ({entry['category']}) {entry['text']}"))

    def populate_channels(self, channels: list) -> None:
        current = self.channel_combo.currentData()
        self.channel_combo.clear()
        for ch in channels:
            self.channel_combo.addItem(f"# {ch['name']}", ch["id"])
        if current:
            idx = self.channel_combo.findData(current)
            if idx >= 0:
                self.channel_combo.setCurrentIndex(idx)

    def append_history(self, entry: dict) -> None:
        self.history_list.insertItem(0, QListWidgetItem(f"[{entry['time']}] ({entry['category']}) {entry['text']}"))
        while self.history_list.count() > 50:
            self.history_list.takeItem(self.history_list.count() - 1)

    def _save(self) -> None:
        channel_id = self.channel_combo.currentData() or ""
        events = {key: cb.isChecked() for key, cb in self.checkboxes.items()}

        self.data.logs.update(lambda d: {**d, "log_channel_id": channel_id, "events": events})
        self.data.channels.update(lambda d: {**d, "log_channel_id": channel_id})
        self.toast.show_message("Logging settings saved.", "success")
