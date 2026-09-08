"""
bot/bot_thread.py

Runs the discord.py bot on a background QThread with its own asyncio
event loop, so the PyQt6 UI thread is never blocked. Communication back
to the UI happens exclusively through Qt signals (thread-safe by design).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import discord
from PyQt6.QtCore import QThread, pyqtSignal

from bot.discord_bot import ModerationBot
from storage.json_store import DataManager

logger = logging.getLogger("snapshield.bot_thread")


class BotThread(QThread):
    """
    Owns the asyncio event loop and the ModerationBot instance.

    Signals:
        status_changed(bool online, str message)
        guild_info(dict info)
        roles_fetched(list roles)
        channels_fetched(list channels)
        log_event(dict entry)
        error_occurred(str message)
        token_invalid(str message)
    """

    status_changed = pyqtSignal(bool, str)
    guild_info = pyqtSignal(dict)
    roles_fetched = pyqtSignal(list)
    channels_fetched = pyqtSignal(list)
    log_event = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    token_invalid = pyqtSignal(str)

    # Generic bridge for one-off coroutine results (e.g. reaction-panel
    # send/edit/delete) that need to hand a result back to a UI callback.
    # Emitting this from the bot thread and connecting it in the main
    # thread lets Qt queue the delivery onto the Qt (main) thread instead
    # of running the callback -- and any widget code inside it -- on the
    # asyncio event-loop thread, which Qt does not allow.
    coro_result = pyqtSignal(object, object)

    def __init__(self, data: DataManager, token: str, guild_id: Optional[str], parent=None):
        super().__init__(parent)
        self.data = data
        self.token = token
        self.guild_id = int(guild_id) if guild_id and guild_id.isdigit() else None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.bot: Optional[ModerationBot] = None
        self._stopping = False

    # ------------------------------------------------------------------ #
    # QThread entry point
    # ------------------------------------------------------------------ #
    def run(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bot = ModerationBot(self.data, emit=self._emit, guild_id=self.guild_id)
        try:
            self.loop.run_until_complete(self._start_bot())
        except discord.LoginFailure:
            self.token_invalid.emit("The bot token was rejected by Discord. Please check it and try again.")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Bot thread crashed")
            self.error_occurred.emit(f"Bot stopped unexpectedly: {exc}")
        finally:
            try:
                self.loop.run_until_complete(self._shutdown())
            except Exception:  # noqa: BLE001
                pass
            self.loop.close()

    async def _start_bot(self) -> None:
        # reconnect=True (the default) lets discord.py's gateway
        # transparently reconnect/resume on transient network drops; the
        # bot's keep-alive task adds a second layer of insurance on top.
        await self.bot.start(self.token, reconnect=True)

    async def _shutdown(self) -> None:
        if self.bot and not self.bot.is_closed():
            await self.bot.close()

    # ------------------------------------------------------------------ #
    # Emit bridge: called from the asyncio thread, forwards to Qt signals
    # ------------------------------------------------------------------ #
    def _emit(self, event: str, **kwargs) -> None:
        if event == "status":
            self.status_changed.emit(kwargs.get("online", False), kwargs.get("message", ""))
        elif event == "guild_info":
            self.guild_info.emit(kwargs)
        elif event == "roles_fetched":
            self.roles_fetched.emit(kwargs.get("roles", []))
        elif event == "channels_fetched":
            self.channels_fetched.emit(kwargs.get("channels", []))
        elif event == "log_event":
            self.log_event.emit(kwargs.get("entry", {}))
        elif event == "error":
            self.error_occurred.emit(kwargs.get("message", "Unknown error"))

    # ------------------------------------------------------------------ #
    # Thread-safe commands invoked from the UI thread
    # ------------------------------------------------------------------ #
    def _run_coro(self, coro) -> None:
        if self.loop and self.bot and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, self.loop)

    def request_fetch_roles(self) -> None:
        if self.bot:
            self._run_coro(self.bot.fetch_roles())

    def request_fetch_channels(self) -> None:
        if self.bot:
            self._run_coro(self.bot.fetch_channels())

    def request_refresh_all(self) -> None:
        if self.bot:
            self._run_coro(self.bot.refresh_all())

    def request_refresh_strike_schedule(self) -> None:
        if self.bot:
            self._run_coro(self.bot.refresh_strike_reset_schedule())

    def stop(self) -> None:
        self._stopping = True
        if self.loop and self.bot:
            asyncio.run_coroutine_threadsafe(self._shutdown(), self.loop)
