from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDateTime
from src.ui.dialogs import AddGoalDialog
from src.logic import GoalService


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