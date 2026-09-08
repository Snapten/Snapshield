#!/usr/bin/env python3
"""
main.py

Entry point for SnapShield, a locally-hosted Discord moderation
desktop application built with PyQt6 and discord.py.

Run directly with:
    python main.py

Or package into a single Windows executable with:
    pyinstaller --onefile --windowed --name SnapShield main.py
"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.theme import STYLESHEET


def _base_dir() -> Path:
    """Resolve the app's base directory, whether run from source or a
    PyInstaller-frozen executable."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def setup_logging() -> None:
    base_dir = _base_dir()
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / "snapshield.log"
    handler = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))

    root = logging.getLogger("snapshield")
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    root.addHandler(console)

    # discord.py's own logger is fairly chatty; route it to the same file
    # at WARNING level so real problems are still visible.
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.WARNING)
    discord_logger.addHandler(handler)


def main() -> int:
    # Make sure relative paths (data/, logs/) resolve correctly whether
    # running from source or from the frozen .exe.
    os.chdir(_base_dir())

    setup_logging()
    logger = logging.getLogger("snapshield.main")
    logger.info("Starting SnapShield")

    app = QApplication(sys.argv)
    app.setApplicationName("SnapShield")
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()

    try:
        return app.exec()
    except Exception:  # noqa: BLE001
        logger.exception("Fatal error in application event loop")
        return 1


if __name__ == "__main__":
    sys.exit(main())
