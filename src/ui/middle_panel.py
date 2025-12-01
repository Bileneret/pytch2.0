from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSizePolicy, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTime


class MiddlePanel(QFrame):
    # Сигнали для кнопок
    stats_clicked = pyqtSignal()
    skills_clicked = pyqtSignal()
    inventory_clicked = pyqtSignal()
    shop_clicked = pyqtSignal()

    logout_clicked = pyqtSignal()
    debug_time_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- ЖОРСТКА ФІКСАЦІЯ ВИСОТИ ---
        self.setFixedHeight(300)
        # Ширина може змінюватись
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #2c3e50; 
                border-radius: 10px; 
                border: 2px solid #3498db; 
            }
            QLabel { color: white; border: none; background: transparent; }
        """)

        # Головний вертикальний леаут
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(10, 15, 10, 15)
        main_layout.setSpacing(20)

        # --- 1. ВЕРХ: Годинник + Утиліти (По центру) ---
        top_bar = QHBoxLayout()
        top_bar.setAlignment(Qt.AlignCenter)

        # Годинник
        self.lbl_clock = QLabel("00:00:00")
        self.lbl_clock.setStyleSheet("font-size: 16px; font-family: monospace; font-weight: bold; color: #ecf0f1;")

        # Кнопка Debug (+)
        self.btn_debug = QPushButton("+")
        self.btn_debug.setFixedSize(20, 20)
        self.btn_debug.setToolTip("Debug: +2 години")
        self.btn_debug.setCursor(Qt.PointingHandCursor)
        self.btn_debug.setStyleSheet("""
            QPushButton { background-color: #2980b9; color: white; border: none; font-weight: bold; border-radius: 10px; }
            QPushButton:hover { background-color: #3498db; }
        """)
        self.btn_debug.clicked.connect(self.debug_time_clicked.emit)
        self.btn_debug.hide()

        # Кнопка Виходу
        self.btn_logout = QPushButton("🚪")
        self.btn_logout.setToolTip("Вийти з акаунту")
        self.btn_logout.setFixedSize(30, 30)
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.setStyleSheet("""
            QPushButton { background-color: #c0392b; color: white; border: none; border-radius: 5px; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background-color: #e74c3c; }
        """)
        self.btn_logout.clicked.connect(self.logout_clicked.emit)

        top_bar.addWidget(self.lbl_clock)
        top_bar.addWidget(self.btn_debug)
        top_bar.addSpacing(10)
        top_bar.addWidget(self.btn_logout)

        main_layout.addLayout(top_bar)

        # --- 2. ЦЕНТР: Матриця кнопок 2x2 ---
        grid = QGridLayout()
        grid.setSpacing(15)
        # Рівномірний розподіл
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # --- [0, 0] Магазин (Верхній Лівий) ---
        self.btn_shop = self.create_menu_button("Магазин", "#f1c40f", "#f39c12", text_color="#2c3e50")
        self.btn_shop.clicked.connect(self.shop_clicked.emit)
        grid.addWidget(self.btn_shop, 0, 0)

        # --- [0, 1] Інвентар (Верхній Правий) ---
        self.btn_inventory = self.create_menu_button("Інвентар", "#e67e22", "#d35400")
        self.btn_inventory.clicked.connect(self.inventory_clicked.emit)
        grid.addWidget(self.btn_inventory, 0, 1)

        # --- [1, 0] Характеристики + Інфо (Нижній Лівий) ---
        stats_container = QWidget()
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(5)

        self.btn_stats = self.create_menu_button("Характеристики", "#3498db", "#2980b9")
        self.btn_stats.clicked.connect(self.stats_clicked.emit)

        self.lbl_stats_summary = QLabel("⚔️0 🧠0 🎯0 🧡0 🛡️0")
        self.lbl_stats_summary.setAlignment(Qt.AlignCenter)
        self.lbl_stats_summary.setStyleSheet("font-size: 10px; color: #bdc3c7; font-weight: bold;")

        stats_layout.addWidget(self.btn_stats)
        stats_layout.addWidget(self.lbl_stats_summary)

        grid.addWidget(stats_container, 1, 0)

        # --- [1, 1] Навички + Інфо (Нижній Правий) ---
        skills_container = QWidget()
        skills_layout = QVBoxLayout(skills_container)
        skills_layout.setContentsMargins(0, 0, 0, 0)
        skills_layout.setSpacing(5)

        self.btn_skills = self.create_menu_button("Навички", "#9b59b6", "#8e44ad")
        self.btn_skills.clicked.connect(self.skills_clicked.emit)

        # Лейбл для навичок (поки заглушка, або можна виводити к-сть вивчених)
        self.lbl_skills_summary = QLabel("---")
        self.lbl_skills_summary.setAlignment(Qt.AlignCenter)
        self.lbl_skills_summary.setStyleSheet("font-size: 10px; color: #bdc3c7; font-weight: bold;")

        skills_layout.addWidget(self.btn_skills)
        skills_layout.addWidget(self.lbl_skills_summary)

        grid.addWidget(skills_container, 1, 1)

        main_layout.addLayout(grid)

        # Пружина знизу, щоб все було компактно зверху-по центру
        main_layout.addStretch()

    def create_menu_button(self, text, color, hover_color, text_color="white"):
        """Створює стильну кнопку меню."""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(40)  # Фіксована висота кнопки
        # btn.setFixedWidth(140) # Ширину прибираємо, хай тягнеться по грідy
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        btn.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {color}; 
                color: {text_color}; 
                border: none; 
                border-radius: 5px; 
                font-weight: bold; 
                font-size: 12px; 
            }}
            QPushButton:hover {{ background-color: {hover_color}; }}
        """)
        return btn

    def update_data(self, hero, simulated_time):
        """Оновлює дані на панелі."""
        self.lbl_stats_summary.setText(
            f"⚔️{hero.str_stat} 🧠{hero.int_stat} 🎯{hero.dex_stat} 🧡{hero.vit_stat} 🛡️{hero.def_stat}")
        self.lbl_clock.setText(simulated_time.strftime("%H:%M:%S"))
        if hero.nickname.lower() == "tester":
            self.btn_debug.show()
        else:
            self.btn_debug.hide()