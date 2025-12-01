from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QDateTimeEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDateTime, Qt
from src.models import Difficulty
from src.logic import GoalService


class AddGoalDialog(QDialog):
    def __init__(self, parent, service: GoalService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Новий Квест ⚔️")
        self.resize(400, 450)
        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout(self)

        # 1. Назва
        self.layout.addWidget(QLabel("Назва квесту:"))
        self.title_input = QLineEdit()
        self.layout.addWidget(self.title_input)

        # 2. Опис
        self.layout.addWidget(QLabel("Опис:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.layout.addWidget(self.desc_input)

        # 3. Дедлайн
        self.layout.addWidget(QLabel("Дедлайн:"))
        self.date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_input.setCalendarPopup(True)
        # Встановлюємо формат без секунд
        self.date_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.layout.addWidget(self.date_input)

        # 4. Складність
        self.layout.addWidget(QLabel("Складність (Нагорода XP/Gold):"))
        self.diff_input = QComboBox()
        for diff in Difficulty:
            self.diff_input.addItem(f"{diff.name}", diff)
        self.layout.addWidget(self.diff_input)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Створити")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_save.clicked.connect(self.save_goal)

        btn_cancel = QPushButton("Скасувати")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        self.layout.addLayout(btn_layout)

    def save_goal(self):
        title = self.title_input.text()
        desc = self.desc_input.toPlainText()

        # Отримуємо дату і примусово обнуляємо секунди та мікросекунди
        deadline = self.date_input.dateTime().toPyDateTime().replace(second=0, microsecond=0)

        difficulty = self.diff_input.currentData()

        try:
            self.service.create_goal(title, desc, deadline, difficulty)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити квест:\n{str(e)}")