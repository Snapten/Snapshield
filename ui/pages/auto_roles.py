"""
ui/pages/auto_roles.py

Auto Role System: pick one or more roles (fetched live from Discord)
that new members automatically receive when they join.
"""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from storage.json_store import DataManager
from ui.widgets import Card, Toast, page_header


class AutoRolesPage(QWidget):
    def __init__(self, data: DataManager, request_fetch_roles: Callable[[], None]):
        super().__init__()
        self.data = data
        self.request_fetch_roles = request_fetch_roles

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        layout.addWidget(page_header("Auto Roles", "Automatically assign roles when a member joins"))

        card = Card()
        btn_row = QHBoxLayout()
        self.fetch_btn = QPushButton("Fetch Roles")
        self.fetch_btn.clicked.connect(self.request_fetch_roles)
        btn_row.addWidget(self.fetch_btn)
        btn_row.addStretch(1)
        row_widget = QWidget()
        row_widget.setLayout(btn_row)
        card.add(row_widget)

        self.role_list = QListWidget()
        self.role_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        card.add(self.role_list)

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
        roles_cfg = self.data.roles.load()
        self.populate_roles(roles_cfg.get("cached_roles", []), preserve_selection=True)

    def populate_roles(self, roles: list, preserve_selection: bool = False) -> None:
        selected_ids = set(self.data.roles.load().get("auto_role_ids", []))
        self.role_list.clear()
        for role in roles:
            item = QListWidgetItem(role["name"])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setData(Qt.ItemDataRole.UserRole, role["id"])
            item.setCheckState(
                Qt.CheckState.Checked if role["id"] in selected_ids else Qt.CheckState.Unchecked
            )
            self.role_list.addItem(item)

    def _save(self) -> None:
        selected = []
        for i in range(self.role_list.count()):
            item = self.role_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.data(Qt.ItemDataRole.UserRole))
        self.data.roles.update(lambda d: {**d, "auto_role_ids": selected})
        self.toast.show_message(f"Saved {len(selected)} auto role(s).", "success")
