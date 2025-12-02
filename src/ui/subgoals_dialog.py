from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QCheckBox, QHBoxLayout, QPushButton, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from src.models import SubGoal
from src.logic import GoalService


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
        if self.goal.subgoals and all(s.is_completed for s in self.goal.subgoals):
            if not self.goal.is_completed:
                self.goal.is_completed = True
                # Якщо потрібно нарахувати нагороду одразу, можна викликати logic.complete_goal,
                # але безпечніше просто змінити статус, щоб користувач побачив зелену картку.

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