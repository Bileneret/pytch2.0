from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from .base_tab import BaseTab
from src.ui.cards import QuestCard
from src.ui.search_dialog import SearchDialog


class QuestTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.mw = main_window  # Ссылка на MainWindow для доступа к методам и данным
        self.sort_combo = None

        # Стан: ID закріпленої цілі (результат пошуку)
        self.pinned_goal_id = None
        # Стан: чи потрібно програти анімацію (тільки 1 раз після пошуку)
        self.should_animate_pin = False

        self.setup_ui()

    def setup_ui(self):
        # Панель управления
        self.sort_combo = self.create_tab_controls(
            btn_text="➕ Новий Квест",
            btn_command=self.mw.on_add_goal,
            refresh_command=self.mw.refresh_data,
            sort_items=["Дедлайн (спочатку старі)", "Дедлайн (спочатку нові)", "Пріоритет (Складність)", "Прогрес",
                        "Дата створення"],
            on_sort_change=self.on_sort_change,  # Викликаємо власний метод обробки
            add_cleanup=True,
            cleanup_command=self.mw.on_auto_delete_completed,
            add_ai_btn=True,
            ai_command=self.mw.on_ai_goal_dialog,
            add_search=True,
            search_command=self.open_search
        )

        # Область прокрутки
        self.create_scroll_area()

    def on_sort_change(self):
        """При зміні сортування скидаємо закріплення."""
        self.pinned_goal_id = None
        self.update_list()

    def open_search(self):
        """Открывает диалог поиска."""
        goals = self.mw.service.get_all_goals()
        dialog = SearchDialog(self, goals)

        if dialog.exec_():
            selected_goal = dialog.selected_goal
            if selected_goal:
                # Зберігаємо ID цілі, щоб вона була зверху навіть після оновлення
                self.pinned_goal_id = selected_goal.id
                self.should_animate_pin = True
                self.update_list()

    def update_list(self):
        """
        Обновляет список квестов.
        Використовує self.pinned_goal_id для утримання цілі зверху.
        """
        # Очистка текущего списка
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        try:
            # Получаем данные через main_window -> service
            goals = self.mw.service.get_all_goals()

            # 1. Сортировка по умолчанию или по выбору
            if self.sort_combo:
                mode = self.sort_combo.currentText()
                if "Дедлайн (спочатку старі)" in mode:
                    goals.sort(key=lambda x: (x.is_completed, x.deadline))
                elif "Дедлайн (спочатку нові)" in mode:
                    goals.sort(key=lambda x: (x.is_completed, x.deadline), reverse=True)
                elif "Пріоритет" in mode:
                    goals.sort(key=lambda x: (x.is_completed, -x.difficulty.value))
                elif "Прогрес" in mode:
                    goals.sort(key=lambda x: (x.is_completed, -x.calculate_progress()))
                elif "Дата створення" in mode:
                    goals.sort(key=lambda x: (x.is_completed, x.created_at), reverse=True)
            else:
                goals.sort(key=lambda x: (x.is_completed, x.deadline))

            # 2. Якщо є закріплена ціль, переміщуємо її на початок
            target_card = None

            if self.pinned_goal_id:
                # Шукаємо ціль у списку
                pinned_goal = next((g for g in goals if g.id == self.pinned_goal_id), None)
                if pinned_goal:
                    goals.remove(pinned_goal)
                    goals.insert(0, pinned_goal)  # Вставляємо на 1 місце
                else:
                    # Якщо ціль видалили або не знайшли
                    self.pinned_goal_id = None

            # 3. Отображение
            if not goals:
                self.list_layout.addWidget(
                    QLabel("Немає активних квестів.", styleSheet="color: #7f8c8d; font-size: 14px;",
                           alignment=Qt.AlignCenter))
            else:
                for g in goals:
                    card = QuestCard(
                        g,
                        self.mw.complete_goal,
                        self.mw.delete_goal,
                        self.mw.edit_goal,
                        self.mw.manage_subgoals,
                        self.mw.on_card_subgoal_checked
                    )
                    self.list_layout.addWidget(card)

                    # Перевіряємо, чи це наша закріплена ціль
                    if self.pinned_goal_id and g.id == self.pinned_goal_id:
                        target_card = card

            # 4. Анімація (тільки якщо це результат пошуку, а не просто оновлення галочки)
            if target_card and self.should_animate_pin:
                target_card.play_highlight_animation()
                self.should_animate_pin = False  # Більше не анімуємо при наступних оновленнях

        except Exception as e:
            self.list_layout.addWidget(QLabel(f"Помилка: {e}", styleSheet="color: red;"))