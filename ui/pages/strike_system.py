"""
ui/pages/strike_system.py

Strike System: a fully configurable, unlimited-level escalation ladder.
Each level has a strike number, an action (Warning / Timeout / Kick /
Ban), an optional timeout duration, and a message sent to the member.

Layout notes: cards are capped to a comfortable maximum width instead
of stretching edge-to-edge across the window (which, combined with a
QFormLayout's field column, was pushing inputs/buttons past the
visible area on narrower windows). The page also lives inside a
QScrollArea so a long list of configured strike levels never gets
squeezed into a fixed space.
"""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from storage.json_store import DataManager
from ui.widgets import Card, Toast, page_header

ACTIONS = ["Warning", "Timeout", "Kick", "Ban"]

# Cards are capped at this width so fields/buttons don't stretch out to
# the window's edge on wide windows, and never get pushed past the
# visible area on narrow ones -- the page just leaves blank space to
# the right instead.
CARD_MAX_WIDTH = 760


class StrikeSystemPage(QWidget):
    def __init__(self, data: DataManager, on_save_reset_settings: "Callable[[], None] | None" = None):
        super().__init__()
        self.data = data
        self.on_save_reset_settings = on_save_reset_settings
        self._editing_level: int | None = None

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
        layout.addWidget(page_header("Strike System", "Build an unlimited, fully configurable escalation ladder"))

        reset_card = Card()
        reset_card.setMaximumWidth(CARD_MAX_WIDTH)
        reset_card.add(QLabel("Automatic Strike Reset"))

        self.auto_reset_checkbox = QCheckBox("Automatically clear all strikes on a schedule")
        reset_card.add(self.auto_reset_checkbox)

        reset_form = QFormLayout()
        reset_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        self.reset_hours_spin = QSpinBox()
        self.reset_hours_spin.setMinimum(1)
        self.reset_hours_spin.setMaximum(8760)  # up to 1 year
        self.reset_hours_spin.setSuffix(" hours")
        self.reset_hours_spin.setValue(12)
        self.reset_hours_spin.setMinimumWidth(140)
        reset_form.addRow("Reset every", self.reset_hours_spin)
        reset_form_widget = QWidget()
        reset_form_widget.setLayout(reset_form)
        reset_card.add(reset_form_widget)

        save_reset_btn = QPushButton("Save Reset Settings")
        save_reset_btn.setObjectName("primary")
        save_reset_btn.clicked.connect(self._save_reset_settings)
        reset_card.add(save_reset_btn)

        layout.addWidget(reset_card)

        form_card = Card()
        form_card.setMaximumWidth(CARD_MAX_WIDTH)
        self.form = QFormLayout()
        self.form.setSpacing(10)

        self.level_spin = QSpinBox()
        self.level_spin.setMinimum(1)
        self.level_spin.setMaximum(9999)
        self.level_spin.setMinimumWidth(140)
        self.form.addRow("Strike Number", self.level_spin)

        self.action_combo = QComboBox()
        self.action_combo.addItems(ACTIONS)
        self.action_combo.currentTextChanged.connect(self._on_action_changed)
        self.form.addRow("Action", self.action_combo)

        self.duration_spin = QSpinBox()
        self.duration_spin.setMinimum(1)
        self.duration_spin.setMaximum(40320)  # up to 28 days, Discord's timeout cap
        self.duration_spin.setValue(60)
        self.duration_spin.setSuffix(" minutes")
        self.duration_spin.setMinimumWidth(140)
        self.form.addRow("Timeout Duration", self.duration_spin)
        self.form.setRowVisible(self.duration_spin, False)

        self.message_input = QTextEdit()
        self.message_input.setFixedHeight(70)
        self.message_input.setPlaceholderText('e.g. "This is your first warning."')
        self.form.addRow("Message", self.message_input)

        form_widget = QWidget()
        form_widget.setLayout(self.form)
        form_card.add(form_widget)

        btn_row = QHBoxLayout()
        self.save_level_btn = QPushButton("Add / Update Level")
        self.save_level_btn.setObjectName("primary")
        self.save_level_btn.clicked.connect(self._save_level)
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self._clear_form)
        btn_row.addWidget(self.save_level_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch(1)
        btn_row_widget = QWidget()
        btn_row_widget.setLayout(btn_row)
        form_card.add(btn_row_widget)

        layout.addWidget(form_card)

        list_card = Card()
        list_card.setMaximumWidth(CARD_MAX_WIDTH)
        list_card.add(QLabel("Configured Strike Levels"))
        self.level_list = QListWidget()
        self.level_list.setFixedHeight(140)
        self.level_list.itemDoubleClicked.connect(self._load_level_for_edit)
        list_card.add(self.level_list)

        list_btn_row = QHBoxLayout()
        edit_btn = QPushButton("Edit Selected")
        edit_btn.clicked.connect(self._load_level_for_edit)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.setObjectName("danger")
        remove_btn.clicked.connect(self._remove_level)
        list_btn_row.addWidget(edit_btn)
        list_btn_row.addWidget(remove_btn)
        list_btn_row.addStretch(1)
        list_btn_row_widget = QWidget()
        list_btn_row_widget.setLayout(list_btn_row)
        list_card.add(list_btn_row_widget)

        layout.addWidget(list_card)

        self.toast = Toast()
        layout.addWidget(self.toast)
        layout.addStretch(1)

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        self._load_reset_settings()
        self._refresh_list()

    def _load_reset_settings(self) -> None:
        strikes_cfg = self.data.strikes.load()
        self.auto_reset_checkbox.setChecked(strikes_cfg.get("auto_reset_enabled", True))
        self.reset_hours_spin.setValue(int(strikes_cfg.get("auto_reset_hours", 12) or 12))

    def _save_reset_settings(self) -> None:
        enabled = self.auto_reset_checkbox.isChecked()
        hours = self.reset_hours_spin.value()
        self.data.strikes.update(lambda d: {**d, "auto_reset_enabled": enabled, "auto_reset_hours": hours})
        if self.on_save_reset_settings:
            self.on_save_reset_settings()
        state = "enabled" if enabled else "disabled"
        self.toast.show_message(f"Automatic strike reset {state}, every {hours} hour(s).", "success")

    def _on_action_changed(self, action: str) -> None:
        self.form.setRowVisible(self.duration_spin, action == "Timeout")

    def _refresh_list(self) -> None:
        self.level_list.clear()
        strikes_cfg = self.data.strikes.load()
        levels = sorted(strikes_cfg.get("levels", []), key=lambda lv: int(lv.get("level", 0)))
        for lv in levels:
            action = lv.get("action", "Warning")
            extra = f" ({lv.get('duration_minutes')} min)" if action == "Timeout" else ""
            text = f"Strike {lv.get('level')} → {action}{extra}: {lv.get('message', '')[:50]}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, lv)
            self.level_list.addItem(item)

    def _save_level(self) -> None:
        level_num = self.level_spin.value()
        action = self.action_combo.currentText()
        message = self.message_input.toPlainText().strip()
        entry = {
            "level": level_num,
            "action": action,
            "message": message,
        }
        if action == "Timeout":
            entry["duration_minutes"] = self.duration_spin.value()

        def _mutate(d):
            levels = [lv for lv in d.get("levels", []) if int(lv.get("level", 0)) != level_num]
            levels.append(entry)
            return {**d, "levels": levels}

        self.data.strikes.update(_mutate)
        self._refresh_list()
        self._clear_form()
        self.toast.show_message(f"Strike {level_num} saved.", "success")

    def _load_level_for_edit(self, *_args) -> None:
        item = self.level_list.currentItem()
        if not item:
            self.toast.show_message("Select a strike level first.", "error")
            return
        lv = item.data(Qt.ItemDataRole.UserRole)
        self.level_spin.setValue(int(lv.get("level", 1)))
        idx = self.action_combo.findText(lv.get("action", "Warning"))
        if idx >= 0:
            self.action_combo.setCurrentIndex(idx)
        self.duration_spin.setValue(int(lv.get("duration_minutes", 60)))
        self.message_input.setPlainText(lv.get("message", ""))

    def _remove_level(self) -> None:
        item = self.level_list.currentItem()
        if not item:
            self.toast.show_message("Select a strike level to remove.", "error")
            return
        lv = item.data(Qt.ItemDataRole.UserRole)
        self.data.strikes.update(
            lambda d: {**d, "levels": [x for x in d.get("levels", []) if int(x.get("level")) != int(lv.get("level"))]}
        )
        self._refresh_list()
        self.toast.show_message(f"Strike {lv.get('level')} removed.", "success")

    def _clear_form(self) -> None:
        self.level_spin.setValue(self.level_spin.value())
        self.action_combo.setCurrentIndex(0)
        self.duration_spin.setValue(60)
        self.message_input.clear()
