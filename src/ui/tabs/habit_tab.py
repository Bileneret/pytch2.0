from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from .base_tab import BaseTab
from src.ui.cards import HabitCard
from datetime import datetime

class HabitTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.mw = main_window
        self.sort_combo = None
        self.setup_ui()

    def setup_ui(self):
        self.sort_combo = self.create_tab_controls(
            btn_text="📅 Нова Звичка",
            btn_command=self.mw.on_add_longterm,
            refresh_command=self.mw.refresh_data,
            sort_items=["Дата старту (нові)", "Дата старту (старі)", "Прогрес (більше)", "Прогрес (менше)", "Тривалість (довгі)"],
            on_sort_change=self.update_list,
            add_cleanup=False,
            add_search=False
        )
        self.create_scroll_area()

    def update_list(self):
        """Обновляет список привычек."""
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        simulated_now = datetime.now() + self.mw.time_offset
        try:
            lt_goals, _ = self.mw.service.get_long_term_goals(custom_now=simulated_now)

            if self.sort_combo:
                mode = self.sort_combo.currentText()
                if "Дата старту (нові)" in mode:
                    lt_goals.sort(key=lambda x: (x.is_completed, x.start_date), reverse=True)
                elif "Дата старту (старі)" in mode:
                    lt_goals.sort(key=lambda x: (x.is_completed, x.start_date))
                elif "Прогрес (більше)" in mode:
                    lt_goals.sort(key=lambda x: (x.is_completed, -x.calculate_progress()))
                elif "Прогрес (менше)" in mode:
                    lt_goals.sort(key=lambda x: (x.is_completed, x.calculate_progress()))
                elif "Тривалість (довгі)" in mode:
                    lt_goals.sort(key=lambda x: (x.is_completed, -x.total_days))

            if not lt_goals:
                self.list_layout.addWidget(
                    QLabel("Немає активних звичок.", styleSheet="color: #7f8c8d; font-size: 14px;",
                           alignment=Qt.AlignCenter))
            else:
                for g in lt_goals:
                    card = HabitCard(
                        g,
                        simulated_now,
                        self.mw.start_habit,
                        self.mw.finish_habit,
                        self.mw.edit_habit,
                        self.mw.delete_habit
                    )
                    self.list_layout.addWidget(card)
        except Exception as e:
            self.list_layout.addWidget(QLabel(f"Помилка: {e}", styleSheet="color: red;"))