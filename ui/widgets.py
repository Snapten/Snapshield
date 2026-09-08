"""
ui/widgets.py

Small reusable UI building blocks shared across SnapShield's pages:
cards, section headers, and a toast-style status banner.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class Card(QWidget):
    """A rounded, bordered container used throughout the dashboard/pages.

    Capped at a comfortable max width by default so single-column forms
    don't stretch edge-to-edge on wide windows (which, combined with
    label columns in QFormLayout, was pushing fields/buttons past the
    visible area on narrower ones). Pass `max_width=None` to opt out --
    e.g. for cards placed side-by-side in a grid, where the grid cell
    already constrains the width."""

    DEFAULT_MAX_WIDTH = 760

    def __init__(self, parent: QWidget | None = None, max_width: int | None = DEFAULT_MAX_WIDTH):
        super().__init__(parent)
        self.setObjectName("card")
        if max_width is not None:
            self.setMaximumWidth(max_width)
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(16, 16, 16, 16)
        self.layout_.setSpacing(8)

    def add(self, widget: QWidget) -> None:
        self.layout_.addWidget(widget)


class StatCard(Card):
    """Dashboard summary card: a title, a big value, optional caption."""

    def __init__(self, title: str, value: str = "-", parent: QWidget | None = None):
        super().__init__(parent)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("cardValue")
        self.add(self.title_label)
        self.add(self.value_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


def page_header(title: str, subtitle: str = "") -> QWidget:
    """Standard page title + subtitle block used at the top of every page."""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    title_label = QLabel(title)
    title_label.setObjectName("pageTitle")
    layout.addWidget(title_label)

    if subtitle:
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("pageSubtitle")
        layout.addWidget(subtitle_label)

    return container


def hline() -> QFrame:
    frame = QFrame()
    frame.setObjectName("hline")
    frame.setFrameShape(QFrame.Shape.HLine)
    return frame


def labeled_field(label_text: str, widget: QWidget) -> QWidget:
    """A small label stacked above its input widget, instead of beside
    it -- keeps long labels from squeezing the field's usable width the
    way a QFormLayout label column would. Shared by any page with a lot
    of (mostly optional) fields, e.g. Reaction Roles and Social
    Notifications embed builders."""
    container = QWidget()
    v = QVBoxLayout(container)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(4)
    label = QLabel(label_text)
    label.setStyleSheet("color: #9ea2b3; font-size: 12px;")
    v.addWidget(label)
    v.addWidget(widget)
    return container


class Toast(QLabel):
    """A transient status message shown at the bottom of a page."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setVisible(False)
        self.setWordWrap(True)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(lambda: self.setVisible(False))

    def show_message(self, text: str, kind: str = "info", duration_ms: int = 4000) -> None:
        colors = {
            "info": "#4d84ff",
            "success": "#3ddc84",
            "error": "#ff5c72",
        }
        color = colors.get(kind, colors["info"])
        self.setStyleSheet(f"color: {color}; font-size: 12px; padding-top: 6px;")
        self.setText(text)
        self.setVisible(True)
        self._timer.start(duration_ms)
