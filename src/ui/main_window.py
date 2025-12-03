import os
import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMessageBox, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

from src.logic import GoalService

# Імпорти діалогів
from src.ui.dialogs import AddGoalDialog
from src.ui.longterm_dialog import AddLongTermDialog
from src.ui.stats_dialog import StatsDialog
from src.ui.inventory_dialog import InventoryDialog
from src.ui.shop_dialog import ShopDialog
from src.ui.subgoals_dialog import SubgoalsDialog
from src.ui.edit_goal_dialog import EditGoalDialog
from src.ui.edit_longterm_dialog import EditLongTermDialog
from src.ui.ai_goal_dialog import AIGoalDialog

# Імпорт панелей та вкладок
from src.ui.hero_panel import HeroPanel
from src.ui.middle_panel import MiddlePanel
from src.ui.enemy_panel import EnemyWidget
from src.ui.tabs.quest_tab import QuestTab
from src.ui.tabs.habit_tab import HabitTab
from src.ui.skills_dialog import SkillsDialog


class MainWindow(QMainWindow):
    logout_signal = pyqtSignal()

    def __init__(self, service: GoalService):
        super().__init__()
        self.service = service
        self.time_offset = timedelta(0)

        self.setWindowTitle("Learning Goals RPG 🛡️")
        self.resize(1000, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.root_layout = QVBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(10, 10, 10, 10)
        self.root_layout.setSpacing(15)

        self.setup_ui()

        self.main_timer = QTimer(self)
        self.main_timer.timeout.connect(self.on_tick)
        self.main_timer.start(1000)

        self.refresh_data()

    def setup_ui(self):
        # 1. ВЕРХНЯ СЕКЦІЯ
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)
        top_layout.setAlignment(Qt.AlignTop)

        self.hero_panel = HeroPanel()
        top_layout.addWidget(self.hero_panel)

        self.middle_panel = MiddlePanel()
        self.middle_panel.stats_clicked.connect(self.open_stats_dialog)
        self.middle_panel.inventory_clicked.connect(self.open_inventory)
        self.middle_panel.shop_clicked.connect(self.open_shop)
        self.middle_panel.logout_clicked.connect(self.on_logout)
        self.middle_panel.debug_time_clicked.connect(self.on_debug_add_time)
        top_layout.addWidget(self.middle_panel)

        self.enemy_widget = EnemyWidget()
        top_layout.addWidget(self.enemy_widget)

        self.root_layout.addWidget(top_container)

        # 2. НИЖНЯ СЕКЦІЯ (ТАБИ)
        self.tabs = QTabWidget()

        # Використовуємо нові класи вкладок
        self.quest_tab = QuestTab(self.tabs, self)
        self.tabs.addTab(self.quest_tab, "⚔️ Квести")

        self.habit_tab = HabitTab(self.tabs, self)
        self.tabs.addTab(self.habit_tab, "📅 Звички")

        self.root_layout.addWidget(self.tabs)

        # Підключення скілів
        self.middle_panel.skills_clicked.connect(self.open_skills_dialog)
        self.middle_panel.skill_used_signal.connect(self.use_skill)

    # --- LOGIC ---
    def on_debug_add_time(self):
        self.time_offset += timedelta(hours=2)
        self.on_tick()

    def on_tick(self):
        simulated_now = datetime.now() + self.time_offset
        try:
            hero = self.service.get_hero()
            self.middle_panel.update_data(hero, simulated_now)
        except:
            pass

        try:
            alerts_q = self.service.check_deadlines(custom_now=simulated_now)
            _, alerts_h = self.service.get_long_term_goals(custom_now=simulated_now)
            all_alerts = alerts_q + alerts_h

            if all_alerts:
                self.refresh_data()
                QMessageBox.warning(self, "УВАГА!", "\n\n".join(all_alerts))
        except Exception as e:
            print(f"Error checking deadlines: {e}")

    def refresh_data(self):
        try:
            hero = self.service.get_hero()
            enemy = self.service.get_current_enemy()
            simulated_now = datetime.now() + self.time_offset

            self.hero_panel.update_data(hero)
            self.middle_panel.update_data(hero, simulated_now)
            self.enemy_widget.update_enemy(enemy)
        except ValueError:
            pass

        # Оновлюємо списки через методи вкладок
        if hasattr(self, 'quest_tab'):
            self.quest_tab.update_list()
        if hasattr(self, 'habit_tab'):
            self.habit_tab.update_list()

    # --- МЕТОДИ КАРТОК И ДЕЙСТВИЙ ---
    # Эти методы остаются в MainWindow, так как они управляют общей логикой приложения

    def on_card_subgoal_checked(self, goal, subgoal, is_checked):
        subgoal.is_completed = is_checked
        self.service.storage.save_goal(goal, self.service.hero_id)

        if is_checked:
            if not goal.is_completed and goal.subgoals and all(s.is_completed for s in goal.subgoals):
                msg = self.service.complete_goal(goal)
                QMessageBox.information(self, "Квест виконано!", f"Всі підцілі завершено!\n{msg}")
        else:
            if goal.is_completed:
                msg = self.service.undo_complete_goal(goal)
                QMessageBox.warning(self, "Відміна виконання", f"Ціль повернута до активних.\n{msg}")

        self.refresh_data()

    def on_add_goal(self):
        if AddGoalDialog(self, self.service).exec_(): self.refresh_data()

    def on_add_longterm(self):
        if AddLongTermDialog(self, self.service).exec_(): self.refresh_data()

    def on_ai_goal_dialog(self):
        if AIGoalDialog(self, self.service).exec_():
            self.refresh_data()

    def on_auto_delete_completed(self):
        goals = self.service.get_all_goals()
        completed = [g for g in goals if g.is_completed]

        if not completed:
            QMessageBox.information(self, "Інфо", "Немає виконаних квестів для видалення.")
            return

        reply = QMessageBox.question(
            self, 'Автовидалення',
            f"Ви впевнені, що хочете видалити {len(completed)} виконаних квестів?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                for g in completed:
                    self.service.delete_goal(g.id)
                self.refresh_data()
                QMessageBox.information(self, "Успіх", "Виконані квести видалено.")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити:\n{str(e)}")

    def complete_goal(self, goal):
        try:
            msg = self.service.complete_goal(goal)
            QMessageBox.information(self, "Результат", msg)
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося завершити квест:\n{str(e)}")

    def delete_goal(self, goal):
        try:
            reply = QMessageBox.question(self, 'Видалити?', f"Видалити '{goal.title}'?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.service.delete_goal(goal.id)
                self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося видалити:\n{str(e)}")

    def delete_habit(self, goal):
        try:
            reply = QMessageBox.question(self, 'Видалити?', f"Видалити звичку '{goal.title}'?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.service.delete_long_term_goal(goal.id)
                self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося видалити звичку:\n{str(e)}")

    def edit_goal(self, goal):
        if EditGoalDialog(self, self.service, goal).exec_():
            self.refresh_data()

    def manage_subgoals(self, goal):
        if SubgoalsDialog(self, self.service, goal).exec_():
            self.refresh_data()

    def edit_habit(self, goal):
        if EditLongTermDialog(self, self.service, goal).exec_():
            self.refresh_data()

    def start_habit(self, goal):
        try:
            simulated_now = datetime.now() + self.time_offset
            self.service.start_habit(goal, custom_now=simulated_now)
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка старту:\n{str(e)}")

    def finish_habit(self, goal):
        try:
            simulated_now = datetime.now() + self.time_offset
            msg = self.service.finish_habit(goal, custom_now=simulated_now)
            QMessageBox.information(self, "Результат", msg)
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка завершення:\n{str(e)}")

    def open_skills_dialog(self):
        try:
            SkillsDialog(self, self.service).exec_()
        except Exception as e:
            print(e)

    def use_skill(self, skill_id):
        try:
            msg = self.service.use_skill(skill_id)
            self.refresh_data()
            QMessageBox.information(self, "Навичка", msg)
        except ValueError as e:
            QMessageBox.warning(self, "Неможливо", str(e))
        except Exception as e:
            print(f"Skill Error: {e}")

    def open_stats_dialog(self):
        try:
            StatsDialog(self, self.service).exec_()
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити характеристики:\n{str(e)}")

    def open_inventory(self):
        try:
            InventoryDialog(self, self.service).exec_()
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити інвентар:\n{str(e)}")

    def open_shop(self):
        try:
            ShopDialog(self, self.service).exec_()
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити магазин:\n{str(e)}")

    def on_logout(self):
        reply = QMessageBox.question(self, 'Вихід', "Вийти з акаунту?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logout_signal.emit()
            self.close()