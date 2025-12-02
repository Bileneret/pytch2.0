from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt
from src.logic import GoalService


class StatsDialog(QDialog):
    def __init__(self, parent, service: GoalService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Характеристики Героя 📊")
        self.resize(500, 650)
        # Видалено світлий фон
        # self.setStyleSheet("background-color: white;")

        self.hero = self.service.get_hero()
        self.bonuses = self.service.calculate_equipment_bonuses()

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- ЗАГОЛОВОК: ОЧКИ ---
        self.lbl_points = QLabel(f"Вільні очки: {self.hero.stat_points}")
        self.lbl_points.setAlignment(Qt.AlignCenter)
        self.lbl_points.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2980b9; margin-bottom: 10px; border-bottom: 2px solid #555; padding-bottom: 10px;")
        layout.addWidget(self.lbl_points)

        # --- СЕКЦІЯ 1: БОЙОВІ ПАРАМЕТРИ (Frame) ---
        combat_frame = QFrame()
        # Темний фон для блоку
        combat_frame.setStyleSheet("background-color: #2d2d2d; border-radius: 8px; border: 1px solid #555;")
        combat_layout = QVBoxLayout(combat_frame)

        lbl_combat_header = QLabel("⚔️ БОЙОВА ЕФЕКТИВНІСТЬ")
        lbl_combat_header.setStyleSheet("font-weight: bold; color: #bdc3c7; font-size: 12px; border: none; background: transparent;")
        combat_layout.addWidget(lbl_combat_header, 0, Qt.AlignHCenter)

        # Розрахунок урону
        phys_dmg, magic_dmg = self.service.calculate_hero_damage(self.hero)
        double_chance = self.bonuses.get('double_attack_chance', 0)

        # Grid для бойових статів
        c_grid = QGridLayout()
        c_grid.setSpacing(10)

        # Фіз урон
        c_grid.addWidget(QLabel("💥 Фізичний урон:", styleSheet="border: none; background: transparent; color: white;"), 0, 0)
        self.lbl_phys = QLabel(str(phys_dmg))
        self.lbl_phys.setStyleSheet("font-weight: bold; font-size: 16px; color: #c0392b; border: none; background: transparent;")
        c_grid.addWidget(self.lbl_phys, 0, 1)

        # Маг урон
        c_grid.addWidget(QLabel("✨ Магічний урон:", styleSheet="border: none; background: transparent; color: white;"), 1, 0)
        self.lbl_magic = QLabel(str(magic_dmg))
        self.lbl_magic.setStyleSheet("font-weight: bold; font-size: 16px; color: #8e44ad; border: none; background: transparent;")
        c_grid.addWidget(self.lbl_magic, 1, 1)

        # Подвійна атака
        c_grid.addWidget(QLabel("⚡ Подвійна атака:", styleSheet="border: none; background: transparent; color: white;"), 2, 0)
        val_da = f"{double_chance}%"
        color_da = "#27ae60" if double_chance > 0 else "gray"
        lbl_da = QLabel(val_da)
        lbl_da.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {color_da}; border: none; background: transparent;")
        c_grid.addWidget(lbl_da, 2, 1)

        combat_layout.addLayout(c_grid)
        layout.addWidget(combat_frame)

        # --- СЕКЦІЯ 2: ОСНОВНІ ХАРАКТЕРИСТИКИ ---
        layout.addWidget(
            QLabel("📈 ОСНОВНІ ХАРАКТЕРИСТИКИ", styleSheet="font-weight: bold; color: #bdc3c7; margin-top: 10px;"))

        self.stats_layout = QVBoxLayout()
        self.stats_layout.setSpacing(8)

        # Створення рядків
        self.create_stat_row("Сила ⚔️", "str_stat", "str", "+2 Фіз. Урон")
        self.create_stat_row("Інтелект 🧠", "int_stat", "int", "+2 Маг. Урон, +5 Мана")
        self.create_stat_row("Спритність 🎯", "dex_stat", "dex", "+1% Ухилення")
        self.create_stat_row("Здоров'я 🧡", "vit_stat", "vit", "+5 Макс. HP")
        self.create_stat_row("Захист 🛡️", "def_stat", "def", "-2 Отримуваний урон")

        layout.addLayout(self.stats_layout)
        layout.addStretch()

        # Кнопка закрити
        btn_close = QPushButton("Закрити")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        # Стиль кнопки підтягнеться з QSS, або можна залишити дефолтний сірий
        btn_close.setStyleSheet("""
            QPushButton { background-color: #95a5a6; color: #2c3e50; border-radius: 5px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        layout.addWidget(btn_close)

    def create_stat_row(self, name, attr_name, bonus_key, description):
        """Створює рядок характеристики з відображенням бонусів."""
        row_frame = QFrame()
        # Темний фон для рядка
        row_frame.setStyleSheet("background-color: #2d2d2d; border-radius: 5px;")
        row_layout = QHBoxLayout(row_frame)
        row_layout.setContentsMargins(10, 5, 10, 5)

        # 1. Назва
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-size: 14px; font-weight: bold; border: none; background: transparent; color: white;")
        lbl_name.setFixedWidth(130)

        # 2. Значення (База + Бонус)
        base_val = getattr(self.hero, attr_name)
        bonus_val = self.bonuses.get(bonus_key, 0)
        total_val = base_val + bonus_val

        # Форматування тексту
        if bonus_val > 0:
            val_text = f"{total_val} <span style='color:#bdc3c7; font-size:14px;'>({base_val} + <span style='color:#27ae60;'>{bonus_val}</span>)</span>"
        else:
            val_text = f"{total_val}"

        lbl_val = QLabel(val_text)
        lbl_val.setStyleSheet("font-size: 16px; border: none; background: transparent; color: white;")
        lbl_val.setTextFormat(Qt.RichText)
        lbl_val.setFixedWidth(150)

        # 3. Кнопка "+"
        btn_plus = QPushButton("+")
        btn_plus.setFixedSize(30, 30)
        btn_plus.setCursor(Qt.PointingHandCursor)
        # Зелена кнопка збережена
        btn_plus.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; border-radius: 5px; border: none; }
            QPushButton:disabled { background-color: #555; color: #888; }
            QPushButton:hover { background-color: #2ecc71; }
        """)

        # Зберігаємо посилання на віджети
        btn_plus.clicked.connect(lambda checked, a=attr_name, l=lbl_val, b=bonus_key: self.increase_stat(a, l, b))

        setattr(self, f"btn_{attr_name}", btn_plus)
        if self.hero.stat_points <= 0:
            btn_plus.setEnabled(False)

        row_layout.addWidget(lbl_name)
        row_layout.addWidget(lbl_val)
        row_layout.addStretch()
        row_layout.addWidget(btn_plus)

        self.stats_layout.addWidget(row_frame)

    def increase_stat(self, attr_name, lbl_widget, bonus_key):
        if self.hero.stat_points > 0:
            current_base = getattr(self.hero, attr_name)
            setattr(self.hero, attr_name, current_base + 1)
            self.hero.stat_points -= 1

            self.hero.update_derived_stats()
            self.service.storage.update_hero(self.hero)

            new_base = current_base + 1
            bonus_val = self.bonuses.get(bonus_key, 0)
            total_val = new_base + bonus_val

            if bonus_val > 0:
                val_text = f"{total_val} <span style='color:#bdc3c7; font-size:14px;'>({new_base} + <span style='color:#27ae60;'>{bonus_val}</span>)</span>"
            else:
                val_text = f"{total_val}"

            lbl_widget.setText(val_text)
            self.lbl_points.setText(f"Вільні очки: {self.hero.stat_points}")

            if self.hero.stat_points == 0:
                self.disable_all_buttons()

            new_phys, new_magic = self.service.calculate_hero_damage(self.hero)
            self.lbl_phys.setText(str(new_phys))
            self.lbl_magic.setText(str(new_magic))

    def disable_all_buttons(self):
        for attr in ["str_stat", "int_stat", "dex_stat", "vit_stat", "def_stat"]:
            btn = getattr(self, f"btn_{attr}", None)
            if btn: btn.setEnabled(False)