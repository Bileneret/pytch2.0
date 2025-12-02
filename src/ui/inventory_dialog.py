import os
import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QWidget, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from src.models import EquipmentSlot, Item


def get_project_root():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class InventoryDialog(QDialog):
    def __init__(self, parent, service):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Інвентар та Спорядження 🎒")
        self.resize(900, 600)
        # Видалено світлий фон
        # self.setStyleSheet("background-color: white;")

        self.layout = QHBoxLayout(self)

        # --- ЛІВА ЧАСТИНА: СУМКА (GRID) ---
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)

        self.left_layout.addWidget(
            QLabel("📦 В СУМЦІ", styleSheet="font-weight: bold; font-size: 14px; color: #f1c40f;"))

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # Прозорий фон, без рамок (щоб зливався з вікном)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")

        self.items_container = QWidget()
        # Прозорий фон контейнера
        self.items_container.setStyleSheet("background: transparent;")

        self.items_grid = QGridLayout(self.items_container)
        self.items_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.items_grid.setSpacing(10)

        self.scroll_area.setWidget(self.items_container)
        self.left_layout.addWidget(self.scroll_area)

        # --- ПРАВА ЧАСТИНА: СПОРЯДЖЕННЯ ---
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)

        self.right_layout.addWidget(
            QLabel("🛡️ СПОРЯДЖЕННЯ", styleSheet="font-weight: bold; font-size: 14px; color: #f1c40f;"))

        self.slots_container = QWidget()
        self.slots_layout = QVBoxLayout(self.slots_container)

        self.slot_widgets = {}
        display_order = [
            EquipmentSlot.HEAD, EquipmentSlot.BODY, EquipmentSlot.HANDS,
            EquipmentSlot.LEGS, EquipmentSlot.FEET,
            EquipmentSlot.MAIN_HAND, EquipmentSlot.OFF_HAND
        ]

        for slot in display_order:
            frame = QFrame()
            # Темний стиль для слота
            frame.setStyleSheet("background-color: #2d2d2d; border-radius: 5px; border: 1px solid #555;")
            hbox = QHBoxLayout(frame)
            hbox.setContentsMargins(5, 5, 5, 5)

            lbl_slot_name = QLabel(slot.value)
            lbl_slot_name.setFixedWidth(80)
            lbl_slot_name.setStyleSheet("color: #bdc3c7; font-weight: bold;")  # Світло-сірий

            lbl_item_name = QLabel("Пусто")
            lbl_item_name.setStyleSheet("color: white;")  # Білий

            btn_unequip = QPushButton("Зняти")
            btn_unequip.setCursor(Qt.PointingHandCursor)
            btn_unequip.setFixedWidth(60)
            # Червона кнопка "Зняти" залишається
            btn_unequip.setStyleSheet(
                "background-color: #e74c3c; color: white; border: none; border-radius: 3px; font-weight: bold;")
            btn_unequip.hide()

            hbox.addWidget(lbl_slot_name)
            hbox.addWidget(lbl_item_name)
            hbox.addStretch()
            hbox.addWidget(btn_unequip)

            self.slots_layout.addWidget(frame)

            self.slot_widgets[slot] = {
                'name_lbl': lbl_item_name,
                'btn': btn_unequip,
                'frame': frame
            }

        self.right_layout.addWidget(self.slots_container)
        self.right_layout.addStretch()

        self.lbl_bonuses = QLabel("Бонуси: 0")
        self.lbl_bonuses.setStyleSheet(
            "color: #27ae60; font-weight: bold; border: 1px solid #27ae60; padding: 10px; border-radius: 5px;")
        self.lbl_bonuses.setWordWrap(True)
        self.right_layout.addWidget(self.lbl_bonuses)

        # --- DEBUG BUTTON ЛИШЕ ДЛЯ tester ---
        hero = self.service.get_hero()
        if hero.nickname.lower() == "tester":
            btn_debug_add = QPushButton("🎁 Отримати тестові речі")
            btn_debug_add.setCursor(Qt.PointingHandCursor)
            btn_debug_add.clicked.connect(self.add_test_items)
            self.right_layout.addWidget(btn_debug_add)
        # ------------------------------------------------

        self.layout.addWidget(self.left_panel, stretch=3)
        self.layout.addWidget(self.right_panel, stretch=2)

        self.refresh_ui()

    def refresh_ui(self):
        """Оновлює інтерфейс."""
        # Очищення гріду
        for i in reversed(range(self.items_grid.count())):
            self.items_grid.itemAt(i).widget().setParent(None)

        try:
            inventory = self.service.get_inventory()
            equipped_items = {item.item.slot: item for item in inventory if item.is_equipped}
            bag_items = [item for item in inventory if not item.is_equipped]

            # --- ЗАПОВНЮЄМО СУМКУ (GRID) ---
            if not bag_items:
                self.items_grid.addWidget(QLabel("Інвентар порожній", styleSheet="color: gray;"), 0, 0)
            else:
                columns = 4  # Кількість колонок
                row, col = 0, 0
                for inv_item in bag_items:
                    item_widget = self.create_grid_item(inv_item)
                    self.items_grid.addWidget(item_widget, row, col)

                    col += 1
                    if col >= columns:
                        col = 0
                        row += 1

            # --- ОНОВЛЕННЯ СЛОТІВ ---
            total_bonuses = {'str': 0, 'int': 0, 'dex': 0, 'vit': 0, 'def': 0, 'base_dmg': 0, 'double_attack_chance': 0}

            for slot, widgets in self.slot_widgets.items():
                try:
                    widgets['btn'].clicked.disconnect()
                except TypeError:
                    pass

                if slot in equipped_items:
                    item = equipped_items[slot].item
                    widgets['name_lbl'].setText(f"{item.name}")
                    widgets['btn'].show()
                    widgets['btn'].clicked.connect(
                        lambda checked, i_id=equipped_items[slot].id: self.unequip_item(i_id))

                    # Стиль для АКТИВНОГО слота (Темно-зелений фон)
                    widgets['frame'].setStyleSheet(
                        "background-color: #254e38; border-radius: 5px; border: 1px solid #2ecc71;")

                    total_bonuses['str'] += item.bonus_str
                    total_bonuses['int'] += item.bonus_int
                    total_bonuses['dex'] += item.bonus_dex
                    total_bonuses['vit'] += item.bonus_vit
                    total_bonuses['def'] += item.bonus_def
                    total_bonuses['base_dmg'] += item.base_dmg
                    if hasattr(item, 'double_attack_chance'):
                        total_bonuses['double_attack_chance'] += item.double_attack_chance
                else:
                    widgets['name_lbl'].setText("Пусто")
                    widgets['btn'].hide()
                    # Стиль для ПОРОЖНЬОГО слота (Темний)
                    widgets['frame'].setStyleSheet(
                        "background-color: #2d2d2d; border-radius: 5px; border: 1px solid #555;")

            parts = []
            if total_bonuses['str']: parts.append(f"⚔️STR+{total_bonuses['str']}")
            if total_bonuses['int']: parts.append(f"🧠INT+{total_bonuses['int']}")
            if total_bonuses['dex']: parts.append(f"🎯DEX+{total_bonuses['dex']}")
            if total_bonuses['vit']: parts.append(f"🧡VIT+{total_bonuses['vit']}")
            if total_bonuses['def']: parts.append(f"🛡️DEF+{total_bonuses['def']}")
            if total_bonuses['base_dmg']: parts.append(f"💥DMG+{total_bonuses['base_dmg']}")
            if total_bonuses['double_attack_chance']: parts.append(f"⚡Double+{total_bonuses['double_attack_chance']}%")

            bonus_text = "БОНУСИ: " + ", ".join(parts) if parts else "БОНУСИ: Немає"
            self.lbl_bonuses.setText(bonus_text)

        except Exception as e:
            print(f"Inventory Error: {e}")
            import traceback
            traceback.print_exc()

    def create_grid_item(self, inv_item):
        """Створює іконку предмета для гріду."""
        btn = QPushButton()
        btn.setFixedSize(80, 80)
        btn.setCursor(Qt.PointingHandCursor)

        # Стиль кнопки в гріде (Темний)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                border: 1px solid #555;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #3e526a;
                border: 2px solid #3498db;
            }
        """)

        # Іконка
        if inv_item.item.image_path:
            base_path = get_project_root()
            img_path = os.path.join(base_path, "assets", "items", inv_item.item.image_path)
            if not os.path.exists(img_path):
                img_path = os.path.join(base_path, "assets", "enemies", inv_item.item.image_path)  # Fallback

            if os.path.exists(img_path):
                icon = QIcon(img_path)
                btn.setIcon(icon)
                btn.setIconSize(QSize(60, 60))
            else:
                btn.setText("📦")
        else:
            btn.setText("📦")

        btn.setToolTip(f"{inv_item.item.name}\n{inv_item.item.item_type.value}")
        btn.clicked.connect(lambda: self.show_item_details(inv_item))

        return btn

    def show_item_details(self, inv_item):
        """Відкриває спливаюче вікно з інформацією про предмет."""
        details = QDialog(self)
        details.setWindowTitle(inv_item.item.name)
        details.resize(300, 400)
        # Видалено білий фон, використовується глобальний стиль
        # details.setStyleSheet("background-color: white;")

        layout = QVBoxLayout(details)

        # Велика іконка
        lbl_img = QLabel()
        lbl_img.setAlignment(Qt.AlignCenter)
        lbl_img.setFixedSize(150, 150)

        if inv_item.item.image_path:
            base_path = get_project_root()
            img_path = os.path.join(base_path, "assets", "items", inv_item.item.image_path)
            if not os.path.exists(img_path): img_path = os.path.join(base_path, "assets", "enemies",
                                                                     inv_item.item.image_path)
            if os.path.exists(img_path):
                pix = QPixmap(img_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl_img.setPixmap(pix)
        layout.addWidget(lbl_img, 0, Qt.AlignHCenter)

        # Назва та тип
        title = QLabel(inv_item.item.name)
        # Заголовок жовтий
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: #f1c40f;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        type_lbl = QLabel(
            f"{inv_item.item.item_type.value} | {inv_item.item.slot.value if inv_item.item.slot else 'Сміття'}")
        type_lbl.setStyleSheet("color: #bdc3c7; font-size: 12px;")  # Сірий
        type_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(type_lbl)

        # Характеристики
        stats_text = ""
        item = inv_item.item
        if item.base_dmg: stats_text += f"💥 Урон: {item.base_dmg}\n"
        if item.bonus_str: stats_text += f"⚔️ Сила: +{item.bonus_str}\n"
        if item.bonus_int: stats_text += f"🧠 Інтелект: +{item.bonus_int}\n"
        if item.bonus_dex: stats_text += f"🎯 Спритність: +{item.bonus_dex}\n"
        if item.bonus_vit: stats_text += f"🧡 Здоров'я: +{item.bonus_vit}\n"
        if item.bonus_def: stats_text += f"🛡️ Захист: +{item.bonus_def}\n"
        if hasattr(item, 'double_attack_chance') and item.double_attack_chance:
            stats_text += f"⚡ Шанс подв. атаки: {item.double_attack_chance}%\n"

        stats_lbl = QLabel(stats_text)
        stats_lbl.setStyleSheet("font-size: 14px; margin-top: 10px; color: white;")
        stats_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(stats_lbl)

        layout.addStretch()

        # Кнопка "Вдягнути"
        if item.slot:
            btn_equip = QPushButton("Вдягнути")
            btn_equip.setCursor(Qt.PointingHandCursor)
            btn_equip.setStyleSheet(
                "background-color: #27ae60; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
            btn_equip.clicked.connect(lambda: [self.equip_item(inv_item.id, item.slot), details.accept()])
            layout.addWidget(btn_equip)

        btn_close = QPushButton("Закрити")
        btn_close.clicked.connect(details.accept)
        layout.addWidget(btn_close)

        details.exec_()

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

    def add_test_items(self):
        self.service.give_test_items()
        self.refresh_ui()
        QMessageBox.information(self, "Інвентар", "Тестові предмети додано!")