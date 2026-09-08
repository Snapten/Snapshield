"""
storage/json_store.py

Thread-safe JSON file storage layer for SnapShield.

Every configuration domain (settings, roles, channels, strikes, word
filters, reaction roles, logs) is persisted as its own JSON file inside
the `data/` directory. Files are created automatically with sensible
defaults the first time they are accessed, so the application never
crashes because a file is missing.
"""

from __future__ import annotations

import json
import os
import shutil
import threading
from pathlib import Path
from typing import Any, Dict


class JSONStore:
    """
    A small, thread-safe key-value JSON persistence helper.

    Each `JSONStore` instance is bound to a single file (e.g. settings.json)
    and a default value that is written the first time the file does not
    exist or is unreadable. All reads/writes are guarded by a lock so the
    UI thread and the bot's asyncio thread can safely share the same file.
    """

    def __init__(self, data_dir: Path, filename: str, default: Any) -> None:
        self._path = data_dir / filename
        self._default = default
        self._lock = threading.RLock()
        self._data_dir = data_dir
        self._ensure_exists()

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _ensure_exists(self) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write_raw(self._default)

    def _write_raw(self, data: Any) -> None:
        """Write atomically: write to a temp file, then replace."""
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        shutil.move(str(tmp_path), str(self._path))

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def load(self) -> Any:
        """Load and return the JSON contents, recovering from corruption."""
        with self._lock:
            try:
                with open(self._path, "r", encoding="utf-8") as fh:
                    return json.load(fh)
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                # File missing or corrupted -- back up the bad file (if any)
                # and reset to the default so the app keeps running.
                if self._path.exists():
                    corrupt_backup = self._path.with_suffix(".corrupt.bak")
                    try:
                        shutil.copy(self._path, corrupt_backup)
                    except OSError:
                        pass
                self._write_raw(self._default)
                return json.loads(json.dumps(self._default))

    def save(self, data: Any) -> None:
        """Persist data to disk."""
        with self._lock:
            self._write_raw(data)

    def update(self, mutator) -> Any:
        """
        Load the current data, pass it to `mutator(data) -> data`, then
        save the result. Returns the new data. Useful for atomic
        read-modify-write operations.
        """
        with self._lock:
            data = self.load()
            new_data = mutator(data)
            self._write_raw(new_data)
            return new_data


class DataManager:
    """
    Central access point for all SnapShield JSON stores.

    Creates/opens every JSON file the application needs under `data/`
    and exposes them as named attributes.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.settings = JSONStore(self.data_dir, "settings.json", {
            "bot_token": "",
            "client_id": "",
            "guild_id": "",
            "auto_connect": False,
        })

        self.roles = JSONStore(self.data_dir, "roles.json", {
            "cached_roles": [],       # [{id, name, color}]
            "auto_role_ids": [],      # roles assigned on join
        })

        self.channels = JSONStore(self.data_dir, "channels.json", {
            "cached_channels": [],        # [{id, name}]
            "moderated_channel_ids": [],  # channels the filter watches
            "log_channel_id": "",
        })

        self.strikes = JSONStore(self.data_dir, "strikes.json", {
            "levels": [],       # [{level, action, duration_minutes, message}]
            "user_strikes": {}, # {user_id: strike_count}
            "auto_reset_enabled": True,
            "auto_reset_hours": 12,
        })

        self.strike_words = JSONStore(self.data_dir, "strike_words.json", {
            "words": [],
        })

        self.banned_words = JSONStore(self.data_dir, "banned_words.json", {
            "words": [],
            "action": "Kick",   # "Kick" or "Ban"
            "message": "You used prohibited language and have been removed.",
        })

        self.reaction_roles = JSONStore(self.data_dir, "reaction_roles.json", {
            "panels": [],
            # [{id, channel_id, message_id, text, mappings: [{emoji, role_id}],
            #   title, color, footer, thumbnail_url, image_url,
            #   author_name, author_icon_url}]
        })

        self.logs = JSONStore(self.data_dir, "logs.json", {
            "log_channel_id": "",
            "events": {
                "joins": True,
                "leaves": True,
                "deleted_messages": True,
                "edited_messages": True,
                "strikes": True,
                "timeouts": True,
                "kicks": True,
                "bans": True,
                "auto_roles": True,
                "social_notifications": True,
            },
            "history": [],  # rolling local log of recent events (for dashboard)
        })

        self.social_notifications = JSONStore(self.data_dir, "social_notifications.json", {
            "twitch_client_id": "",
            "twitch_client_secret": "",
            "subscriptions": [],
            # [{id, twitch_username, discord_channel_id, role_id,
            #   message_template, delete_on_end, is_live, last_stream_id,
            #   last_message_id}]
        })

    def all_stores(self) -> Dict[str, JSONStore]:
        return {
            "settings": self.settings,
            "roles": self.roles,
            "channels": self.channels,
            "strikes": self.strikes,
            "strike_words": self.strike_words,
            "banned_words": self.banned_words,
            "reaction_roles": self.reaction_roles,
            "logs": self.logs,
            "social_notifications": self.social_notifications,
        }
