import os
import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSizePolicy, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTime, QSize
from PyQt5.QtGui import QIcon


def get_project_root():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class MiddlePanel(QFrame):
    stats_clicked = pyqtSignal()
    skills_clicked = pyqtSignal()
    inventory_clicked = pyqtSignal()
    shop_clicked = pyqtSignal()
    skill_used_signal = pyqtSignal(int)  # Сигнал: використано навичку (id)

    logout_clicked = pyqtSignal()
    debug_time_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QFrame { background-color: #2c3e50; border-radius: 10px; border: 2px solid #3498db; }
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
        self.btn_debug = QPushButton("+");
        self.btn_debug.setFixedSize(20, 20);
        self.btn_debug.clicked.connect(self.debug_time_clicked.emit);
        self.btn_debug.hide()
        self.btn_logout = QPushButton("🚪");
        self.btn_logout.setFixedSize(30, 30);
        self.btn_logout.clicked.connect(self.logout_clicked.emit)
        top_bar.addWidget(self.lbl_clock);
        top_bar.addWidget(self.btn_debug);
        top_bar.addSpacing(10);
        top_bar.addWidget(self.btn_logout)
        main_layout.addLayout(top_bar)

        # --- 2. МЕНЮ КНОПОК (2x2) ---
        grid = QGridLayout()
        grid.setSpacing(15)
        self.btn_shop = self.create_menu_button("Магазин", "#f1c40f", "#f39c12", "#2c3e50")
        self.btn_shop.clicked.connect(self.shop_clicked.emit)
        grid.addWidget(self.btn_shop, 0, 0)
        self.btn_inventory = self.create_menu_button("Інвентар", "#e67e22", "#d35400")
        self.btn_inventory.clicked.connect(self.inventory_clicked.emit)
        grid.addWidget(self.btn_inventory, 0, 1)

        # Характеристики
        stats_cont = QWidget();
        stats_l = QVBoxLayout(stats_cont);
        stats_l.setContentsMargins(0, 0, 0, 0);
        stats_l.setSpacing(5)
        self.btn_stats = self.create_menu_button("Характеристики", "#3498db", "#2980b9")
        self.btn_stats.clicked.connect(self.stats_clicked.emit)
        self.lbl_stats_summary = QLabel("Stats...");
        self.lbl_stats_summary.setAlignment(Qt.AlignCenter);
        self.lbl_stats_summary.setStyleSheet("font-size: 9px; color: #bdc3c7;")
        stats_l.addWidget(self.btn_stats);
        stats_l.addWidget(self.lbl_stats_summary)
        grid.addWidget(stats_cont, 1, 0)

        # Навички
        skills_cont = QWidget();
        skills_l = QVBoxLayout(skills_cont);
        skills_l.setContentsMargins(0, 0, 0, 0);
        skills_l.setSpacing(5)
        self.btn_skills = self.create_menu_button("Навички", "#9b59b6", "#8e44ad")
        self.btn_skills.clicked.connect(self.skills_clicked.emit)
        skills_l.addWidget(self.btn_skills)
        # Місце для швидких слотів (будуть нижче в окремому блоці, тут просто кнопка)
        grid.addWidget(skills_cont, 1, 1)

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
            # Прив'язка ID (1..5)
            btn.clicked.connect(lambda checked, sid=i + 1: self.skill_used_signal.emit(sid))
            self.skill_buttons.append(btn)
            self.skills_box.addWidget(btn)

        main_layout.addLayout(self.skills_box)
        main_layout.addStretch()

    def create_menu_button(self, text, color, hover_color, text_color="white"):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(40)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {color}; color: {text_color}; border: none; border-radius: 5px; font-weight: bold; font-size: 12px; }} QPushButton:hover {{ background-color: {hover_color}; }}")
        return btn

    def update_data(self, hero, simulated_time):
        self.lbl_stats_summary.setText(
            f"⚔️{hero.str_stat} 🧠{hero.int_stat} 🎯{hero.dex_stat} ❤️{hero.vit_stat} 🛡️{hero.def_stat}")
        self.lbl_clock.setText(simulated_time.strftime("%H:%M:%S"))
        if hero.nickname.lower() == "tester":
            self.btn_debug.show()
        else:
            self.btn_debug.hide()

        # Оновлення іконок навичок
        class_map = {
            "Воїн": "knight", "Лучник": "archer", "Маг": "mage", "Розбійник": "rogue"
        }
        cls_folder = class_map.get(hero.hero_class.value, "knight")
        base_path = get_project_root()

        skill_levels = [5, 10, 15, 20, 25]

        for i, btn in enumerate(self.skill_buttons):
            lvl_req = skill_levels[i]

            if hero.level >= lvl_req:
                btn.setEnabled(True)
                # Завантаження іконки
                icon_path = os.path.join(base_path, "assets", "skills", cls_folder, f"skill{i + 1}.png")
                if os.path.exists(icon_path):
                    btn.setIcon(QIcon(icon_path))
                    btn.setIconSize(QSize(32, 32))
                    btn.setToolTip(f"Skill {i + 1} (Lvl {lvl_req})")
                else:
                    btn.setText(f"S{i + 1}")
            else:
                btn.setEnabled(False)
                btn.setIcon(QIcon())
                btn.setText("🔒")
                btn.setToolTip(f"Відкриється на {lvl_req} рівні")