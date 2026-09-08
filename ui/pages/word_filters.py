"""
ui/pages/word_filters.py

Word Filters page: two entirely separate lists.

  * Strike Words  -- trigger a strike (see strike_system.py) and have
                     the offending message removed.
  * Banned Words  -- trigger instant Ban/Kick with a custom message,
                     no strike involved.

Both sections support Add / Remove / Import (from a .txt file, one
word per line) / Export.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from storage.json_store import DataManager
from ui.widgets import Card, Toast, page_header


class _WordListSection(QWidget):
    """Reusable Add/Remove/Import/Export word-list widget."""

    def __init__(self, title: str, load_words, save_words, toast: Toast, extra_controls: QWidget | None = None):
        super().__init__()
        self.load_words = load_words
        self.save_words = save_words
        self.toast = toast

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        card = Card()
        card.add(QLabel(title))

        input_row = QHBoxLayout()
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Enter a word or phrase")
        self.word_input.returnPressed.connect(self._add_word)
        add_btn = QPushButton("Add Word")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self._add_word)
        input_row.addWidget(self.word_input)
        input_row.addWidget(add_btn)
        row_widget = QWidget()
        row_widget.setLayout(input_row)
        card.add(row_widget)

        self.list_widget = QListWidget()
        card.add(self.list_widget)

        btn_row = QHBoxLayout()
        remove_btn = QPushButton("Remove Word")
        remove_btn.setObjectName("danger")
        remove_btn.clicked.connect(self._remove_word)
        import_btn = QPushButton("Import List")
        import_btn.clicked.connect(self._import_list)
        export_btn = QPushButton("Export List")
        export_btn.clicked.connect(self._export_list)
        btn_row.addWidget(remove_btn)
        btn_row.addWidget(import_btn)
        btn_row.addWidget(export_btn)
        btn_row.addStretch(1)
        btn_row_widget = QWidget()
        btn_row_widget.setLayout(btn_row)
        card.add(btn_row_widget)

        if extra_controls is not None:
            card.add(extra_controls)

        layout.addWidget(card)
        self.refresh()

    def refresh(self) -> None:
        self.list_widget.clear()
        for word in self.load_words():
            self.list_widget.addItem(QListWidgetItem(word))

    def _add_word(self) -> None:
        word = self.word_input.text().strip()
        if not word:
            return
        words = self.load_words()
        if word.lower() in [w.lower() for w in words]:
            self.toast.show_message(f'"{word}" is already in the list.', "error")
            return
        words.append(word)
        self.save_words(words)
        self.word_input.clear()
        self.refresh()
        self.toast.show_message(f'Added "{word}".', "success")

    def _remove_word(self) -> None:
        item = self.list_widget.currentItem()
        if not item:
            self.toast.show_message("Select a word to remove.", "error")
            return
        word = item.text()
        words = [w for w in self.load_words() if w != word]
        self.save_words(words)
        self.refresh()
        self.toast.show_message(f'Removed "{word}".', "success")

    def _import_list(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import Word List", "", "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                new_words = [line.strip() for line in fh if line.strip()]
        except OSError as exc:
            self.toast.show_message(f"Could not read file: {exc}", "error")
            return

        existing = self.load_words()
        existing_lower = {w.lower() for w in existing}
        added = 0
        for w in new_words:
            if w.lower() not in existing_lower:
                existing.append(w)
                existing_lower.add(w.lower())
                added += 1
        self.save_words(existing)
        self.refresh()
        self.toast.show_message(f"Imported {added} new word(s).", "success")

    def _export_list(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export Word List", "words.txt", "Text Files (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("\n".join(self.load_words()))
        except OSError as exc:
            self.toast.show_message(f"Could not save file: {exc}", "error")
            return
        self.toast.show_message("List exported.", "success")


class WordFiltersPage(QWidget):
    def __init__(self, data: DataManager):
        super().__init__()
        self.data = data

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        layout.addWidget(page_header("Word Filters", "Strike Words add a strike; Banned Words punish instantly"))

        self.toast = Toast()

        tabs = QTabWidget()

        # --- Strike Words tab -------------------------------------------------
        strike_section = _WordListSection(
            "Strike Words — detected messages are removed and a strike is added",
            load_words=lambda: list(self.data.strike_words.load().get("words", [])),
            save_words=lambda words: self.data.strike_words.update(lambda d: {**d, "words": words}),
            toast=self.toast,
        )
        tabs.addTab(strike_section, "Strike Words")

        # --- Banned Words tab ---------------------------------------------------
        banned_cfg = self.data.banned_words.load()

        extra = QWidget()
        extra_layout = QVBoxLayout(extra)
        extra_layout.setContentsMargins(0, 8, 0, 0)
        extra_layout.setSpacing(8)

        extra_layout.addWidget(QLabel("Custom Action"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Kick", "Ban"])
        self.action_combo.setCurrentText(banned_cfg.get("action", "Kick"))
        self.action_combo.currentTextChanged.connect(self._save_banned_action)
        extra_layout.addWidget(self.action_combo)

        extra_layout.addWidget(QLabel("Custom Message"))
        self.banned_message_input = QTextEdit()
        self.banned_message_input.setFixedHeight(60)
        self.banned_message_input.setPlainText(banned_cfg.get("message", ""))
        self.banned_message_input.textChanged.connect(self._save_banned_message)
        extra_layout.addWidget(self.banned_message_input)

        banned_section = _WordListSection(
            "Banned Words — detected messages trigger instant Ban/Kick, no strike",
            load_words=lambda: list(self.data.banned_words.load().get("words", [])),
            save_words=lambda words: self.data.banned_words.update(lambda d: {**d, "words": words}),
            toast=self.toast,
            extra_controls=extra,
        )
        tabs.addTab(banned_section, "Banned Words")

        layout.addWidget(tabs)
        layout.addWidget(self.toast)

    def _save_banned_action(self, action: str) -> None:
        self.data.banned_words.update(lambda d: {**d, "action": action})

    def _save_banned_message(self) -> None:
        text = self.banned_message_input.toPlainText()
        self.data.banned_words.update(lambda d: {**d, "message": text})
