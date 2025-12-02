from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QDateTimeEdit, QPushButton, QHBoxLayout, QMessageBox,
    QListWidget, QListWidgetItem, QCheckBox, QInputDialog
)
from PyQt5.QtCore import QDateTime, Qt
from src.models import Difficulty, SubGoal
from src.logic import GoalService


class AddGoalDialog(QDialog):
    def __init__(self, parent, service: GoalService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Новий Квест ⚔️")
        self.resize(400, 450)

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
        self.date_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.layout.addWidget(self.date_input)

        # 4. Складність
        self.layout.addWidget(QLabel("Складність:"))
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
        deadline = self.date_input.dateTime().toPyDateTime().replace(second=0, microsecond=0)
        difficulty = self.diff_input.currentData()

        if not title:
            QMessageBox.warning(self, "Помилка", "Введіть назву!")
            return

        try:
            self.service.create_goal(title, desc, deadline, difficulty)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))


class EditGoalDialog(AddGoalDialog):
    """Діалог редагування квесту. Наслідується від AddGoalDialog."""

    def __init__(self, parent, service: GoalService, goal):
        super().__init__(parent, service)
        self.goal = goal
        self.setWindowTitle("Редагувати Квест ✏️")

        self.title_input.setText(goal.title)
        self.desc_input.setText(goal.description)
        self.date_input.setDateTime(QDateTime(goal.deadline))

        index = self.diff_input.findData(goal.difficulty)
        if index >= 0:
            self.diff_input.setCurrentIndex(index)

        btn_layout_item = self.layout.itemAt(self.layout.count() - 1)
        if btn_layout_item:
            btn_save = btn_layout_item.layout().itemAt(0).widget()
            btn_save.setText("Зберегти")

    def save_goal(self):
        title = self.title_input.text()
        desc = self.desc_input.toPlainText()
        deadline = self.date_input.dateTime().toPyDateTime().replace(second=0, microsecond=0)
        difficulty = self.diff_input.currentData()

        if not title:
            QMessageBox.warning(self, "Помилка", "Введіть назву!")
            return

        self.goal.title = title
        self.goal.description = desc
        self.goal.deadline = deadline
        self.goal.difficulty = difficulty

        try:
            self.service.storage.save_goal(self.goal, self.service.hero_id)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))


class SubgoalsDialog(QDialog):
    """Діалог управління підцілями з автовиконанням батьківської цілі."""

    def __init__(self, parent, service: GoalService, goal):
        super().__init__(parent)
        self.service = service
        self.goal = goal
        self.setWindowTitle(f"Підцілі: {goal.title}")
        self.resize(400, 500)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Список підцілей:"))

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.update_list()

        btn_box = QHBoxLayout()
        btn_add = QPushButton("➕ Додати")
        btn_add.clicked.connect(self.add_subgoal)
        btn_box.addWidget(btn_add)

        btn_edit = QPushButton("✏️ Ред.")
        btn_edit.clicked.connect(self.edit_subgoal)
        btn_box.addWidget(btn_edit)

        btn_del = QPushButton("❌ Видалити")
        btn_del.clicked.connect(self.delete_subgoal)
        btn_box.addWidget(btn_del)

        layout.addLayout(btn_box)

        btn_close = QPushButton("Закрити")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def update_list(self):
        self.list_widget.clear()
        for sub in self.goal.subgoals:
            item = QListWidgetItem()
            widget = QCheckBox(sub.title)
            widget.setChecked(sub.is_completed)
            widget.stateChanged.connect(lambda state, s=sub: self.toggle_subgoal(s, state))
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def toggle_subgoal(self, subgoal, state):
        subgoal.is_completed = (state == Qt.Checked)

        # --- АВТОВИКОНАННЯ ЦІЛІ ---
        # Перевіряємо, чи є підцілі і чи всі вони виконані
        if self.goal.subgoals and all(s.is_completed for s in self.goal.subgoals):
            if not self.goal.is_completed:
                # Якщо ціль ще не завершена, ставимо прапорець.
                # УВАГА: Це лише змінює стан. Нагороду нарахує метод complete_goal у сервісі,
                # якщо користувач натисне "Завершити" або ми викличемо це програмно.
                # Тут ми поки що просто зберігаємо статус "Виконано" для візуалізації.
                # Для повного завершення (з нагородами) краще залишити кнопку,
                # але якщо ви хочете автоматично - можна додати виклик self.service.complete_goal(self.goal)
                # Але це небезпечно робити тут без оновлення GUI батьківського вікна.
                # Тому поки що просто змінюємо статус, а кнопку "Завершити" можна буде натиснути.
                pass
                # Варіант користувача: "автовиконання".
                # Якщо ми хочемо щоб воно ставало зеленим (is_completed=True), робимо це:
                self.goal.is_completed = True

        # Зберігаємо
        self.service.storage.save_goal(self.goal, self.service.hero_id)

    def add_subgoal(self):
        text, ok = QInputDialog.getText(self, "Нова підціль", "Введіть назву підцілі:")
        if ok and text:
            new_sub = SubGoal(title=text)
            self.goal.add_subgoal(new_sub)
            self.goal.is_completed = False  # Скидаємо виконання при додаванні нової
            self.service.storage.save_goal(self.goal, self.service.hero_id)
            self.update_list()

    def edit_subgoal(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть підціль для редагування")
            return

        sub = self.goal.subgoals[row]
        text, ok = QInputDialog.getText(self, "Редагувати", "Нова назва:", text=sub.title)
        if ok and text:
            sub.title = text
            self.service.storage.save_goal(self.goal, self.service.hero_id)
            self.update_list()

    def delete_subgoal(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть підціль для видалення")
            return

        del self.goal.subgoals[row]
        self.service.storage.save_goal(self.goal, self.service.hero_id)
        self.update_list()