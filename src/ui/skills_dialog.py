import os
import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap


def get_project_root():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class SkillsDialog(QDialog):
    def __init__(self, parent, service):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Навички Класу 📜")
        self.resize(500, 600)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout(self)

        hero = self.service.get_hero()
        # Тепер цей виклик спрацює, бо ми додали SkillLogic до GoalService
        skills = self.service.get_skills()

        lbl_header = QLabel(f"Навички: {hero.hero_class.value}")
        lbl_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #8e44ad; margin-bottom: 10px;")
        lbl_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        container = QWidget()
        vbox = QVBoxLayout(container)

        class_map = {"Воїн": "knight", "Лучник": "archer", "Маг": "mage", "Розбійник": "rogue"}
        cls_name = hero.hero_class.value if hasattr(hero.hero_class, 'value') else "Воїн"
        cls_folder = class_map.get(cls_name, "knight")
        base_path = get_project_root()

        for s in skills:
            frame = QFrame()
            frame.setStyleSheet("background-color: #f0f2f5; border-radius: 8px; border: 1px solid #bdc3c7;")
            row = QHBoxLayout(frame)

            lbl_icon = QLabel()
            lbl_icon.setFixedSize(64, 64)
            lbl_icon.setAlignment(Qt.AlignCenter)
            icon_path = os.path.join(base_path, "assets", "skills", cls_folder, f"skill{s['id']}.png")

            if os.path.exists(icon_path):
                pix = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl_icon.setPixmap(pix)
            else:
                lbl_icon.setText("🔮")

            text_layout = QVBoxLayout()
            name_lbl = QLabel(f"{s['name']} (Lvl {s['level_req']})")
            name_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")

            desc_lbl = QLabel(s['desc'])
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("color: #2c3e50;")

            cost_lbl = QLabel(f"Мана: {s['mana_cost']}")
            cost_lbl.setStyleSheet("color: #3498db; font-weight: bold; font-size: 10px;")

            text_layout.addWidget(name_lbl)
            text_layout.addWidget(desc_lbl)
            text_layout.addWidget(cost_lbl)

            status_lbl = QLabel()
            if hero.level >= s['level_req']:
                status_lbl.setText("✅")
                status_lbl.setStyleSheet("color: green; font-size: 20px;")
            else:
                status_lbl.setText("🔒")
                status_lbl.setStyleSheet("color: gray; font-size: 20px;")

            row.addWidget(lbl_icon)
            row.addLayout(text_layout)
            row.addWidget(status_lbl)

            vbox.addWidget(frame)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        btn_close = QPushButton("Закрити")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)