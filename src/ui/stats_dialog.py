from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from src.logic import GoalService


class StatsDialog(QDialog):
    def __init__(self, parent, service: GoalService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Характеристики Героя 📊")
        self.resize(400, 500)
        self.setStyleSheet("background-color: white;")

        self.hero = self.service.get_hero()

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Заголовок
        self.lbl_points = QLabel(f"Вільні очки: {self.hero.stat_points}")
        self.lbl_points.setAlignment(Qt.AlignCenter)
        self.lbl_points.setStyleSheet("font-size: 18px; font-weight: bold; color: #2980b9;")
        layout.addWidget(self.lbl_points)

        # Список статів
        self.stats_layout = QVBoxLayout()

        self.create_stat_row("Сила ⚔️", "str_stat", "+2 Фіз. Урон")
        self.create_stat_row("Інтелект 🧠", "int_stat", "+2 Маг. Урон, +5 Мана")
        self.create_stat_row("Спритність 🎯", "dex_stat", "+1% Ухилення")
        self.create_stat_row("Здоров'я 🧡", "vit_stat", "+5 Макс. HP")
        self.create_stat_row("Захист 🛡️", "def_stat", "-2 Отримуваний урон")

        layout.addLayout(self.stats_layout)

        # Кнопка закрити
        btn_close = QPushButton("Закрити")
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet("""
            QPushButton { background-color: #bdc3c7; color: black; border-radius: 5px; padding: 10px; }
            QPushButton:hover { background-color: #a6acaf; }
        """)
        layout.addWidget(btn_close)

    def create_stat_row(self, name, attr_name, description):
        row = QHBoxLayout()

        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-size: 14px; font-weight: bold;")
        lbl_name.setFixedWidth(120)

        val = getattr(self.hero, attr_name)
        lbl_val = QLabel(str(val))
        lbl_val.setStyleSheet("font-size: 14px;")
        lbl_val.setFixedWidth(30)

        lbl_desc = QLabel(description)
        lbl_desc.setStyleSheet("color: gray; font-size: 10px;")

        btn_plus = QPushButton("+")
        btn_plus.setFixedSize(30, 30)
        btn_plus.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; border-radius: 5px; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        btn_plus.clicked.connect(lambda: self.increase_stat(attr_name, lbl_val, btn_plus))

        # Зберігаємо кнопку, щоб вимкнути її пізніше
        setattr(self, f"btn_{attr_name}", btn_plus)
        if self.hero.stat_points <= 0:
            btn_plus.setEnabled(False)

        row.addWidget(lbl_name)
        row.addWidget(lbl_val)
        row.addWidget(btn_plus)
        row.addWidget(lbl_desc)

        self.stats_layout.addLayout(row)

    def increase_stat(self, attr_name, lbl_widget, btn_widget):
        if self.hero.stat_points > 0:
            current_val = getattr(self.hero, attr_name)
            setattr(self.hero, attr_name, current_val + 1)
            self.hero.stat_points -= 1

            self.hero.update_derived_stats()
            self.service.storage.update_hero(self.hero)

            lbl_widget.setText(str(current_val + 1))
            self.lbl_points.setText(f"Вільні очки: {self.hero.stat_points}")

            if self.hero.stat_points == 0:
                self.disable_all_buttons()

    def disable_all_buttons(self):
        for attr in ["str_stat", "int_stat", "dex_stat", "vit_stat", "def_stat"]:
            btn = getattr(self, f"btn_{attr}", None)
            if btn: btn.setEnabled(False)