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

        # --- ЖОРСТКА ФІКСАЦІЯ РОЗМІРІВ (Як у HeroPanel) ---
        self.setFixedSize(200, 350)

        # Базовий стиль, рамка буде змінюватись динамічно
        self.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 2px solid #c0392b;
                border-radius: 10px;
            }
            QLabel { color: white; border: none; background: transparent; }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        # Відступи як у HeroPanel
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        # 1. Заголовок
        lbl_title = QLabel("ENEMY STATUS")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 10px;")
        layout.addWidget(lbl_title)

        # 2. Аватар
        self.lbl_icon = QLabel("👹")
        self.lbl_icon.setFixedSize(150, 150)
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setStyleSheet("font-size: 60px;")
        layout.addWidget(self.lbl_icon, 0, Qt.AlignHCenter)

        # 3. Ім'я
        self.lbl_name = QLabel("Name")
        self.lbl_name.setAlignment(Qt.AlignCenter)
        self.lbl_name.setWordWrap(True)
        # Стиль як у нікнейма героя
        self.lbl_name.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl_name)

        # 4. Інфо (Рівень і Рідкість)
        self.lbl_info = QLabel("Lvl ? | Rarity")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        # Стиль як у класа героя
        self.lbl_info.setStyleSheet("font-weight: bold; font-size: 11px; color: #bdc3c7;")
        layout.addWidget(self.lbl_info)

        # 5. Статистика (Урон) - оформлено як рядок валюти героя
        stats_line = QHBoxLayout()
        stats_line.addStretch()
        self.lbl_stats = QLabel("⚔️ 0")
        self.lbl_stats.setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 14px;")
        stats_line.addWidget(self.lbl_stats)
        stats_line.addStretch()
        layout.addLayout(stats_line)

        # 6. HP Bar - Стиль як у HeroPanel
        self.hp_bar = QProgressBar()
        self.hp_bar.setFixedHeight(15)
        self.hp_bar.setTextVisible(True)
        self.hp_bar.setAlignment(Qt.AlignCenter)
        self.hp_bar.setStyleSheet("""
            QProgressBar { 
                border: 1px solid #7f8c8d; 
                border-radius: 5px; 
                background-color: #34495e; 
                text-align: center; 
                color: white; 
                font-weight: bold; 
                font-size: 10px; 
            }
            QProgressBar::chunk { 
                background-color: #c0392b; 
                border-radius: 4px; 
            }
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

        # --- ВІДОБРАЖЕННЯ КАРТИНКИ ---
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
        color = "#c0392b"  # Red default
        if enemy.rarity.name == "EASY":
            color = "#2ecc71"
        elif enemy.rarity.name == "MEDIUM":
            color = "#f39c12"
        elif enemy.rarity.name == "HARD":
            color = "#c0392b"

        # Оновлюємо стиль рамки, зберігаючи загальний стиль фону
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2c3e50;
                border: 2px solid {color};
                border-radius: 10px;
            }}
            QLabel {{ color: white; border: none; background: transparent; }}
        """)