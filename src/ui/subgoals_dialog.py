from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QCheckBox, QHBoxLayout, QPushButton, QInputDialog, QMessageBox,
    QLineEdit, QTextEdit, QAbstractItemView, QWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from src.models import SubGoal
from src.logic import GoalService
from src.logic.ai_service import AIService


class AIWorker(QThread):
    """Потік для виконання запиту до AI без зависання інтерфейсу."""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, goal_title, goal_desc, difficulty):
        super().__init__()
        self.goal_title = goal_title
        self.goal_desc = goal_desc
        self.difficulty = difficulty

    def run(self):
        try:
            service = AIService()
            # Передаємо складність у сервіс
            subgoals = service.generate_subgoals(self.goal_title, self.goal_desc, self.difficulty)
            self.finished.emit(subgoals)
        except Exception as e:
            self.error.emit(str(e))


class SubGoalInputDialog(QDialog):
    """Кастомний діалог для додавання/редагування підцілі (Назва + Опис)."""

    def __init__(self, parent=None, title_text="", desc_text=""):
        super().__init__(parent)
        self.setWindowTitle("Підціль")
        self.resize(500, 400)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        # Назва
        self.layout.addWidget(QLabel("Назва:"))
        self.title_input = QLineEdit(title_text)
        self.title_input.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        self.layout.addWidget(self.title_input)

        # Опис
        self.layout.addWidget(QLabel("Опис (опціонально):"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlainText(desc_text)
        self.desc_input.setStyleSheet("font-size: 12px; padding: 5px;")
        self.layout.addWidget(self.desc_input)

        # Кнопки
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("Зберегти")
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        btn_ok.clicked.connect(self.accept)

        btn_cancel = QPushButton("Скасувати")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("background-color: #555; color: white; padding: 8px; border-radius: 4px;")
        btn_cancel.clicked.connect(self.reject)

        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        self.layout.addLayout(btn_box)

    def get_data(self):
        return self.title_input.text(), self.desc_input.toPlainText()


class SubGoalItemWidget(QWidget):
    """
    Кастомний віджет для елемента списку.
    """

    def __init__(self, item, list_widget, subgoal, on_toggle):
        super().__init__()
        self.item = item
        self.list_widget = list_widget
        self.subgoal = subgoal
        self.on_toggle = on_toggle

        # Основний вертикальний лейаут
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        # Рядок 1: Чекбокс + Назва
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        self.cb = QCheckBox()
        self.cb.setChecked(subgoal.is_completed)
        self.cb.setFixedWidth(20)
        self.cb.stateChanged.connect(self._cb_changed)

        self.title_lbl = QLabel(subgoal.title)
        self.title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        self.title_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)

        row1.addWidget(self.cb)
        row1.addWidget(self.title_lbl)
        row1.addStretch()

        layout.addLayout(row1)

        # Рядок 2: Опис
        if subgoal.description:
            self.desc_lbl = QLabel(subgoal.description)
            self.desc_lbl.setWordWrap(True)
            self.desc_lbl.setStyleSheet("font-size: 12px; color: #aaaaaa; margin-left: 30px;")
            self.desc_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
            layout.addWidget(self.desc_lbl)

    def _cb_changed(self, state):
        self.on_toggle(self.subgoal, state)

    def mousePressEvent(self, event):
        modifiers = event.modifiers()
        if modifiers & Qt.ControlModifier:
            self.item.setSelected(not self.item.isSelected())
        else:
            self.list_widget.clearSelection()
            self.item.setSelected(True)
        self.list_widget.setFocus()
        super().mousePressEvent(event)


class SubgoalsDialog(QDialog):
    """Діалог управління підцілями з автовиконанням батьківської цілі."""

    def __init__(self, parent, service: GoalService, goal):
        super().__init__(parent)
        self.service = service
        self.goal = goal
        self.setWindowTitle(f"Підцілі: {goal.title}")

        self.resize(700, 700)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        lbl_header = QLabel("Список підцілей:")
        lbl_header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        layout.addWidget(lbl_header)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                color: white;
            }
            QListWidget::item {
                border-bottom: 1px solid #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #444;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.list_widget)

        self.update_list()

        # Кнопки управління
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        base_btn_style = """
            QPushButton { 
                border-radius: 4px; 
                padding: 8px 12px; 
                font-weight: bold; 
                color: white;
            }
        """

        # Додати - Зелена
        btn_add = QPushButton("➕ Додати")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet(base_btn_style + """
            QPushButton { background-color: #27ae60; }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_add.clicked.connect(self.add_subgoal)
        btn_box.addWidget(btn_add)

        # AI - Синя
        self.btn_ai = QPushButton("🤖 AI генерація")
        self.btn_ai.setCursor(Qt.PointingHandCursor)
        self.btn_ai.setStyleSheet(base_btn_style + """
            QPushButton { background-color: #3498db; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.btn_ai.clicked.connect(self.on_ai_add)
        btn_box.addWidget(self.btn_ai)

        # Редагувати - Жовта
        btn_edit = QPushButton("✏️ Редагувати")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet(base_btn_style + """
            QPushButton { background-color: #f1c40f; color: #2c3e50; }
            QPushButton:hover { background-color: #f39c12; }
        """)
        btn_edit.clicked.connect(self.edit_subgoal)
        btn_box.addWidget(btn_edit)

        # Видалити - Червона
        btn_del = QPushButton("❌ Видалити")
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setStyleSheet(base_btn_style + """
            QPushButton { background-color: #c0392b; }
            QPushButton:hover { background-color: #e74c3c; }
        """)
        btn_del.clicked.connect(self.delete_subgoal)
        btn_box.addWidget(btn_del)

        layout.addLayout(btn_box)

        # Закрити
        btn_close = QPushButton("Закрити")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton { 
                background-color: #555; 
                color: white; 
                border-radius: 4px; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover { background-color: #666; }
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def on_ai_add(self):
        """Запуск AI генерації."""
        self.btn_ai.setEnabled(False)
        self.btn_ai.setText("⏳ Думаю...")

        # Передаємо title, description та difficulty
        self.ai_worker = AIWorker(self.goal.title, self.goal.description, self.goal.difficulty)
        self.ai_worker.finished.connect(self.on_ai_success)
        self.ai_worker.error.connect(self.on_ai_error)
        self.ai_worker.start()

    def on_ai_success(self, subgoals_data):
        """AI успішно повернув дані."""
        self.btn_ai.setEnabled(True)
        self.btn_ai.setText("🤖 AI генерація")

        if not subgoals_data:
            QMessageBox.information(self, "AI", "AI не зміг придумати підцілі.")
            return

        count = len(subgoals_data)
        reply = QMessageBox.question(
            self, "AI Пропозиція",
            f"AI пропонує додати {count} підцілей.\nДодати їх до списку?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            for item in subgoals_data:
                new_sub = SubGoal(title=item.get('title', 'Без назви'), description=item.get('description', ''))
                self.goal.add_subgoal(new_sub)

            self.goal.is_completed = False
            self.service.storage.save_goal(self.goal, self.service.hero_id)
            self.update_list()
            QMessageBox.information(self, "Успіх", "Підцілі успішно додано!")

    def on_ai_error(self, error_msg):
        """Помилка AI."""
        self.btn_ai.setEnabled(True)
        self.btn_ai.setText("🤖 AI генерація")
        QMessageBox.critical(self, "Помилка AI", f"Щось пішло не так:\n{error_msg}\n\nПеревірте API ключ в .env файлі.")

    def update_list(self):
        self.list_widget.clear()
        for sub in self.goal.subgoals:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, sub)
            widget = SubGoalItemWidget(item, self.list_widget, sub, self.toggle_subgoal)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def toggle_subgoal(self, subgoal, state):
        subgoal.is_completed = (state == Qt.Checked)
        if self.goal.subgoals and all(s.is_completed for s in self.goal.subgoals):
            if not self.goal.is_completed:
                self.goal.is_completed = True
        self.service.storage.save_goal(self.goal, self.service.hero_id)

    def add_subgoal(self):
        dialog = SubGoalInputDialog(self)
        if dialog.exec_():
            title, desc = dialog.get_data()
            if title:
                new_sub = SubGoal(title=title, description=desc)
                self.goal.add_subgoal(new_sub)
                self.goal.is_completed = False
                self.service.storage.save_goal(self.goal, self.service.hero_id)
                self.update_list()

    def edit_subgoal(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Увага", "Оберіть підціль для редагування")
            return
        if len(selected_items) > 1:
            QMessageBox.warning(self, "Увага", "Редагування можливе лише по одній підцілі.")
            return

        item = selected_items[0]
        sub = item.data(Qt.UserRole)

        dialog = SubGoalInputDialog(self, title_text=sub.title, desc_text=sub.description)
        if dialog.exec_():
            title, desc = dialog.get_data()
            if title:
                sub.title = title
                sub.description = desc
                self.service.storage.save_goal(self.goal, self.service.hero_id)
                self.update_list()

    def delete_subgoal(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Увага", "Оберіть підціль(лі) для видалення")
            return

        count = len(selected_items)
        msg = f"Видалити {count} підціль?" if count == 1 else f"Видалити {count} підцілей?"
        reply = QMessageBox.question(self, "Видалити", msg, QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            subs_to_delete = [item.data(Qt.UserRole) for item in selected_items]
            for sub in subs_to_delete:
                if sub in self.goal.subgoals:
                    self.goal.subgoals.remove(sub)
            self.service.storage.save_goal(self.goal, self.service.hero_id)
            self.update_list()