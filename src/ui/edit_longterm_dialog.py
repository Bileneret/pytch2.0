from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTime
from src.ui.longterm_dialog import AddLongTermDialog
from src.logic import GoalService


class EditLongTermDialog(AddLongTermDialog):
    """Діалог редагування звички."""

    def __init__(self, parent, service: GoalService, goal):
        super().__init__(parent, service)
        self.goal = goal
        self.setWindowTitle("Редагувати Звичку 📅")

        # Заповнюємо даними
        self.title_input.setText(goal.title)
        self.days_input.setValue(goal.total_days)
        self.days_input.setDisabled(True)  # Не можна міняти тривалість

        self.desc_input.setText(goal.description)

        try:
            times = goal.time_frame.split(" - ")
            if len(times) == 2:
                self.start_time.setTime(QTime.fromString(times[0], "HH:mm"))
                self.end_time.setTime(QTime.fromString(times[1], "HH:mm"))
        except:
            pass

        self.lbl_warning.setVisible(False)
        self.btn_save.setText("Зберегти Зміни")

    def save_goal(self):
        title = self.title_input.text()
        desc = self.desc_input.toPlainText()

        t_start = self.start_time.time().toString("HH:mm")
        t_end = self.end_time.time().toString("HH:mm")
        time_frame = f"{t_start} - {t_end}"

        if not title:
            QMessageBox.warning(self, "Помилка", "Введіть назву!")
            return

        self.goal.title = title
        self.goal.description = desc
        self.goal.time_frame = time_frame

        try:
            self.service.storage.save_long_term_goal(self.goal, self.service.hero_id)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося оновити:\n{str(e)}")