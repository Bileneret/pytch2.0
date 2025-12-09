from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QScrollArea, QMessageBox
from PyQt5.QtCore import Qt


class BaseTab(QWidget):
    """Базовый класс для вкладок, содержащий общие методы UI."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 10, 0, 0)
        self.list_layout = None  # Сюда будем добавлять карточки

    def create_scroll_area(self):
        """Создает область прокрутки для списка карточек."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")

        self.list_layout = QVBoxLayout(container)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.list_layout.setSpacing(12)
        self.list_layout.setContentsMargins(5, 10, 5, 10)

        scroll.setWidget(container)
        self.layout.addWidget(scroll)

    def create_tab_controls(self, btn_text, btn_command, refresh_command,
                            sort_items=None, on_sort_change=None,
                            add_cleanup=False, cleanup_command=None,
                            add_ai_btn=False, ai_command=None,
                            add_search=False, search_command=None):  # search_command
        """Универсальный метод создания панели управления вкладкой."""
        box = QHBoxLayout()
        box.setContentsMargins(5, 0, 5, 0)
        box.setSpacing(10)

        # --- РАЗМЕРЫ ---
        BTN_ADD_HEIGHT = 36
        BTN_ADD_WIDTH = 140
        BTN_AI_WIDTH = 100
        BTN_REFRESH_HEIGHT = 36
        BTN_REFRESH_WIDTH = 50
        COMBO_SORT_HEIGHT = 36
        COMBO_SORT_WIDTH = 250
        BTN_SEARCH_WIDTH = 100
        BTN_CLEANUP_HEIGHT = 36
        BTN_CLEANUP_WIDTH = 160
        # --------------

        # 1. Кнопка "Додати"
        btn_add = QPushButton(btn_text)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setFixedSize(BTN_ADD_WIDTH, BTN_ADD_HEIGHT)
        btn_add.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; 
                color: white; 
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            } 
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_add.clicked.connect(btn_command)
        box.addWidget(btn_add)

        # 1.5. Кнопка "ШІ ціль"
        if add_ai_btn and ai_command:
            btn_ai = QPushButton("🤖 ШІ ціль")
            btn_ai.setCursor(Qt.PointingHandCursor)
            btn_ai.setFixedSize(BTN_AI_WIDTH, BTN_ADD_HEIGHT)
            btn_ai.setStyleSheet("""
                QPushButton { 
                    background-color: #3498db; 
                    color: white; 
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 13px;
                } 
                QPushButton:hover { background-color: #2980b9; }
            """)
            btn_ai.clicked.connect(ai_command)
            box.addWidget(btn_ai)

        # 2. Кнопка "Оновити"
        btn_refresh = QPushButton("🔄")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setFixedSize(BTN_REFRESH_WIDTH, BTN_REFRESH_HEIGHT)
        btn_refresh.setStyleSheet("""
            QPushButton { 
                background-color: #95a5a6; 
                color: white; 
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            } 
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        btn_refresh.clicked.connect(refresh_command)
        box.addWidget(btn_refresh)

        # 3. Сортировка
        sort_combo = None
        if sort_items:
            sort_combo = QComboBox()
            sort_combo.addItems(sort_items)
            sort_combo.setFixedSize(COMBO_SORT_WIDTH, COMBO_SORT_HEIGHT)

            if on_sort_change:
                sort_combo.currentIndexChanged.connect(on_sort_change)
            box.addWidget(sort_combo)

        # 3.5. Кнопка "Пошук"
        if add_search:
            btn_search = QPushButton("🔍 Пошук")
            btn_search.setCursor(Qt.PointingHandCursor)
            btn_search.setFixedSize(BTN_SEARCH_WIDTH, BTN_ADD_HEIGHT)
            btn_search.setStyleSheet("""
                QPushButton { 
                    background-color: #9b59b6; 
                    color: white; 
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 13px;
                } 
                QPushButton:hover { background-color: #8e44ad; }
            """)
            if search_command:
                btn_search.clicked.connect(search_command)
            else:
                btn_search.clicked.connect(
                    lambda: QMessageBox.information(self, "Інфо", "Функціонал пошуку у розробці 🛠️"))
            box.addWidget(btn_search)

        # 4. Кнопка "Автовидалення"
        if add_cleanup and cleanup_command:
            btn_cleanup = QPushButton("🗑️ Автовидалення")
            btn_cleanup.setCursor(Qt.PointingHandCursor)
            btn_cleanup.setFixedSize(BTN_CLEANUP_WIDTH, BTN_CLEANUP_HEIGHT)
            btn_cleanup.setStyleSheet("""
                QPushButton { 
                    background-color: #c0392b; 
                    color: white; 
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 13px;
                } 
                QPushButton:hover { background-color: #e74c3c; }
            """)
            btn_cleanup.clicked.connect(cleanup_command)
            box.addWidget(btn_cleanup)

        box.addStretch()
        self.layout.addLayout(box)

        return sort_combo