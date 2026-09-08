"""
ui/pages/dashboard.py

Overview page: bot status, connected server info, and quick counts of
configured moderation data.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from storage.json_store import DataManager
from ui.widgets import StatCard, page_header


class DashboardPage(QWidget):
    def __init__(self, data: DataManager):
        super().__init__()
        self.data = data

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        layout.addWidget(page_header("Dashboard", "Live overview of your SnapShield bot"))

        grid = QGridLayout()
        grid.setSpacing(14)

        self.card_status = StatCard("Bot Status", "Offline")
        self.card_server = StatCard("Connected Server", "-")
        self.card_moderated = StatCard("Moderated Channels", "0")
        self.card_strike_words = StatCard("Strike Words", "0")
        self.card_banned_words = StatCard("Banned Words", "0")
        self.card_panels = StatCard("Reaction Role Panels", "0")

        grid.addWidget(self.card_status, 0, 0)
        grid.addWidget(self.card_server, 0, 1)
        grid.addWidget(self.card_moderated, 0, 2)
        grid.addWidget(self.card_strike_words, 1, 0)
        grid.addWidget(self.card_banned_words, 1, 1)
        grid.addWidget(self.card_panels, 1, 2)

        layout.addLayout(grid)

        info_grid = QGridLayout()
        info_grid.setSpacing(14)
        self.card_members = StatCard("Member Count", "-")
        self.card_channels = StatCard("Channel Count", "-")
        self.card_roles = StatCard("Role Count", "-")
        info_grid.addWidget(self.card_members, 0, 0)
        info_grid.addWidget(self.card_channels, 0, 1)
        info_grid.addWidget(self.card_roles, 0, 2)
        layout.addLayout(info_grid)

        layout.addStretch(1)

        self.refresh_counts()

    def on_shown(self) -> None:
        self.refresh_counts()

    def set_bot_status(self, online: bool) -> None:
        self.card_status.set_value("✅ Online" if online else "❌ Offline")

    def set_guild_info(self, info: dict) -> None:
        if info.get("found"):
            self.card_server.set_value(info.get("name", "-"))
            self.card_members.set_value(str(info.get("member_count", "-")))
            self.card_channels.set_value(str(info.get("channel_count", "-")))
            self.card_roles.set_value(str(info.get("role_count", "-")))
        else:
            self.card_server.set_value("Not found")

    def refresh_counts(self) -> None:
        channels_cfg = self.data.channels.load()
        strike_words_cfg = self.data.strike_words.load()
        banned_words_cfg = self.data.banned_words.load()
        panels_cfg = self.data.reaction_roles.load()

        self.card_moderated.set_value(str(len(channels_cfg.get("moderated_channel_ids", []))))
        self.card_strike_words.set_value(str(len(strike_words_cfg.get("words", []))))
        self.card_banned_words.set_value(str(len(banned_words_cfg.get("words", []))))
        self.card_panels.set_value(str(len(panels_cfg.get("panels", []))))
