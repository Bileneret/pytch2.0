import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox, QHBoxLayout, QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from src.logic import AuthService
from src.models import HeroClass, Gender


# Утиліта для отримання кореневого шляху
def get_project_root():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class LoginWindow(QWidget):
    login_successful = pyqtSignal()

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.setWindowTitle("Вхід 🛡️")
        self.resize(300, 250)
        # Видалено примусовий білий фон
        # self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Текст автоматично стане світлим завдяки QSS
        layout.addWidget(QLabel("Введіть Нікнейм вашого Героя:", styleSheet="font-size: 14px; font-weight: bold;"))

        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("Нікнейм")
        layout.addWidget(self.nick_input)

        # Стиль кнопок залишено специфічним (синій)
        btn_login = QPushButton("Увійти")
        btn_login.setStyleSheet("background-color: #3498db; color: white; padding: 10px; font-weight: bold;")
        btn_login.clicked.connect(self.do_login)
        layout.addWidget(btn_login)

        layout.addStretch()

        layout.addWidget(QLabel("Перший раз тут?"))

        # Стиль кнопок залишено специфічним (зелений)
        btn_create = QPushButton("Створити Персонажа")
        btn_create.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
        btn_create.clicked.connect(self.open_creation)
        layout.addWidget(btn_create)

    def do_login(self):
        nick = self.nick_input.text().strip()
        try:
            self.auth_service.login(nick)
            self.login_successful.emit()
        except Exception as e:  # Ловимо всі помилки
            QMessageBox.warning(self, "Помилка входу", str(e))

    def open_creation(self):
        self.creation_window = CreationWindow(self.auth_service)
        self.creation_window.creation_successful.connect(self.on_creation_success)
        self.creation_window.show()
        self.close()

    def on_creation_success(self):
        self.login_successful.emit()
        self.creation_window.close()


class CreationWindow(QWidget):
    creation_successful = pyqtSignal()

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.setWindowTitle("Створення Персонажа ✨")
        self.resize(450, 600)
        # Видалено примусовий білий фон
        # self.setStyleSheet("background-color: white;")

        self.available_images = []
        self.current_image_index = 0
        self.relative_folder_path = ""

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)

        # 1. Нікнейм
        self.layout.addWidget(QLabel("1. Оберіть ім'я:", styleSheet="font-weight: bold;"))
        self.nick_input = QLineEdit()
        self.layout.addWidget(self.nick_input)

        # 2. Клас
        self.layout.addWidget(QLabel("2. Оберіть клас:", styleSheet="font-weight: bold;"))
        self.class_combo = QComboBox()
        for hc in HeroClass:
            self.class_combo.addItem(hc.value, hc)
        self.class_combo.currentIndexChanged.connect(self.load_appearance_images)
        self.layout.addWidget(self.class_combo)

        # 3. Стать
        self.layout.addWidget(QLabel("3. Оберіть стать:", styleSheet="font-weight: bold;"))
        self.gender_combo = QComboBox()
        for g in Gender:
            self.gender_combo.addItem(g.value, g)
        self.gender_combo.currentIndexChanged.connect(self.load_appearance_images)
        self.layout.addWidget(self.gender_combo)

        # 4. Зовнішність
        self.layout.addWidget(QLabel("4. Зовнішність:", styleSheet="font-weight: bold;"))

        appearance_layout = QHBoxLayout()

        self.btn_prev = QPushButton("<")
        self.btn_prev.setFixedSize(30, 50)
        self.btn_prev.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.btn_prev.clicked.connect(self.prev_image)
        appearance_layout.addWidget(self.btn_prev)

        self.lbl_image = QLabel("Завантаження...")
        self.lbl_image.setFixedSize(200, 200)
        self.lbl_image.setAlignment(Qt.AlignCenter)
        # Прибрано світлий background-color: #ecf0f1; залишено тільки рамку
        self.lbl_image.setStyleSheet("border: 2px solid #bdc3c7; border-radius: 10px;")
        appearance_layout.addWidget(self.lbl_image)

        self.btn_next = QPushButton(">")
        self.btn_next.setFixedSize(30, 50)
        self.btn_next.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.btn_next.clicked.connect(self.next_image)
        appearance_layout.addWidget(self.btn_next)

        self.layout.addLayout(appearance_layout)

        self.lbl_filename = QLabel("")
        self.lbl_filename.setAlignment(Qt.AlignCenter)
        self.lbl_filename.setStyleSheet("color: gray; font-size: 10px;")
        self.layout.addWidget(self.lbl_filename)

        self.layout.addStretch()

        btn_create = QPushButton("Створити Героя")
        btn_create.setStyleSheet(
            "background-color: #8e44ad; color: white; padding: 12px; font-weight: bold; font-size: 14px;")
        btn_create.clicked.connect(self.create_character)
        self.layout.addWidget(btn_create)

        self.load_appearance_images()

    def load_appearance_images(self):
        gender_enum = self.gender_combo.currentData()
        class_enum = self.class_combo.currentData()

        gender_str = "male" if gender_enum == Gender.MALE else "female"

        class_map = {
            HeroClass.WARRIOR: "knight",
            HeroClass.ARCHER: "archer",
            HeroClass.MAGE: "mage",
            HeroClass.ROGUE: "rogue"
        }
        class_str = class_map.get(class_enum, "knight")

        base_path = get_project_root()
        self.relative_folder_path = os.path.join("assets", "look", gender_str, class_str)
        full_path = os.path.join(base_path, self.relative_folder_path)

        self.available_images = []

        if os.path.exists(full_path):
            try:
                files = [f for f in os.listdir(full_path) if f.lower().endswith('.png')]
                self.available_images = sorted(files)
            except Exception as e:
                print(f"Error reading images: {e}")

        self.current_image_index = 0
        self.update_image_display()

    def update_image_display(self):
        if not self.available_images:
            self.lbl_image.setText("Немає зображень\nдля цього класу")
            self.lbl_image.setPixmap(QPixmap())
            self.lbl_filename.setText("")
            return

        filename = self.available_images[self.current_image_index]
        base_path = get_project_root()
        full_img_path = os.path.join(base_path, self.relative_folder_path, filename)

        if os.path.exists(full_img_path):
            pixmap = QPixmap(full_img_path)
            pixmap = pixmap.scaled(self.lbl_image.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_image.setPixmap(pixmap)
            self.lbl_filename.setText(f"{self.current_image_index + 1}/{len(self.available_images)}")
        else:
            self.lbl_image.setText("Помилка файлу")

    def next_image(self):
        if not self.available_images: return
        self.current_image_index = (self.current_image_index + 1) % len(self.available_images)
        self.update_image_display()

    def prev_image(self):
        if not self.available_images: return
        self.current_image_index = (self.current_image_index - 1) % len(self.available_images)
        self.update_image_display()

    def create_character(self):
        nick = self.nick_input.text().strip()
        h_class = self.class_combo.currentData()
        gender = self.gender_combo.currentData()

        appearance_path = ""
        if self.available_images:
            filename = self.available_images[self.current_image_index]
            appearance_path = os.path.join(self.relative_folder_path, filename)
        else:
            appearance_path = "assets/enemies/goblin.png"

        try:
            self.auth_service.register(nick, h_class, gender, appearance_path)
            QMessageBox.information(self, "Успіх", "Героя створено! Пригоди починаються!")
            self.creation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "Критична помилка", f"Не вдалося створити героя:\n{str(e)}")