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
        self.resize(500, 850)
        # Видалено світлий фон
        # self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout(self)

        hero = self.service.get_hero()
        skills = self.service.get_skills()

        lbl_header = QLabel(f"Навички: {hero.hero_class.value}")
        lbl_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #8e44ad; margin-bottom: 10px;")
        lbl_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        # Прибираємо рамку та фон скролу
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(container)

        class_map = {"Воїн": "knight", "Лучник": "archer", "Маг": "mage", "Розбійник": "rogue"}
        cls_name = hero.hero_class.value if hasattr(hero.hero_class, 'value') else "Воїн"
        cls_folder = class_map.get(cls_name, "knight")
        base_path = get_project_root()

        for s in skills:
            frame = QFrame()
            # Темний фон для карток навичок
            frame.setStyleSheet("background-color: #2d2d2d; border-radius: 8px; border: 1px solid #555;")
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
            # Білий текст заголовка
            name_lbl.setStyleSheet(
                "font-weight: bold; font-size: 14px; color: white; border: none; background: transparent;")

            desc_lbl = QLabel(s['desc'])
            desc_lbl.setWordWrap(True)
            # Світло-сірий опис
            desc_lbl.setStyleSheet("color: #bdc3c7; border: none; background: transparent;")

            cost_lbl = QLabel(f"Мана: {s['mana_cost']}")
            cost_lbl.setStyleSheet(
                "color: #3498db; font-weight: bold; font-size: 10px; border: none; background: transparent;")

            text_layout.addWidget(name_lbl)
            text_layout.addWidget(desc_lbl)
            text_layout.addWidget(cost_lbl)

            status_lbl = QLabel()
            if hero.level >= s['level_req']:
                status_lbl.setText("✅")
                status_lbl.setStyleSheet("color: green; font-size: 20px; border: none; background: transparent;")
            else:
                status_lbl.setText("🔒")
                status_lbl.setStyleSheet("color: gray; font-size: 20px; border: none; background: transparent;")

            row.addWidget(lbl_icon)
            row.addLayout(text_layout)
            row.addWidget(status_lbl)

            vbox.addWidget(frame)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # --- ПОПЕРЕДЖЕННЯ ПРО ПОДВІЙНУ АТАКУ ---
        lbl_info = QLabel(
            "⚠️ Навички мають 50% від вашого шансу на подвійну дію. (включно з лікуванням). При подвійнійній дії бонус від повторного виконання також складає 50%.")
        lbl_info.setWordWrap(True)
        lbl_info.setAlignment(Qt.AlignCenter)
        # Темний стиль попередження
        lbl_info.setStyleSheet(
            "color: #e67e22; font-size: 12px; font-weight: bold; padding: 5px; border: 1px solid #e67e22; border-radius: 5px;")
        layout.addWidget(lbl_info)
        # ---------------------------------------

        btn_close = QPushButton("Закрити")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)