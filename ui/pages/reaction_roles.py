"""
ui/pages/reaction_roles.py

Reaction Role System: build fully customizable embedded reaction-role
panels (channel + embed fields + emoji-to-role mappings), then send /
modify / delete them live on Discord. Every embed field is optional --
SnapShield only sets what the user actually fills in, so a bare-minimum
panel (just mappings) still renders a clean, valid embed.

Layout notes: the whole page lives inside a QScrollArea (there are a
lot of optional fields) and short fields are arranged two-per-row in a
grid with the label placed *above* each input rather than beside it,
so long labels ("Author Icon URL") don't eat into the field's usable
width the way a QFormLayout's label column would.
"""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from storage.json_store import DataManager
from ui.widgets import Card, Toast, page_header, hline, labeled_field


class ReactionRolesPage(QWidget):
    def __init__(
        self,
        data: DataManager,
        request_fetch_roles: Callable[[], None],
        request_fetch_channels: Callable[[], None],
        send_panel: Callable[[str, dict, list, Callable], None],
        delete_panel: Callable[[dict, Callable], None],
        edit_panel: Callable[[dict, dict, Callable], None],
    ):
        super().__init__()
        self.data = data
        self.request_fetch_roles = request_fetch_roles
        self.request_fetch_channels = request_fetch_channels
        self.send_panel = send_panel
        self.delete_panel_cb = delete_panel
        self.edit_panel_cb = edit_panel

        self._pending_mappings: list[dict] = []
        self._channels_cache: list[dict] = []
        self._roles_cache: list[dict] = []

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
        layout.addWidget(page_header("Reaction Roles", "Let members self-assign roles by reacting to a message"))

        builder_card = Card()

        fetch_row = QHBoxLayout()
        fetch_channels_btn = QPushButton("Fetch Channels")
        fetch_channels_btn.clicked.connect(self.request_fetch_channels)
        fetch_roles_btn = QPushButton("Fetch Roles")
        fetch_roles_btn.clicked.connect(self.request_fetch_roles)
        fetch_row.addWidget(fetch_channels_btn)
        fetch_row.addWidget(fetch_roles_btn)
        fetch_row.addStretch(1)
        builder_card.add(self._wrap(fetch_row))

        self.channel_combo = QComboBox()
        builder_card.add(labeled_field("Channel", self.channel_combo))

        # ---------------------------------------------------------------
        # Fully customizable embed fields -- every one of these is
        # optional. Discord only requires an embed to have *something*
        # in it (a title, description, image, etc.) to be valid; the
        # mapping fields we always add cover that, so a totally blank
        # form here still produces a valid embed.
        # ---------------------------------------------------------------
        section_label = QLabel("Embed Settings  (all fields optional)")
        section_label.setStyleSheet("font-weight: 600; padding-top: 4px;")
        builder_card.add(section_label)

        embed_grid = QGridLayout()
        embed_grid.setHorizontalSpacing(16)
        embed_grid.setVerticalSpacing(14)
        embed_grid.setColumnStretch(0, 1)
        embed_grid.setColumnStretch(1, 1)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Role Selection")

        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("Hex, e.g. 5865F2")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("React below to receive a role!")
        self.description_input.setFixedHeight(72)
        self.description_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.author_name_input = QLineEdit()
        self.author_name_input.setPlaceholderText("Author name")

        self.author_icon_input = QLineEdit()
        self.author_icon_input.setPlaceholderText("Author icon URL")

        self.thumbnail_input = QLineEdit()
        self.thumbnail_input.setPlaceholderText("Thumbnail image URL")

        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("Large image URL")

        self.footer_input = QLineEdit()
        self.footer_input.setPlaceholderText("Footer text")

        embed_grid.addWidget(labeled_field("Title", self.title_input), 0, 0)
        embed_grid.addWidget(labeled_field("Color", self.color_input), 0, 1)
        embed_grid.addWidget(labeled_field("Description", self.description_input), 1, 0, 1, 2)
        embed_grid.addWidget(labeled_field("Author Name", self.author_name_input), 2, 0)
        embed_grid.addWidget(labeled_field("Author Icon URL", self.author_icon_input), 2, 1)
        embed_grid.addWidget(labeled_field("Thumbnail URL", self.thumbnail_input), 3, 0)
        embed_grid.addWidget(labeled_field("Image URL", self.image_input), 3, 1)
        embed_grid.addWidget(labeled_field("Footer Text", self.footer_input), 4, 0, 1, 2)

        embed_grid_widget = QWidget()
        embed_grid_widget.setLayout(embed_grid)
        builder_card.add(embed_grid_widget)

        builder_card.add(hline())

        mapping_label = QLabel("Emoji → Role Mappings")
        mapping_label.setStyleSheet("font-weight: 600; padding-top: 4px;")
        builder_card.add(mapping_label)

        mapping_row = QHBoxLayout()
        mapping_row.setSpacing(10)
        self.emoji_input = QLineEdit()
        self.emoji_input.setPlaceholderText("Emoji (e.g. 🎮 or :custom:)")
        self.emoji_input.setMinimumWidth(140)
        self.role_combo = QComboBox()
        self.role_combo.setMinimumWidth(160)
        add_mapping_btn = QPushButton("Add Mapping")
        add_mapping_btn.setMinimumWidth(110)
        add_mapping_btn.clicked.connect(self._add_mapping)
        mapping_row.addWidget(self.emoji_input, stretch=2)
        mapping_row.addWidget(self.role_combo, stretch=3)
        mapping_row.addWidget(add_mapping_btn, stretch=0)
        builder_card.add(self._wrap(mapping_row))

        self.mapping_list = QListWidget()
        self.mapping_list.setFixedHeight(90)
        builder_card.add(self.mapping_list)

        remove_row = QHBoxLayout()
        remove_mapping_btn = QPushButton("Remove Selected Mapping")
        remove_mapping_btn.setObjectName("danger")
        remove_mapping_btn.clicked.connect(self._remove_mapping)
        remove_row.addWidget(remove_mapping_btn)
        remove_row.addStretch(1)
        builder_card.add(self._wrap(remove_row))

        action_row = QHBoxLayout()
        send_btn = QPushButton("Send Role Message")
        send_btn.setObjectName("primary")
        send_btn.clicked.connect(self._send_message)
        clear_btn = QPushButton("Clear Form")
        clear_btn.clicked.connect(self._clear_form)
        action_row.addWidget(send_btn)
        action_row.addWidget(clear_btn)
        action_row.addStretch(1)
        builder_card.add(self._wrap(action_row))

        layout.addWidget(builder_card)
        layout.addWidget(hline())

        # Existing panels
        panels_card = Card()
        panels_card.add(QLabel("Existing Reaction Role Panels"))
        self.panel_list = QListWidget()
        self.panel_list.setFixedHeight(120)
        panels_card.add(self.panel_list)

        panel_btn_row = QHBoxLayout()
        load_btn = QPushButton("Load Into Form")
        load_btn.clicked.connect(self._load_panel_into_form)
        modify_btn = QPushButton("Modify Existing Message")
        modify_btn.clicked.connect(self._modify_panel)
        delete_btn = QPushButton("Delete Role Panel")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self._delete_panel)
        panel_btn_row.addWidget(load_btn)
        panel_btn_row.addWidget(modify_btn)
        panel_btn_row.addWidget(delete_btn)
        panel_btn_row.addStretch(1)
        panels_card.add(self._wrap(panel_btn_row))

        layout.addWidget(panels_card)

        self.toast = Toast()
        layout.addWidget(self.toast)
        layout.addStretch(1)

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        self._load_panels()

    @staticmethod
    def _wrap(inner_layout) -> QWidget:
        w = QWidget()
        w.setLayout(inner_layout)
        return w

    # ------------------------------------------------------------------ #
    def populate_channels(self, channels: list) -> None:
        self._channels_cache = channels
        self.channel_combo.clear()
        for ch in channels:
            self.channel_combo.addItem(f"# {ch['name']}", ch["id"])

    def populate_roles(self, roles: list) -> None:
        self._roles_cache = roles
        self.role_combo.clear()
        for role in roles:
            self.role_combo.addItem(role["name"], role["id"])

    def _add_mapping(self) -> None:
        emoji = self.emoji_input.text().strip()
        if not emoji or self.role_combo.count() == 0:
            self.toast.show_message("Enter an emoji and select a role first.", "error")
            return
        role_id = self.role_combo.currentData()
        role_name = self.role_combo.currentText()
        self._pending_mappings.append({"emoji": emoji, "role_id": role_id})
        item = QListWidgetItem(f"{emoji} → {role_name}")
        self.mapping_list.addItem(item)
        self.emoji_input.clear()

    def _remove_mapping(self) -> None:
        row = self.mapping_list.currentRow()
        if row < 0:
            self.toast.show_message("Select a mapping to remove.", "error")
            return
        self.mapping_list.takeItem(row)
        del self._pending_mappings[row]

    def _gather_embed_config(self) -> dict:
        """Collect every embed field from the form. All keys are present
        but any left blank by the user come through as empty strings,
        which `_build_reaction_embed` on the bot side treats as unset."""
        return {
            "title": self.title_input.text().strip(),
            "description": self.description_input.toPlainText().strip(),
            "color": self.color_input.text().strip(),
            "author_name": self.author_name_input.text().strip(),
            "author_icon_url": self.author_icon_input.text().strip(),
            "thumbnail_url": self.thumbnail_input.text().strip(),
            "image_url": self.image_input.text().strip(),
            "footer": self.footer_input.text().strip(),
        }

    def _apply_embed_config(self, embed_config: dict) -> None:
        self.title_input.setText(embed_config.get("title", ""))
        self.description_input.setPlainText(embed_config.get("description", ""))
        self.color_input.setText(embed_config.get("color", ""))
        self.author_name_input.setText(embed_config.get("author_name", ""))
        self.author_icon_input.setText(embed_config.get("author_icon_url", ""))
        self.thumbnail_input.setText(embed_config.get("thumbnail_url", ""))
        self.image_input.setText(embed_config.get("image_url", ""))
        self.footer_input.setText(embed_config.get("footer", ""))

    def _send_message(self) -> None:
        if self.channel_combo.count() == 0:
            self.toast.show_message("Fetch and select a channel first.", "error")
            return
        if not self._pending_mappings:
            self.toast.show_message("Add at least one emoji → role mapping.", "error")
            return
        channel_id = self.channel_combo.currentData()
        embed_config = self._gather_embed_config()
        mappings = list(self._pending_mappings)

        def _on_done(panel):
            if panel:
                self.data.reaction_roles.update(
                    lambda d: {**d, "panels": d.get("panels", []) + [panel]}
                )
                self._load_panels()
                self._clear_form()
                self.toast.show_message("Reaction role panel sent.", "success")
            else:
                self.toast.show_message("Could not send the panel. Is the bot connected?", "error")

        self.send_panel(channel_id, embed_config, mappings, _on_done)

    def _load_panels(self) -> None:
        self.panel_list.clear()
        panels = self.data.reaction_roles.load().get("panels", [])
        for panel in panels:
            embed_config = panel.get("embed_config", {})
            label = embed_config.get("title") or embed_config.get("description") or "(untitled panel)"
            preview = label[:40] + ("..." if len(label) > 40 else "")
            item = QListWidgetItem(f"[{panel['id']}] {preview} ({len(panel.get('mappings', []))} mappings)")
            item.setData(Qt.ItemDataRole.UserRole, panel)
            self.panel_list.addItem(item)

    def _selected_panel(self) -> dict | None:
        item = self.panel_list.currentItem()
        if not item:
            self.toast.show_message("Select a panel from the list first.", "error")
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _load_panel_into_form(self) -> None:
        panel = self._selected_panel()
        if not panel:
            return
        self._apply_embed_config(panel.get("embed_config", {}))
        self.toast.show_message("Loaded panel into the form. Edit fields, then click Modify Existing Message.", "info")

    def _delete_panel(self) -> None:
        panel = self._selected_panel()
        if not panel:
            return

        def _on_done(success: bool):
            if success:
                self.data.reaction_roles.update(
                    lambda d: {**d, "panels": [p for p in d.get("panels", []) if p["id"] != panel["id"]]}
                )
                self._load_panels()
                self.toast.show_message("Panel deleted.", "success")
            else:
                self.toast.show_message("Could not delete the panel on Discord.", "error")

        self.delete_panel_cb(panel, _on_done)

    def _modify_panel(self) -> None:
        panel = self._selected_panel()
        if not panel:
            return
        embed_config = self._gather_embed_config()
        if not any(embed_config.values()):
            self.toast.show_message("Fill in at least one embed field above, then click Modify.", "error")
            return

        def _on_done(success: bool):
            if success:
                self.data.reaction_roles.update(
                    lambda d: {
                        **d,
                        "panels": [
                            {**p, "embed_config": embed_config} if p["id"] == panel["id"] else p
                            for p in d.get("panels", [])
                        ],
                    }
                )
                self._load_panels()
                self.toast.show_message("Panel updated.", "success")
            else:
                self.toast.show_message("Could not update the panel on Discord.", "error")

        self.edit_panel_cb(panel, embed_config, _on_done)

    def _clear_form(self) -> None:
        self.title_input.clear()
        self.description_input.clear()
        self.color_input.clear()
        self.author_name_input.clear()
        self.author_icon_input.clear()
        self.thumbnail_input.clear()
        self.image_input.clear()
        self.footer_input.clear()
        self.mapping_list.clear()
        self._pending_mappings.clear()
