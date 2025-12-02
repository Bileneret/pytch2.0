import os
import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon


def get_project_root():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class ShopDialog(QDialog):
    def __init__(self, parent, service):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Магазин 🛒")
        self.resize(950, 950)
        # Видалено світлий фон
        # self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout(self)

        # Баланс
        self.lbl_balance = QLabel("💰 Баланс: 0")
        self.lbl_balance.setStyleSheet("font-size: 18px; font-weight: bold; color: #f1c40f; margin: 10px;")
        self.lbl_balance.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_balance)

        # Список товарів
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        # Прибираємо фон скролу
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(container)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid.setSpacing(15)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # Кнопка закрити
        btn_close = QPushButton("Закрити")
        btn_close.clicked.connect(self.accept)
        # Стиль підтягнеться з global QSS
        layout.addWidget(btn_close)

        self.refresh_ui()

    def refresh_ui(self):
        # Очищення
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        # Баланс
        hero = self.service.get_hero()
        self.lbl_balance.setText(f"💰 Баланс: {hero.gold}")

        # Товари
        items = self.service.get_all_library_items()
        # Сортуємо за ціною
        items.sort(key=lambda x: x.price)

        columns = 4
        row, col = 0, 0

        for item in items:
            card = self.create_item_card(item)
            self.grid.addWidget(card, row, col)

            col += 1
            if col >= columns:
                col = 0
                row += 1

    def create_item_card(self, item):
        frame = QFrame()
        frame.setFixedSize(200, 250)
        # Темний стиль для карток
        frame.setStyleSheet("""
            QFrame { 
                background-color: #2d2d2d; 
                border: 1px solid #555; 
                border-radius: 8px; 
            }
            QFrame:hover { border: 2px solid #3498db; }
        """)
        layout = QVBoxLayout(frame)

        # Картинка
        lbl_icon = QLabel()
        lbl_icon.setAlignment(Qt.AlignCenter)
        if item.image_path:
            base_path = get_project_root()
            img_path = os.path.join(base_path, "assets", "items", item.image_path)
            if os.path.exists(img_path):
                pix = QPixmap(img_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl_icon.setPixmap(pix)
            else:
                lbl_icon.setText("📦")
        layout.addWidget(lbl_icon)

        # Назва
        name = QLabel(item.name)
        name.setStyleSheet("font-weight: bold; border: none; background: transparent; color: white;")
        name.setWordWrap(True)
        name.setAlignment(Qt.AlignCenter)
        layout.addWidget(name)

        # Ціна
        price = QLabel(f"💰 {item.price}")
        price.setStyleSheet("color: #f39c12; font-weight: bold; border: none; background: transparent;")
        price.setAlignment(Qt.AlignCenter)
        layout.addWidget(price)

        # Стати
        stats = []
        if item.bonus_str: stats.append(f"STR+{item.bonus_str}")
        if item.bonus_int: stats.append(f"INT+{item.bonus_int}")
        if item.bonus_def: stats.append(f"DEF+{item.bonus_def}")
        stats_str = " ".join(stats) if stats else "Звичайний"

        lbl_stats = QLabel(stats_str)
        # Світло-сірий колір для другорядної інфи
        lbl_stats.setStyleSheet("color: #bdc3c7; font-size: 10px; border: none; background: transparent;")
        lbl_stats.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_stats)

        # Кнопка Купити
        btn_buy = QPushButton("Купити")
        btn_buy.setCursor(Qt.PointingHandCursor)
        # Зелена кнопка збережена
        btn_buy.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; border: none; border-radius: 4px; padding: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_buy.clicked.connect(lambda: self.buy_item(item))
        layout.addWidget(btn_buy)

        return frame

    def buy_item(self, item):
        try:
            msg = self.service.buy_item(item.id)
            QMessageBox.information(self, "Успіх", msg)
            self.refresh_ui()
        except ValueError as e:
            QMessageBox.warning(self, "Помилка", str(e))