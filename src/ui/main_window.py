import os
import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QMessageBox, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

from src.logic import GoalService
from src.models import Goal, Difficulty, LongTermGoal
from src.ui.dialogs import AddGoalDialog
from src.ui.longterm_dialog import AddLongTermDialog
from src.ui.stats_dialog import StatsDialog
from src.ui.inventory_dialog import InventoryDialog
from src.ui.shop_dialog import ShopDialog

# Імпорт панелей
from src.ui.hero_panel import HeroPanel
from src.ui.middle_panel import MiddlePanel
from src.ui.enemy_panel import EnemyWidget
from src.ui.cards import QuestCard, HabitCard

from src.ui.skills_dialog import SkillsDialog


class MainWindow(QMainWindow):
    logout_signal = pyqtSignal()

    def __init__(self, service: GoalService):
        super().__init__()
        self.service = service
        self.time_offset = timedelta(0)

        self.setWindowTitle("Learning Goals RPG 🛡️")
        self.resize(1000, 800)
        # Видалено світлий фон, тепер працює глобальний стиль
        # self.setStyleSheet("background-color: #f0f2f5;")

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

        # 2. НИЖНЯ СЕКЦІЯ
        self.tabs = QTabWidget()
        # Видалено локальні стилі вкладок, тепер вони беруться з style.qss

        self.tab_quests = QWidget()
        l1 = QVBoxLayout(self.tab_quests)
        l1.setContentsMargins(0, 10, 0, 0)
        self.create_tab_controls(l1, "➕ Новий Квест", self.on_add_goal)
        self.quest_list_layout = self.create_scroll_area(l1)
        self.tabs.addTab(self.tab_quests, "⚔️ Квести")

        self.tab_longterm = QWidget()
        l2 = QVBoxLayout(self.tab_longterm)
        l2.setContentsMargins(0, 10, 0, 0)
        self.create_tab_controls(l2, "📅 Нова Звичка", self.on_add_longterm)
        self.longterm_list_layout = self.create_scroll_area(l2)
        self.tabs.addTab(self.tab_longterm, "📅 Звички")

        self.root_layout.addWidget(self.tabs)

        self.middle_panel.skills_clicked.connect(self.open_skills_dialog)  # Підключення вікна
        self.middle_panel.skill_used_signal.connect(self.use_skill)  # Підключення кнопок

    def open_skills_dialog(self):
        try:
            SkillsDialog(self, self.service).exec_()
        except Exception as e:
            print(e)

    def use_skill(self, skill_id):
        """Використання навички з MiddlePanel."""
        try:
            msg = self.service.use_skill(skill_id)
            self.refresh_data()  # Оновити ману/HP/ворога
            QMessageBox.information(self, "Навичка", msg)

        except ValueError as e:
            QMessageBox.warning(self, "Неможливо", str(e))
        except Exception as e:
            print(f"Skill Error: {e}")

    def create_tab_controls(self, layout, btn_text, btn_command):
        box = QHBoxLayout()
        box.setContentsMargins(5, 0, 5, 0)

        btn_add = QPushButton(btn_text)
        btn_add.setCursor(Qt.PointingHandCursor)
        # Зберігаємо стиль кнопок (зелений), як ви просили
        btn_add.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; padding: 10px; font-weight: bold; border-radius: 5px; } QPushButton:hover { background-color: #2ecc71; }")
        btn_add.clicked.connect(btn_command)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setFixedWidth(50)
        # Зберігаємо стиль кнопок (сірий)
        btn_refresh.setStyleSheet(
            "QPushButton { background-color: #95a5a6; color: white; border-radius: 5px; padding: 10px; font-weight: bold; } QPushButton:hover { background-color: #7f8c8d; }")
        btn_refresh.clicked.connect(self.refresh_data)

        box.addWidget(btn_add)
        box.addWidget(btn_refresh)
        layout.addLayout(box)

    def create_scroll_area(self, layout):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        # Прибрано фон, залишено тільки прибирання рамки
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        # Прибрано світлий фон контейнера
        container.setStyleSheet("background: transparent;")

        vbox = QVBoxLayout(container)
        vbox.setAlignment(Qt.AlignTop)
        vbox.setSpacing(12)
        vbox.setContentsMargins(5, 10, 5, 10)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        return vbox

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

        self.update_quest_list()
        self.update_habit_list()

    def update_quest_list(self):
        while self.quest_list_layout.count():
            child = self.quest_list_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        try:
            goals = self.service.get_all_goals()
            goals.sort(key=lambda x: (x.is_completed, x.deadline))

            if not goals:
                self.quest_list_layout.addWidget(
                    QLabel("Немає активних квестів.", styleSheet="color: #7f8c8d; font-size: 14px;",
                           alignment=Qt.AlignCenter))
            else:
                for g in goals:
                    card = QuestCard(g, self.complete_goal, self.delete_goal)
                    self.quest_list_layout.addWidget(card)
        except Exception as e:
            self.quest_list_layout.addWidget(QLabel(f"Помилка: {e}", styleSheet="color: red;"))

    def update_habit_list(self):
        while self.longterm_list_layout.count():
            child = self.longterm_list_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        simulated_now = datetime.now() + self.time_offset
        try:
            lt_goals, _ = self.service.get_long_term_goals(custom_now=simulated_now)

            if not lt_goals:
                self.longterm_list_layout.addWidget(
                    QLabel("Немає активних звичок.", styleSheet="color: #7f8c8d; font-size: 14px;",
                           alignment=Qt.AlignCenter))
            else:
                for g in lt_goals:
                    card = HabitCard(g, simulated_now, self.start_habit, self.finish_habit)
                    self.longterm_list_layout.addWidget(card)
        except Exception as e:
            self.longterm_list_layout.addWidget(QLabel(f"Помилка: {e}", styleSheet="color: red;"))

    # --- ACTIONS ---
    def on_add_goal(self):
        if AddGoalDialog(self, self.service).exec_(): self.refresh_data()

    def on_add_longterm(self):
        if AddLongTermDialog(self, self.service).exec_(): self.refresh_data()

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
        """Відкриває магазин."""
        try:
            ShopDialog(self, self.service).exec_()
            self.refresh_data()  # Оновлюємо золото після покупок
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити магазин:\n{str(e)}")
            print(f"Shop Crash Details: {e}")

    def on_logout(self):
        reply = QMessageBox.question(self, 'Вихід', "Вийти з акаунту?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logout_signal.emit()
            self.close()