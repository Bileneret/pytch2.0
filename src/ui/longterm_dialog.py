from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QSpinBox, QPushButton, QMessageBox, QTimeEdit, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTime
from src.logic import GoalService


class AddLongTermDialog(QDialog):
    def __init__(self, parent, service: GoalService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Нова Звичка 📅")
        self.resize(400, 550)  # Трохи збільшив висоту
        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(12)

        # 1. Назва
        self.layout.addWidget(QLabel("Назва (напр. 'Вчити Python'):"))
        self.title_input = QLineEdit()
        self.layout.addWidget(self.title_input)

        # 2. Тривалість
        self.layout.addWidget(QLabel("Тривалість челенджу (днів):"))
        self.days_input = QSpinBox()
        self.days_input.setRange(1, 365)
        self.days_input.setValue(30)
        self.layout.addWidget(self.days_input)

        # 3. Час виконання
        self.layout.addWidget(QLabel("Час виконання (Початок - Кінець):"))

        time_layout = QHBoxLayout()
        self.start_time = QTimeEdit()
        self.start_time.setDisplayFormat("HH:mm")
        self.start_time.setTime(QTime(9, 0))

        lbl_dash = QLabel("-")
        lbl_dash.setAlignment(Qt.AlignCenter)

        self.end_time = QTimeEdit()
        self.end_time.setDisplayFormat("HH:mm")
        self.end_time.setTime(QTime(10, 0))

        time_layout.addWidget(self.start_time)
        time_layout.addWidget(lbl_dash)
        time_layout.addWidget(self.end_time)

        self.layout.addLayout(time_layout)

        # 4. Опис
        self.layout.addWidget(QLabel("Опис:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.layout.addWidget(self.desc_input)

        # --- ПОПЕРЕДЖЕННЯ ---
        lbl_warning = QLabel("⚠️ Увага: Виконання звички та дедлайни\nрозпочнуться з НАСТУПНОГО дня.")
        lbl_warning.setStyleSheet(
            "color: #e67e22; font-weight: bold; font-size: 12px; border: 1px solid #e67e22; padding: 5px; border-radius: 4px;")
        lbl_warning.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(lbl_warning)

        # Кнопка
        btn_save = QPushButton("Почати Челендж")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton { 
                background-color: #8e44ad; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #9b59b6; }
        """)
        btn_save.clicked.connect(self.save_goal)
        self.layout.addWidget(btn_save)

    def save_goal(self):
        title = self.title_input.text()
        days = self.days_input.value()
        desc = self.desc_input.toPlainText()

        t_start = self.start_time.time().toString("HH:mm")
        t_end = self.end_time.time().toString("HH:mm")
        time_frame = f"{t_start} - {t_end}"

        try:
            self.service.create_long_term_goal(title, desc, days, time_frame)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити звичку:\n{str(e)}")