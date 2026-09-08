"""
ui/theme.py

Central dark theme definition for SnapShield. Keeping the palette and
stylesheet in one module makes it trivial to re-skin the app or expose
a theme picker later.
"""

# Palette
BG_DARK = "#1e1f26"
BG_PANEL = "#262832"
BG_PANEL_LIGHT = "#2f313d"
BORDER = "#3a3d4a"
ACCENT = "#4d84ff"
ACCENT_HOVER = "#6b9aff"
ACCENT_PRESSED = "#3a6ce0"
TEXT_PRIMARY = "#f2f3f7"
TEXT_SECONDARY = "#9ea2b3"
SUCCESS = "#3ddc84"
DANGER = "#ff5c72"
WARNING = "#ffb84d"

STYLESHEET = f"""
* {{
    font-family: "Segoe UI", "Inter", sans-serif;
    color: {TEXT_PRIMARY};
    outline: none;
}}

QMainWindow, QWidget#centralWidget {{
    background-color: {BG_DARK};
}}

QWidget#sidebar {{
    background-color: {BG_PANEL};
    border-right: 1px solid {BORDER};
}}

QLabel#appTitle {{
    font-size: 18px;
    font-weight: 600;
    padding: 20px 16px 4px 16px;
}}

QLabel#appSubtitle {{
    font-size: 11px;
    color: {TEXT_SECONDARY};
    padding: 0px 16px 18px 16px;
}}

QPushButton#navButton {{
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-radius: 8px;
    background-color: transparent;
    font-size: 13px;
    margin: 2px 10px;
}}

QPushButton#navButton:hover {{
    background-color: {BG_PANEL_LIGHT};
}}

QPushButton#navButton:checked {{
    background-color: {ACCENT};
    color: white;
    font-weight: 600;
}}

QLabel#pageTitle {{
    font-size: 22px;
    font-weight: 700;
    padding-bottom: 4px;
}}

QLabel#pageSubtitle {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
    padding-bottom: 14px;
}}

QWidget#card {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}

QLabel#cardTitle {{
    font-size: 13px;
    color: {TEXT_SECONDARY};
}}

QLabel#cardValue {{
    font-size: 24px;
    font-weight: 700;
}}

QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {{
    background-color: {BG_PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 13px;
    selection-background-color: {ACCENT};
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 1px solid {ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {BG_PANEL_LIGHT};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
}}

QPushButton {{
    background-color: {BG_PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {BORDER};
}}

QPushButton#primary {{
    background-color: {ACCENT};
    border: none;
    color: white;
    font-weight: 600;
}}

QPushButton#primary:hover {{
    background-color: {ACCENT_HOVER};
}}

QPushButton#primary:pressed {{
    background-color: {ACCENT_PRESSED};
}}

QPushButton#danger {{
    background-color: transparent;
    border: 1px solid {DANGER};
    color: {DANGER};
}}

QPushButton#danger:hover {{
    background-color: {DANGER};
    color: white;
}}

QListWidget, QTreeWidget, QTableWidget {{
    background-color: {BG_PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 4px;
}}

QHeaderView::section {{
    background-color: {BG_PANEL};
    padding: 6px;
    border: none;
    border-bottom: 1px solid {BORDER};
    font-weight: 600;
}}

QCheckBox {{
    spacing: 8px;
    font-size: 13px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {ACCENT};
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
}}

QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 5px;
}}

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

QTabWidget::pane {{
    background-color: {BG_DARK};
    border: 1px solid {BORDER};
    border-radius: 10px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {BG_PANEL};
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 18px;
    margin-right: 4px;
    font-size: 13px;
}}

QTabBar::tab:selected {{
    background-color: {ACCENT};
    color: white;
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    background-color: {BG_PANEL_LIGHT};
    color: {TEXT_PRIMARY};
}}

QLabel#statusOnline {{
    color: {SUCCESS};
    font-weight: 600;
}}

QLabel#statusOffline {{
    color: {DANGER};
    font-weight: 600;
}}

QFrame#hline {{
    background-color: {BORDER};
    max-height: 1px;
    min-height: 1px;
}}
"""
