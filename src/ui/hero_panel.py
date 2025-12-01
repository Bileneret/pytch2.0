import os
import sys
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


def get_project_root():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class HeroPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- ЖОРСТКА ФІКСАЦІЯ РОЗМІРІВ ---
        self.setFixedSize(200, 300)

        self.setStyleSheet("""
            QFrame {
                background-color: #2c3e50; 
                border-radius: 10px; 
                border: 2px solid #2ecc71; 
            }
            QLabel { color: white; border: none; background: transparent; }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)  # Притискаємо контент до верху
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        # 1. Заголовок
        lbl_title = QLabel("HERO")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 10px;")
        layout.addWidget(lbl_title)

        # 2. Аватар
        self.lbl_avatar = QLabel("🧙‍♂️")
        self.lbl_avatar.setFixedSize(100, 100)
        self.lbl_avatar.setAlignment(Qt.AlignCenter)
        self.lbl_avatar.setStyleSheet("font-size: 60px;")
        layout.addWidget(self.lbl_avatar, 0, Qt.AlignHCenter)

        # 3. Нікнейм
        self.lbl_nickname = QLabel("Hero")
        self.lbl_nickname.setAlignment(Qt.AlignCenter)
        self.lbl_nickname.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl_nickname)

        # 4. Інфо
        self.lbl_class_level = QLabel("Lvl 1 | Class")
        self.lbl_class_level.setAlignment(Qt.AlignCenter)
        self.lbl_class_level.setStyleSheet("font-weight: bold; font-size: 11px; color: #bdc3c7;")
        layout.addWidget(self.lbl_class_level)

        # 5. Валюта та Стрік
        stats_line = QHBoxLayout()
        self.lbl_gold = QLabel("💰 0")
        self.lbl_gold.setStyleSheet("font-weight: bold; color: #f1c40f;")
        self.lbl_streak = QLabel("🔥 0")
        self.lbl_streak.setStyleSheet("font-weight: bold; color: #e67e22;")
        stats_line.addWidget(self.lbl_gold)
        stats_line.addStretch()
        stats_line.addWidget(self.lbl_streak)
        layout.addLayout(stats_line)

        # 6. HP Bar
        self.hp_bar = QProgressBar()
        self.hp_bar.setFixedHeight(15)
        self.hp_bar.setTextVisible(True)
        self.hp_bar.setAlignment(Qt.AlignCenter)
        self.hp_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #7f8c8d; border-radius: 5px; background-color: #34495e; text-align: center; color: white; font-weight: bold; font-size: 10px; }
            QProgressBar::chunk { background-color: #e74c3c; border-radius: 4px; }
        """)
        layout.addWidget(self.hp_bar)

        # 7. XP Bar
        self.xp_bar = QProgressBar()
        self.xp_bar.setFixedHeight(15)
        self.xp_bar.setTextVisible(True)
        self.xp_bar.setAlignment(Qt.AlignCenter)
        self.xp_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #7f8c8d; border-radius: 5px; background-color: #34495e; text-align: center; color: white; font-size: 10px; }
            QProgressBar::chunk { background-color: #f1c40f; border-radius: 4px; }
        """)
        layout.addWidget(self.xp_bar)

        layout.addStretch()

    def update_data(self, hero):
        self.lbl_avatar.setText("🧙‍♂️")
        self.lbl_avatar.setStyleSheet("font-size: 60px; background: transparent;")
        if hero.appearance and "assets" in hero.appearance:
            base_path = get_project_root()
            full_path = os.path.join(base_path, hero.appearance)
            if os.path.exists(full_path):
                pixmap = QPixmap(full_path)
                pixmap = pixmap.scaled(self.lbl_avatar.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_avatar.setPixmap(pixmap)
                self.lbl_avatar.setText("")

        self.lbl_nickname.setText(hero.nickname)
        self.lbl_class_level.setText(f"Lvl {hero.level} | {hero.hero_class.value}")
        self.hp_bar.setMaximum(hero.max_hp)
        self.hp_bar.setValue(hero.hp)
        self.hp_bar.setFormat(f"{hero.hp}/{hero.max_hp}")
        self.xp_bar.setMaximum(hero.xp_to_next_level)
        self.xp_bar.setValue(hero.current_xp)
        self.xp_bar.setFormat(f"{hero.current_xp}/{hero.xp_to_next_level} XP")
        self.lbl_gold.setText(f"💰 {hero.gold}")
        self.lbl_streak.setText(f"🔥 {hero.streak_days}")