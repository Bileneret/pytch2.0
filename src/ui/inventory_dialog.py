import os
import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from src.models import EquipmentSlot, ItemType


def get_project_root():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class InventoryDialog(QDialog):
    def __init__(self, parent, service):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Інвентар та Спорядження 🎒")
        self.resize(800, 600)
        self.setStyleSheet("background-color: white;")

        self.layout = QHBoxLayout(self)

        # --- ЛІВА ЧАСТИНА: СПИСОК ПРЕДМЕТІВ (СУМКА) ---
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)

        self.left_layout.addWidget(
            QLabel("📦 В СУМЦІ", styleSheet="font-weight: bold; font-size: 14px; color: #2c3e50;"))

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background-color: #f0f2f5;")

        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.items_container)

        self.left_layout.addWidget(self.scroll_area)

        # --- ПРАВА ЧАСТИНА: СПОРЯДЖЕННЯ (ЛЯЛЬКА) ---
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)

        self.right_layout.addWidget(
            QLabel("🛡️ СПОРЯДЖЕННЯ", styleSheet="font-weight: bold; font-size: 14px; color: #2c3e50;"))

        # Створюємо віджети для кожного слота
        self.slots_container = QWidget()
        self.slots_layout = QVBoxLayout(self.slots_container)

        self.slot_widgets = {}
        # Порядок відображення слотів
        display_order = [
            EquipmentSlot.HEAD,
            EquipmentSlot.BODY,
            EquipmentSlot.HANDS,
            EquipmentSlot.LEGS,
            EquipmentSlot.FEET,
            EquipmentSlot.MAIN_HAND,
            EquipmentSlot.OFF_HAND
        ]

        for slot in display_order:
            frame = QFrame()
            frame.setStyleSheet("background-color: #ecf0f1; border-radius: 5px; border: 1px solid #bdc3c7;")
            hbox = QHBoxLayout(frame)
            hbox.setContentsMargins(5, 5, 5, 5)

            lbl_slot_name = QLabel(slot.value)
            lbl_slot_name.setFixedWidth(80)
            lbl_slot_name.setStyleSheet("color: #7f8c8d; font-weight: bold;")

            lbl_item_name = QLabel("Пусто")
            lbl_item_name.setStyleSheet("color: #2c3e50;")

            btn_unequip = QPushButton("Зняти")
            btn_unequip.setCursor(Qt.PointingHandCursor)
            btn_unequip.setFixedWidth(60)
            btn_unequip.setStyleSheet(
                "background-color: #e74c3c; color: white; border: none; border-radius: 3px; font-weight: bold;")
            btn_unequip.hide()  # Ховаємо, якщо нічого не вдягнуто

            hbox.addWidget(lbl_slot_name)
            hbox.addWidget(lbl_item_name)
            hbox.addStretch()
            hbox.addWidget(btn_unequip)

            self.slots_layout.addWidget(frame)

            # Зберігаємо посилання на віджети, щоб оновлювати їх
            self.slot_widgets[slot] = {
                'name_lbl': lbl_item_name,
                'btn': btn_unequip,
                'frame': frame
            }

        self.right_layout.addWidget(self.slots_container)
        self.right_layout.addStretch()

        # Відображення бонусів від спорядження
        self.lbl_bonuses = QLabel("Бонуси: 0")
        self.lbl_bonuses.setStyleSheet(
            "color: #27ae60; font-weight: bold; border: 1px solid #27ae60; padding: 10px; border-radius: 5px;")
        self.right_layout.addWidget(self.lbl_bonuses)

        self.layout.addWidget(self.left_panel, stretch=3)
        self.layout.addWidget(self.right_panel, stretch=2)

        self.refresh_ui()

    def refresh_ui(self):
        """Оновлює списки предметів та слоти."""
        # 1. Очищаємо список предметів
        while self.items_layout.count():
            child = self.items_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        try:
            inventory = self.service.get_inventory()

            # Розділяємо на вдягнуті та невдягнуті
            equipped_items = {item.item.slot: item for item in inventory if item.is_equipped}
            bag_items = [item for item in inventory if not item.is_equipped]

            # --- Заповнюємо сумку ---
            if not bag_items:
                self.items_layout.addWidget(
                    QLabel("Інвентар порожній", styleSheet="color: gray; margin-top: 20px;", alignment=Qt.AlignCenter))
            else:
                for inv_item in bag_items:
                    self.create_item_card(inv_item)

            # --- Оновлюємо слоти ---
            total_bonuses = {'str': 0, 'int': 0, 'dex': 0, 'vit': 0, 'def': 0}

            for slot, widgets in self.slot_widgets.items():
                if slot in equipped_items:
                    item = equipped_items[slot].item
                    widgets['name_lbl'].setText(f"{item.name}")
                    widgets['btn'].show()
                    widgets['btn'].clicked.disconnect()  # Видаляємо старі підключення
                    widgets['btn'].clicked.connect(
                        lambda checked, i_id=equipped_items[slot].id: self.unequip_item(i_id))
                    widgets['frame'].setStyleSheet(
                        "background-color: #d5f5e3; border-radius: 5px; border: 1px solid #2ecc71;")  # Зелений фон

                    # Рахуємо бонуси для відображення
                    total_bonuses['str'] += item.bonus_str
                    total_bonuses['int'] += item.bonus_int
                    total_bonuses['dex'] += item.bonus_dex
                    total_bonuses['vit'] += item.bonus_vit
                    total_bonuses['def'] += item.bonus_def
                else:
                    widgets['name_lbl'].setText("Пусто")
                    widgets['btn'].hide()
                    widgets['frame'].setStyleSheet(
                        "background-color: #ecf0f1; border-radius: 5px; border: 1px solid #bdc3c7;")

            # --- Оновлюємо текст бонусів ---
            bonus_text = "БОНУСИ ВІД РЕЧЕЙ:\n"
            if total_bonuses['str']: bonus_text += f"⚔️ Сила: +{total_bonuses['str']}  "
            if total_bonuses['int']: bonus_text += f"🧠 Інтел: +{total_bonuses['int']}  "
            if total_bonuses['dex']: bonus_text += f"🎯 Сприт: +{total_bonuses['dex']}  "
            if total_bonuses['vit']: bonus_text += f"❤️ Здор: +{total_bonuses['vit']}  "
            if total_bonuses['def']: bonus_text += f"🛡️ Захист: +{total_bonuses['def']}"

            if bonus_text == "БОНУСИ ВІД РЕЧЕЙ:\n": bonus_text = "Немає активних бонусів"
            self.lbl_bonuses.setText(bonus_text)

        except Exception as e:
            print(f"Inventory Error: {e}")

    def create_item_card(self, inv_item):
        """Створює картку предмета в списку."""
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border: 1px solid #bdc3c7; border-radius: 5px;")
        layout = QHBoxLayout(frame)

        # Іконка
        lbl_icon = QLabel("📦")
        if inv_item.item.image_path:
            base_path = get_project_root()
            # Припускаємо, що іконки предметів лежать в assets/items/
            # Якщо ні, можна використовувати assets/enemies як заглушку або створити папку
            img_path = os.path.join(base_path, "assets", "items", inv_item.item.image_path)
            if os.path.exists(img_path):
                pix = QPixmap(img_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl_icon.setPixmap(pix)

        lbl_icon.setFixedSize(40, 40)
        lbl_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_icon)

        # Інфо
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(inv_item.item.name, styleSheet="font-weight: bold; font-size: 12px;"))

        # Рядок характеристик предмета
        stats = []
        if inv_item.item.bonus_str: stats.append(f"STR+{inv_item.item.bonus_str}")
        if inv_item.item.bonus_int: stats.append(f"INT+{inv_item.item.bonus_int}")
        if inv_item.item.bonus_def: stats.append(f"DEF+{inv_item.item.bonus_def}")
        if inv_item.item.bonus_dex: stats.append(f"DEX+{inv_item.item.bonus_dex}")
        stats_str = ", ".join(stats) if stats else "Звичайний предмет"

        info_layout.addWidget(
            QLabel(f"{inv_item.item.item_type.value} | {stats_str}", styleSheet="color: gray; font-size: 10px;"))
        layout.addLayout(info_layout)

        layout.addStretch()

        # Кнопка "Вдягнути"
        if inv_item.item.slot:  # Якщо предмет можна вдягнути
            btn_equip = QPushButton("Вдягнути")
            btn_equip.setCursor(Qt.PointingHandCursor)
            btn_equip.setStyleSheet(
                "background-color: #3498db; color: white; border: none; padding: 5px; border-radius: 3px; font-weight: bold;")
            btn_equip.clicked.connect(lambda: self.equip_item(inv_item.id, inv_item.item.slot))
            layout.addWidget(btn_equip)

        self.items_layout.addWidget(frame)

    def equip_item(self, inv_id, slot):
        try:
            self.service.equip_item(inv_id, slot)
            self.refresh_ui()
        except Exception as e:
            QMessageBox.warning(self, "Помилка", str(e))

    def unequip_item(self, inv_id):
        try:
            self.service.unequip_item(inv_id)
            self.refresh_ui()
        except Exception as e:
            QMessageBox.warning(self, "Помилка", str(e))