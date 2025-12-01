import os
import sys
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from src.models import Enemy, EnemyRarity


def get_project_root():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class EnemyWidget(QFrame):
    def __init__(self):
        super().__init__()

        # --- ЖОРСТКА ФІКСАЦІЯ РОЗМІРІВ ---
        self.setFixedSize(200, 300)

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
        layout.setAlignment(Qt.AlignTop)  # Притискаємо контент до верху
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        lbl_title = QLabel("ENEMY")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 10px;")
        layout.addWidget(lbl_title)

        self.lbl_icon = QLabel("👹")
        self.lbl_icon.setFixedSize(100, 100)
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setStyleSheet("font-size: 60px;")
        layout.addWidget(self.lbl_icon, 0, Qt.AlignHCenter)

        self.lbl_name = QLabel("Name")
        self.lbl_name.setAlignment(Qt.AlignCenter)
        self.lbl_name.setWordWrap(True)
        self.lbl_name.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl_name)

        self.lbl_info = QLabel("Lvl ?")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        self.lbl_info.setStyleSheet("color: #bdc3c7; font-size: 11px;")
        layout.addWidget(self.lbl_info)

        self.hp_bar = QProgressBar()
        self.hp_bar.setFixedHeight(15)
        self.hp_bar.setTextVisible(True)
        self.hp_bar.setAlignment(Qt.AlignCenter)
        self.hp_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #7f8c8d; border-radius: 5px; background-color: #34495e; text-align: center; color: white; font-weight: bold; font-size: 10px; }
            QProgressBar::chunk { background-color: #c0392b; border-radius: 4px; }
        """)
        layout.addWidget(self.hp_bar)

        self.lbl_stats = QLabel("Dmg: ?")
        self.lbl_stats.setAlignment(Qt.AlignCenter)
        self.lbl_stats.setStyleSheet("color: #f39c12; font-size: 11px;")
        layout.addWidget(self.lbl_stats)

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
            pix = QPixmap(img_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_icon.setPixmap(pix)
            self.lbl_icon.setText("")
        else:
            self.lbl_icon.setPixmap(QPixmap())
            self.lbl_icon.setText("👹")

        color = "#c0392b"
        if enemy.rarity.name == "EASY":
            color = "#2ecc71"
        elif enemy.rarity.name == "MEDIUM":
            color = "#f39c12"
        elif enemy.rarity.name == "HARD":
            color = "#c0392b"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2c3e50;
                border: 2px solid {color};
                border-radius: 10px;
            }}
            QLabel {{ color: white; border: none; background: transparent; }}
        """)