from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSizePolicy, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTime, QSize
from PyQt5.QtGui import QIcon
import os
import sys


def get_project_root():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class MiddlePanel(QFrame):
    stats_clicked = pyqtSignal()
    skills_clicked = pyqtSignal()
    inventory_clicked = pyqtSignal()
    shop_clicked = pyqtSignal()
    skill_used_signal = pyqtSignal(int)

    logout_clicked = pyqtSignal()
    debug_time_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(350)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setup_ui()

    def setup_ui(self):
        # Рамка панелі
        self.setStyleSheet("""
            QFrame { border: 2px solid #3498db; border-radius: 10px; }
            QLabel { color: white; border: none; background: transparent; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(10, 15, 10, 15)
        main_layout.setSpacing(15)

        # --- 1. ВЕРХ: Годинник ---
        top_bar = QHBoxLayout()
        top_bar.setAlignment(Qt.AlignCenter)

        self.lbl_clock = QLabel("00:00:00")
        self.lbl_clock.setStyleSheet("font-size: 16px; font-family: monospace; font-weight: bold; color: #ecf0f1;")

        self.btn_debug = QPushButton("+")
        self.btn_debug.setFixedSize(25, 25)
        self.btn_debug.clicked.connect(self.debug_time_clicked.emit)
        self.btn_debug.hide()

        # Кнопку виходу звідси прибрали

        top_bar.addWidget(self.lbl_clock)
        top_bar.addWidget(self.btn_debug)
        main_layout.addLayout(top_bar)

        # --- 2. МЕНЮ КНОПОК (2x2) ---
        grid = QGridLayout()
        grid.setSpacing(15)

        # Магазин
        self.btn_shop = self.create_menu_button("Магазин", "#f1c40f", "#f39c12", "#2c3e50")
        self.btn_shop.clicked.connect(self.shop_clicked.emit)
        grid.addWidget(self.btn_shop, 0, 0)

        # Інвентар
        self.btn_inventory = self.create_menu_button("Інвентар", "#e67e22", "#d35400")
        self.btn_inventory.clicked.connect(self.inventory_clicked.emit)
        grid.addWidget(self.btn_inventory, 0, 1)

        # Характеристики
        self.btn_stats = self.create_menu_button("Характеристики", "#3498db", "#2980b9")
        self.btn_stats.clicked.connect(self.stats_clicked.emit)
        grid.addWidget(self.btn_stats, 1, 0)

        # Навички
        self.btn_skills = self.create_menu_button("Навички", "#9b59b6", "#8e44ad")
        self.btn_skills.clicked.connect(self.skills_clicked.emit)
        grid.addWidget(self.btn_skills, 1, 1)

        main_layout.addLayout(grid)

        # --- 3. ШВИДКІ СЛОТИ НАВИЧОК ---
        self.skill_slots_label = QLabel("ШВИДКІ НАВИЧКИ")
        self.skill_slots_label.setAlignment(Qt.AlignCenter)
        self.skill_slots_label.setStyleSheet("color: #9b59b6; font-weight: bold; font-size: 10px; margin-top: 10px;")
        main_layout.addWidget(self.skill_slots_label)

        self.skills_box = QHBoxLayout()
        self.skills_box.setAlignment(Qt.AlignCenter)
        self.skills_box.setSpacing(10)

        self.skill_buttons = []
        for i in range(5):
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { background-color: #34495e; border: 1px solid #7f8c8d; border-radius: 5px; }
                QPushButton:hover { border: 1px solid #9b59b6; }
                QPushButton:disabled { background-color: #2c3e50; border: 1px solid #2c3e50; }
            """)
            btn.clicked.connect(lambda checked, sid=i + 1: self.skill_used_signal.emit(sid))
            self.skill_buttons.append(btn)
            self.skills_box.addWidget(btn)

        main_layout.addLayout(self.skills_box)

        # Додаємо розтяжку, щоб кнопка виходу була в самому низу
        main_layout.addStretch()

        # --- 4. КНОПКА ВИХОДУ (Внизу) ---
        self.btn_logout = QPushButton("Вийти з аккаунту")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.setFixedWidth(200)  # Фіксуємо ширину, щоб не була на всю панель
        self.btn_logout.setStyleSheet("""
            QPushButton { 
                background-color: #c0392b; 
                color: white; 
                font-weight: bold; 
                border-radius: 5px; 
                padding: 8px;
                border: 1px solid #e74c3c;
            }
            QPushButton:hover { background-color: #e74c3c; }
        """)
        self.btn_logout.clicked.connect(self.logout_clicked.emit)

        # Додаємо кнопку по центру
        main_layout.addWidget(self.btn_logout, 0, Qt.AlignCenter)

    def create_menu_button(self, text, color, hover_color, text_color="white"):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(50)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {color}; color: {text_color}; border: none; border-radius: 5px; font-weight: bold; font-size: 16px; }} QPushButton:hover {{ background-color: {hover_color}; }}")
        return btn

    def update_data(self, hero, simulated_time):
        self.lbl_clock.setText(simulated_time.strftime("%H:%M:%S"))
        if hero.nickname.lower() == "tester":
            self.btn_debug.show()
        else:
            self.btn_debug.hide()

        class_map = {"Воїн": "knight", "Лучник": "archer", "Маг": "mage", "Розбійник": "rogue"}
        cls_name = hero.hero_class.value if hasattr(hero.hero_class, 'value') else "Воїн"
        cls_folder = class_map.get(cls_name, "knight")

        base_path = get_project_root()
        skill_levels = [5, 10, 15, 20, 25]

        for i, btn in enumerate(self.skill_buttons):
            lvl_req = skill_levels[i]
            if hero.level >= lvl_req:
                btn.setEnabled(True)
                icon_path = os.path.join(base_path, "assets", "skills", cls_folder, f"skill{i + 1}.png")
                if os.path.exists(icon_path):
                    btn.setIcon(QIcon(icon_path))
                    btn.setIconSize(QSize(32, 32))
                    btn.setText("")
                else:
                    btn.setText(f"S{i + 1}")
            else:
                btn.setEnabled(False)
                btn.setIcon(QIcon())
                btn.setText("🔒")