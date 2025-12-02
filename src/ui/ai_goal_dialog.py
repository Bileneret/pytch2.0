from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QProgressBar, QMessageBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from datetime import datetime, timedelta
from src.logic.ai_service import AIService
from src.models import Goal, Difficulty, SubGoal


class AIChatWorker(QThread):
    """Потік для спілкування з AI, щоб не блокувати GUI."""
    response_received = pyqtSignal(str, object)  # text, json_data

    def __init__(self, ai_service, chat_session, message):
        super().__init__()
        self.service = ai_service
        self.chat = chat_session
        self.message = message

    def run(self):
        text, json_data = self.service.send_to_chat(self.chat, self.message)
        self.response_received.emit(text, json_data)


class ChatInputArea(QTextEdit):
    """
    Кастомне поле вводу для чату.
    Enter - відправити повідомлення.
    Shift + Enter - перенос рядка.
    """
    submit_request = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Опишіть вашу ціль тут... (Shift+Enter для переносу)")
        self.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 1px solid #555;
                border-radius: 5px;
                background-color: #333;
                color: white;
            }
        """)
        self.setFixedHeight(60)  # Фіксована висота для компактності

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            if event.modifiers() & Qt.ShiftModifier:
                # Shift + Enter -> Новий рядок (стандартна поведінка QTextEdit при натисканні Enter)
                self.insertPlainText("\n")
            else:
                # Enter (без Shift) -> Відправити
                self.submit_request.emit()
                # Блокуємо стандартну подію, щоб не вставився зайвий перенос рядка
                return
        else:
            super().keyPressEvent(event)


class AIGoalDialog(QDialog):
    """Діалог чату з AI для створення цілі."""

    def __init__(self, parent, service):
        super().__init__(parent)
        self.main_service = service  # GoalService
        self.ai_service = AIService()
        self.chat_session = None
        self.generated_goal_data = None  # Тут буде JSON, коли AI його видасть

        self.setWindowTitle("AI Помічник 🤖")
        self.resize(500, 600)
        self.setup_ui()

        # Запускаємо чат
        self.start_chat()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 1. Область чату
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.chat_area)

        # 2. Індикатор завантаження (AI друкує...)
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)  # Нескінченна анімація
        self.loading_bar.setFixedHeight(3)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setStyleSheet(
            "QProgressBar { background: transparent; border: none; } QProgressBar::chunk { background-color: #3498db; }")
        self.loading_bar.hide()
        layout.addWidget(self.loading_bar)

        # 3. Поле вводу (Використовуємо кастомний клас)
        input_layout = QHBoxLayout()

        self.input_field = ChatInputArea()
        self.input_field.submit_request.connect(self.send_message)

        input_layout.addWidget(self.input_field)

        # Кнопка відправити
        self.btn_send = QPushButton("➤")
        self.btn_send.setFixedSize(40, 40)
        self.btn_send.setCursor(Qt.PointingHandCursor)
        self.btn_send.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 20px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.btn_send.clicked.connect(self.send_message)

        # Вирівнювання кнопки по низу (щоб була на рівні останнього рядка вводу)
        input_layout.addWidget(self.btn_send, 0, Qt.AlignBottom)

        layout.addLayout(input_layout)

        # 4. Кнопка "Додати" (З'являється в кінці)
        self.btn_add = QPushButton("✅ Додати Ціль")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setEnabled(False)  # Спочатку вимкнена
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
            QPushButton:hover:!disabled { background-color: #2ecc71; }
        """)
        self.btn_add.clicked.connect(self.finalize_goal)
        layout.addWidget(self.btn_add)

    def start_chat(self):
        """Ініціалізація сесії."""
        try:
            self.chat_session = self.ai_service.start_goal_chat()
            self.append_message("AI", "Привіт! Я твій помічник з планування. Опиши, чого ти хочеш досягти? 🎯")
        except Exception as e:
            self.append_message("System", f"Помилка запуску AI: {e}")
            self.input_field.setEnabled(False)

    def send_message(self):
        # Отримуємо текст через toPlainText() замість text()
        text = self.input_field.toPlainText().strip()
        if not text: return

        self.append_message("Ви", text)
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.btn_send.setEnabled(False)
        self.loading_bar.show()

        # Запускаємо в окремому потоці
        self.worker = AIChatWorker(self.ai_service, self.chat_session, text)
        self.worker.response_received.connect(self.on_ai_response)
        self.worker.start()

    def on_ai_response(self, text, json_data):
        self.loading_bar.hide()
        self.input_field.setEnabled(True)
        self.btn_send.setEnabled(True)
        self.input_field.setFocus()

        # Якщо AI надіслав просто текст
        if not json_data:
            self.append_message("AI", text)
        else:
            # Якщо AI надіслав JSON (ціль сформована)
            self.generated_goal_data = json_data

            # Формуємо красиве повідомлення про успіх
            summary = (
                f"🎉 <b>План готовий!</b><br><br>"
                f"<b>Назва:</b> {json_data.get('title')}<br>"
                f"<b>Складність:</b> {json_data.get('difficulty')}<br>"
                f"<b>Дедлайн через:</b> {json_data.get('deadline_days')} днів<br>"
                f"<b>Підцілей:</b> {len(json_data.get('subgoals', []))}<br><br>"
                f"Натисніть <b>'Додати Ціль'</b>, щоб зберегти."
            )
            self.chat_area.append(summary)
            self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

            self.btn_add.setEnabled(True)
            self.btn_add.setText(f"✅ Додати: {json_data.get('title')}")
            self.input_field.setPlaceholderText("Ціль сформована. Натисніть Додати.")
            self.input_field.setEnabled(False)

    def append_message(self, sender, text):
        color = "#3498db" if sender == "AI" else "#2ecc71"
        align = "left" if sender == "AI" else "right"

        # Просте форматування HTML
        formatted_text = text.replace("\n", "<br>")

        msg_html = f"""
        <div style='text-align: {align}; margin-bottom: 10px;'>
            <span style='color: {color}; font-weight: bold;'>{sender}:</span><br>
            <span style='font-size: 13px;'>{formatted_text}</span>
        </div>
        """
        self.chat_area.append(msg_html)
        # Автопрокрутка вниз
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def finalize_goal(self):
        """Створення цілі в системі на основі JSON від AI."""
        if not self.generated_goal_data: return

        try:
            data = self.generated_goal_data

            # 1. Парсинг Difficulty
            diff_str = data.get("difficulty", "EASY").upper()
            difficulty = Difficulty.EASY
            if diff_str == "MEDIUM":
                difficulty = Difficulty.MEDIUM
            elif diff_str == "HARD":
                difficulty = Difficulty.HARD
            elif diff_str == "EPIC":
                difficulty = Difficulty.EPIC

            # 2. Розрахунок дедлайну
            days = int(data.get("deadline_days", 7))
            deadline = datetime.now() + timedelta(days=days)

            # 3. Створення цілі
            new_goal = self.main_service.create_goal(
                title=data.get("title", "Нова ціль"),
                description=data.get("description", ""),
                deadline=deadline,
                difficulty=difficulty
            )

            # 4. Додавання підцілей
            subgoals = data.get("subgoals", [])
            for sub in subgoals:
                new_sub = SubGoal(title=sub.get("title"), description=sub.get("description", ""))
                new_goal.add_subgoal(new_sub)

            # Зберігаємо підцілі
            self.main_service.storage.save_goal(new_goal, self.main_service.hero_id)

            QMessageBox.information(self, "Успіх", "Ціль успішно створена з допомогою AI!")
            self.accept()  # Закриваємо діалог

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити ціль: {e}")