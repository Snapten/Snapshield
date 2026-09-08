"""
ui/main_window.py

The main application window: a sidebar for navigation plus a stacked
widget holding each feature page. Owns the DataManager (JSON storage)
and the BotThread (Discord connection), and wires bot signals through
to whichever pages need them.
"""

from __future__ import annotations

import logging

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from bot.bot_thread import BotThread
from storage.json_store import DataManager
from ui.pages.auto_roles import AutoRolesPage
from ui.pages.bot_settings import BotSettingsPage
from ui.pages.dashboard import DashboardPage
from ui.pages.logging_page import LoggingPage
from ui.pages.moderation import ModerationPage
from ui.pages.reaction_roles import ReactionRolesPage
from ui.pages.server_sync import ServerSyncPage
from ui.pages.social_notifications import SocialNotificationsPage
from ui.pages.strike_system import StrikeSystemPage
from ui.pages.word_filters import WordFiltersPage

logger = logging.getLogger("snapshield.ui")

NAV_ITEMS = [
    ("Dashboard", "dashboard"),
    ("Auto Roles", "auto_roles"),
    ("Reaction Roles", "reaction_roles"),
    ("Moderation", "moderation"),
    ("Strike System", "strike_system"),
    ("Word Filters", "word_filters"),
    ("Social Notifications", "social"),
    ("Logging", "logging"),
    ("Bot Settings", "bot_settings"),
    ("Server Sync", "server_sync"),
]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SnapShield - Discord Bot")
        self.resize(1180, 760)
        self.setMinimumSize(980, 640)

        self.data = DataManager()
        self.bot_thread: BotThread | None = None

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, stretch=1)

        self.pages: dict[str, QWidget] = {}
        self._build_pages()

        self.nav_group.buttons()[0].setChecked(True)
        self.stack.setCurrentWidget(self.pages["dashboard"])

        # Give the window a moment to finish constructing before possibly
        # kicking off a connection attempt.
        QTimer.singleShot(300, self._maybe_auto_connect)

    def _maybe_auto_connect(self) -> None:
        settings = self.data.settings.load()
        if settings.get("auto_connect") and settings.get("bot_token"):
            self.pages["bot_settings"].attempt_auto_connect()

    # ------------------------------------------------------------------ #
    # Sidebar
    # ------------------------------------------------------------------ #
    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(2)

        title = QLabel("SnapShield")
        title.setObjectName("appTitle")
        layout.addWidget(title)

        subtitle = QLabel("Discord bot")
        subtitle.setObjectName("appSubtitle")
        layout.addWidget(subtitle)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        for label, key in NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _checked, k=key: self._navigate(k))
            self.nav_group.addButton(btn)
            layout.addWidget(btn)

        layout.addStretch(1)
        return sidebar

    def _navigate(self, key: str) -> None:
        page = self.pages.get(key)
        if page:
            self.stack.setCurrentWidget(page)
            if hasattr(page, "on_shown"):
                page.on_shown()

    # ------------------------------------------------------------------ #
    # Pages
    # ------------------------------------------------------------------ #
    def _build_pages(self) -> None:
        dashboard = DashboardPage(self.data)
        bot_settings = BotSettingsPage(self.data, on_connect=self._connect_bot, on_disconnect=self._disconnect_bot)
        auto_roles = AutoRolesPage(self.data, request_fetch_roles=self._fetch_roles)
        reaction_roles = ReactionRolesPage(self.data, request_fetch_roles=self._fetch_roles,
                                            request_fetch_channels=self._fetch_channels,
                                            send_panel=self._send_reaction_panel,
                                            delete_panel=self._delete_reaction_panel,
                                            edit_panel=self._edit_reaction_panel)
        moderation = ModerationPage(self.data, request_fetch_channels=self._fetch_channels)
        strike_system = StrikeSystemPage(self.data, on_save_reset_settings=self._refresh_strike_schedule)
        word_filters = WordFiltersPage(self.data)
        logging_page = LoggingPage(self.data, request_fetch_channels=self._fetch_channels)
        server_sync = ServerSyncPage(self.data, request_refresh_all=self._refresh_all)
        social = SocialNotificationsPage(
            self.data,
            request_fetch_channels=self._fetch_channels,
            request_fetch_roles=self._fetch_roles,
            test_twitch_credentials=self._test_twitch_credentials,
        )

        self.pages = {
            "dashboard": dashboard,
            "bot_settings": bot_settings,
            "auto_roles": auto_roles,
            "reaction_roles": reaction_roles,
            "moderation": moderation,
            "strike_system": strike_system,
            "word_filters": word_filters,
            "logging": logging_page,
            "server_sync": server_sync,
            "social": social,
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

    # ------------------------------------------------------------------ #
    # Bot lifecycle (delegated to BotThread)
    # ------------------------------------------------------------------ #
    def _connect_bot(self, token: str, guild_id: str) -> None:
        if self.bot_thread and self.bot_thread.isRunning():
            self.pages["bot_settings"].set_status(False, "Already connected. Disconnect first.")
            return

        self.bot_thread = BotThread(self.data, token, guild_id)
        self.bot_thread.status_changed.connect(self._on_status_changed)
        self.bot_thread.guild_info.connect(self._on_guild_info)
        self.bot_thread.roles_fetched.connect(self._on_roles_fetched)
        self.bot_thread.channels_fetched.connect(self._on_channels_fetched)
        self.bot_thread.log_event.connect(self._on_log_event)
        self.bot_thread.error_occurred.connect(self._on_error)
        self.bot_thread.token_invalid.connect(self._on_token_invalid)
        self.bot_thread.coro_result.connect(self._on_coro_result)
        self.bot_thread.finished.connect(self._on_thread_finished)
        self.bot_thread.start()
        self.pages["bot_settings"].set_status(False, "Connecting...")

    def _disconnect_bot(self) -> None:
        if self.bot_thread:
            self.bot_thread.stop()
            self.pages["bot_settings"].set_status(False, "Disconnecting...")

    def _on_thread_finished(self) -> None:
        self.pages["bot_settings"].set_status(False, "Offline")
        self.pages["dashboard"].set_bot_status(False)

    def _on_status_changed(self, online: bool, message: str) -> None:
        self.pages["bot_settings"].set_status(online, message)
        self.pages["dashboard"].set_bot_status(online)

    def _on_guild_info(self, info: dict) -> None:
        self.pages["dashboard"].set_guild_info(info)

    def _on_roles_fetched(self, roles: list) -> None:
        self.pages["auto_roles"].populate_roles(roles)
        self.pages["reaction_roles"].populate_roles(roles)
        self.pages["social"].populate_roles(roles)

    def _on_channels_fetched(self, channels: list) -> None:
        self.pages["moderation"].populate_channels(channels)
        self.pages["reaction_roles"].populate_channels(channels)
        self.pages["logging"].populate_channels(channels)
        self.pages["social"].populate_channels(channels)
        self.pages["dashboard"].refresh_counts()

    def _on_log_event(self, entry: dict) -> None:
        self.pages["logging"].append_history(entry)
        self.pages["dashboard"].refresh_counts()

    def _on_error(self, message: str) -> None:
        self.pages["bot_settings"].show_error(message)

    def _on_token_invalid(self, message: str) -> None:
        self.pages["bot_settings"].set_status(False, message)

    def _on_coro_result(self, callback, result) -> None:
        """Runs on the Qt main thread (queued connection) -- safe to call
        UI-touching callbacks here."""
        callback(result)

    # ------------------------------------------------------------------ #
    # Bot command helpers used by pages
    # ------------------------------------------------------------------ #
    def _fetch_roles(self) -> None:
        if self.bot_thread and self.bot_thread.isRunning():
            self.bot_thread.request_fetch_roles()
        else:
            self.pages["bot_settings"].show_error("Connect the bot before fetching roles.")

    def _fetch_channels(self) -> None:
        if self.bot_thread and self.bot_thread.isRunning():
            self.bot_thread.request_fetch_channels()
        else:
            self.pages["bot_settings"].show_error("Connect the bot before fetching channels.")

    def _refresh_all(self) -> None:
        if self.bot_thread and self.bot_thread.isRunning():
            self.bot_thread.request_refresh_all()
        else:
            self.pages["bot_settings"].show_error("Connect the bot before refreshing.")

    def _refresh_strike_schedule(self) -> None:
        if self.bot_thread and self.bot_thread.isRunning():
            self.bot_thread.request_refresh_strike_schedule()
        # If the bot isn't connected there's nothing to reschedule --
        # the saved setting is picked up automatically next time it starts.

    def _send_reaction_panel(self, channel_id: str, embed_config: dict, mappings: list, callback) -> None:
        if not (self.bot_thread and self.bot_thread.isRunning() and self.bot_thread.bot):
            callback(None)
            return
        import asyncio

        async def _task():
            return await self.bot_thread.bot.send_reaction_panel(int(channel_id), embed_config, mappings)

        future = asyncio.run_coroutine_threadsafe(_task(), self.bot_thread.loop)
        self._attach_result(future, callback, default=None)

    def _delete_reaction_panel(self, panel: dict, callback) -> None:
        if not (self.bot_thread and self.bot_thread.isRunning() and self.bot_thread.bot):
            callback(False)
            return
        import asyncio
        future = asyncio.run_coroutine_threadsafe(self.bot_thread.bot.delete_reaction_panel(panel), self.bot_thread.loop)
        self._attach_result(future, callback, default=False)

    def _edit_reaction_panel(self, panel: dict, embed_config: dict, callback) -> None:
        if not (self.bot_thread and self.bot_thread.isRunning() and self.bot_thread.bot):
            callback(False)
            return
        import asyncio
        future = asyncio.run_coroutine_threadsafe(
            self.bot_thread.bot.edit_reaction_panel(panel, embed_config), self.bot_thread.loop
        )
        self._attach_result(future, callback, default=False)

    def _test_twitch_credentials(self, callback) -> None:
        """Attempt a live Twitch auth check right now, so the Social
        Notifications page can give immediate feedback instead of
        waiting for the next background poll cycle."""
        if not (self.bot_thread and self.bot_thread.isRunning() and self.bot_thread.bot):
            callback(None)  # page treats a falsy result as "bot not connected"
            return
        import asyncio
        future = asyncio.run_coroutine_threadsafe(
            self.bot_thread.bot.test_twitch_credentials(), self.bot_thread.loop
        )
        self._attach_result(future, callback, default=None)

    def _attach_result(self, future, callback, default) -> None:
        """Attach a done-callback that hands the result back to the Qt
        main thread via the coro_result signal, instead of invoking the
        UI callback directly on the asyncio event-loop thread."""
        bot_thread = self.bot_thread

        def _on_done(fut):
            try:
                result = fut.result()
            except Exception:  # noqa: BLE001
                result = default
            bot_thread.coro_result.emit(callback, result)

        future.add_done_callback(_on_done)

    # ------------------------------------------------------------------ #
    def closeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        if self.bot_thread and self.bot_thread.isRunning():
            self.bot_thread.stop()
            self.bot_thread.wait(3000)
        event.accept()
