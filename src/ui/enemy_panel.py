import os
import sys
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from src.models import Enemy, EnemyRarity


def get_project_root():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class EnemyWidget(QFrame):
    def __init__(self):
        super().__init__()

        # --- ЖОРСТКА ФІКСАЦІЯ РОЗМІРІВ ---
        self.setFixedSize(200, 350)
        # Фон і загальні стилі тепер беруться з style.qss
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        lbl_title = QLabel("ENEMY STATUS")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 10px;")
        layout.addWidget(lbl_title)

        self.lbl_icon = QLabel("👹")
        self.lbl_icon.setFixedSize(150, 150)
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setStyleSheet("font-size: 60px;")
        layout.addWidget(self.lbl_icon, 0, Qt.AlignHCenter)

        self.lbl_name = QLabel("Name")
        self.lbl_name.setAlignment(Qt.AlignCenter)
        self.lbl_name.setWordWrap(True)
        # Колір залишаємо білим/світлим через клас, або форсуємо, якщо треба
        self.lbl_name.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl_name)

        self.lbl_info = QLabel("Lvl ? | Rarity")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        self.lbl_info.setStyleSheet("font-weight: bold; font-size: 11px; color: #bdc3c7;")
        layout.addWidget(self.lbl_info)

        stats_line = QHBoxLayout()
        stats_line.addStretch()
        self.lbl_stats = QLabel("⚔️ 0")
        self.lbl_stats.setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 14px;")
        stats_line.addWidget(self.lbl_stats)
        stats_line.addStretch()
        layout.addLayout(stats_line)

        self.hp_bar = QProgressBar()
        self.hp_bar.setFixedHeight(20)
        self.hp_bar.setTextVisible(True)
        self.hp_bar.setAlignment(Qt.AlignCenter)
        # Залишаємо специфічний колір чанка (червоний для ворога)
        self.hp_bar.setStyleSheet("""
            QProgressBar::chunk { background-color: #c0392b; border-radius: 3px; }
        """)
        layout.addWidget(self.hp_bar)

        layout.addStretch()

    def update_enemy(self, enemy):
        self.lbl_name.setText(enemy.name)
        self.lbl_info.setText(f"Lvl {enemy.level} | {enemy.rarity.value}")
        self.hp_bar.setMaximum(enemy.max_hp)
        self.hp_bar.setValue(enemy.current_hp)
        self.hp_bar.setFormat(f"{enemy.current_hp}/{enemy.max_hp}")
        self.lbl_stats.setText(f"⚔️ {enemy.damage}")

        base_path = get_project_root()
        img_path = os.path.join(base_path, "assets", "enemies", enemy.image_path)

        if enemy.image_path and os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_icon.setPixmap(pix)
            self.lbl_icon.setText("")
        else:
            self.lbl_icon.setPixmap(QPixmap())
            self.lbl_icon.setText("👹")

        # Зміна кольору рамки від рідкості
        color = "#c0392b"
        if enemy.rarity.name == "EASY":
            color = "#2ecc71"
        elif enemy.rarity.name == "MEDIUM":
            color = "#f39c12"
        elif enemy.rarity.name == "HARD":
            color = "#c0392b"

        # Встановлюємо ТІЛЬКИ рамку, фон прозорий (береться з батька/теми)
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {color};
                border-radius: 10px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)