## main.py

import sys
import os
from PyQt5.QtWidgets import QApplication

from src.storage import StorageService
from src.logic import GoalService, AuthService
from src.ui.main_window import MainWindow
from src.ui.auth import LoginWindow

# Налаштування шляхів до бази даних
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)


class AppController:
    """
    Головний контролер програми.
    Відповідає за перемикання між вікном входу та головним вікном.
    """

    def __init__(self):
        self.app = QApplication(sys.argv)

        # Налаштування шрифту для всієї програми (опціонально)
        font = self.app.font()
        font.setFamily("Segoe UI")  # Або Arial
        font.setPointSize(9)
        self.app.setFont(font)

        # Ініціалізація сервісів
        self.storage = StorageService(DB_PATH)
        self.auth_service = AuthService(self.storage)

        self.check_auth_and_run()

    def check_auth_and_run(self):
        """Перевіряє сесію при запуску."""
        # 1. Перевіряємо, чи є збережена сесія (хто останній грав)
        user_id = self.auth_service.get_current_user_id()

        if user_id:
            # Якщо є - запускаємо Головне вікно
            self.show_main_window(user_id)
        else:
            # Якщо немає - запускаємо Логін
            self.show_login_window()

    def show_login_window(self):
        self.login_window = LoginWindow(self.auth_service)
        # Коли вхід успішний -> запускаємо main
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()

    def on_login_success(self):
        """Викликається, коли користувач успішно увійшов/зареєструвався."""
        self.login_window.close()
        user_id = self.auth_service.get_current_user_id()
        self.show_main_window(user_id)

    def show_main_window(self, user_id):
        """Створює та показує головне вікно гри."""
        # Створюємо сервіс цілей конкретно для цього користувача
        goal_service = GoalService(self.storage, user_id)

        self.main_window = MainWindow(goal_service)
        # Підключаємо сигнал виходу
        self.main_window.logout_signal.connect(self.on_logout)
        self.main_window.show()

    def on_logout(self):
        """Обробка виходу з акаунту."""
        # Очищаємо сесію
        self.auth_service.logout()
        # Закриваємо головне вікно
        self.main_window.close()
        # Показуємо вікно входу
        self.show_login_window()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    controller = AppController()
    controller.run()



## dialogs.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QDateTimeEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDateTime
from src.models import Difficulty
from src.logic import GoalService


class AddGoalDialog(QDialog):
    def __init__(self, parent, service: GoalService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Новий Квест ⚔️")
        self.resize(400, 400)  # Трохи менше вікно
        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel("Назва квесту:"))
        self.title_input = QLineEdit()
        self.layout.addWidget(self.title_input)

        self.layout.addWidget(QLabel("Опис:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.layout.addWidget(self.desc_input)

        self.layout.addWidget(QLabel("Дедлайн:"))
        self.date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_input.setCalendarPopup(True)
        self.layout.addWidget(self.date_input)

        # Тільки складність
        self.layout.addWidget(QLabel("Складність (Нагорода XP/Gold):"))
        self.diff_input = QComboBox()
        for diff in Difficulty:
            self.diff_input.addItem(f"{diff.name}", diff)
        self.layout.addWidget(self.diff_input)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Створити")
        btn_save.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        btn_save.clicked.connect(self.save_goal)

        btn_cancel = QPushButton("Скасувати")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        self.layout.addLayout(btn_layout)

    def save_goal(self):
        title = self.title_input.text()
        desc = self.desc_input.toPlainText()
        deadline = self.date_input.dateTime().toPyDateTime()
        difficulty = self.diff_input.currentData()

        try:
            self.service.create_goal(title, desc, deadline, difficulty)
            self.accept()
        except Exception as e:  # <--- Ловимо ВСІ помилки
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити квест:\n{str(e)}")


## models.py

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


# --- Enums ---
class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EPIC = 4


class HeroClass(Enum):
    WARRIOR = "Воїн"
    ARCHER = "Лучник"
    MAGE = "Маг"
    ROGUE = "Розбійник"


class Gender(Enum):
    MALE = "Чоловік"
    FEMALE = "Жінка"


class EnemyRarity(Enum):
    EASY = "Легкий"
    MEDIUM = "Середній"
    HARD = "Складний"
    BOSS = "Бос"


# --- Models ---
@dataclass
class Hero:
    nickname: str
    hero_class: HeroClass
    gender: Gender
    appearance: str  # JSON рядок або опис

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    level: int = 1
    current_xp: int = 0
    xp_to_next_level: int = 100
    gold: int = 0
    streak_days: int = 0
    hp: int = 100
    max_hp: int = 100

    # Базова атака (поки немає спорядження)
    base_damage: int = 15

    last_login: datetime = field(default_factory=datetime.now)


@dataclass
class Enemy:
    name: str
    rarity: EnemyRarity
    level: int
    current_hp: int
    max_hp: int
    damage: int  # Урон по герою

    # Нагороди
    reward_xp: int
    reward_gold: int
    drop_chance: float  # Шанс випадіння спорядження (0.0 - 1.0)

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    image_path: str = ""  # Для майбутньої картинки


@dataclass
class SubGoal:
    title: str
    is_completed: bool = False
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def mark_done(self): self.is_completed = True

    def mark_undone(self): self.is_completed = False


@dataclass
class Goal:
    title: str
    description: str
    deadline: datetime
    difficulty: Difficulty = Difficulty.EASY
    created_at: datetime = field(default_factory=datetime.now)
    is_completed: bool = False
    penalty_applied: bool = False
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    subgoals: List[SubGoal] = field(default_factory=list)

    def add_subgoal(self, subgoal: SubGoal):
        self.subgoals.append(subgoal)

    def calculate_progress(self) -> float:
        if not self.subgoals:
            return 100.0 if self.is_completed else 0.0
        completed_count = sum(1 for sg in self.subgoals if sg.is_completed)
        return (completed_count / len(self.subgoals)) * 100.0

    def is_overdue(self) -> bool:
        if self.is_completed:
            return False
        return datetime.now() > self.deadline


@dataclass
class LongTermGoal:
    title: str
    description: str
    total_days: int
    start_date: datetime
    time_frame: str = ""
    current_day: int = 1
    checked_days: int = 0
    missed_days: int = 0
    is_completed: bool = False
    is_failed: bool = False
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    last_checkin: Optional[datetime] = None

    def calculate_progress(self) -> float:
        return (self.current_day / self.total_days) * 100.0


## storage.py

import sqlite3
import uuid
from datetime import datetime
from typing import List, Optional
from .models import Goal, SubGoal, Hero, Difficulty, LongTermGoal, HeroClass, Gender, Enemy, EnemyRarity


class StorageService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        # 1. Таблиця Героїв
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS heroes (
                id TEXT PRIMARY KEY,
                nickname TEXT UNIQUE NOT NULL,
                hero_class TEXT,
                gender TEXT,
                appearance TEXT,
                level INTEGER DEFAULT 1,
                current_xp INTEGER DEFAULT 0,
                xp_to_next_level INTEGER DEFAULT 100,
                gold INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                hp INTEGER DEFAULT 100,
                max_hp INTEGER DEFAULT 100,
                last_login TEXT
            )
        """)

        # 2. Таблиця Звичайних цілей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY,
                hero_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                deadline TEXT,
                difficulty INTEGER,
                created_at TEXT,
                is_completed INTEGER DEFAULT 0,
                penalty_applied INTEGER DEFAULT 0,
                FOREIGN KEY (hero_id) REFERENCES heroes (id) ON DELETE CASCADE
            )
        """)

        # 3. Таблиця Підцілей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sub_goals (
                id TEXT PRIMARY KEY,
                goal_id TEXT NOT NULL,
                title TEXT NOT NULL,
                is_completed INTEGER DEFAULT 0,
                FOREIGN KEY (goal_id) REFERENCES goals (id) ON DELETE CASCADE
            )
        """)

        # 4. Таблиця Довгострокових цілей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_goals (
                id TEXT PRIMARY KEY,
                hero_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                total_days INTEGER,
                start_date TEXT,
                time_frame TEXT,
                current_day INTEGER DEFAULT 1,
                checked_days INTEGER DEFAULT 0,
                missed_days INTEGER DEFAULT 0,
                is_completed INTEGER DEFAULT 0,
                last_checkin TEXT,
                FOREIGN KEY (hero_id) REFERENCES heroes (id) ON DELETE CASCADE
            )
        """)

        # 5. Таблиця Поточних ворогів (ДОДАНО image_path)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS current_enemies (
                hero_id TEXT PRIMARY KEY,
                id TEXT NOT NULL,
                name TEXT,
                rarity TEXT,
                level INTEGER,
                current_hp INTEGER,
                max_hp INTEGER,
                damage INTEGER,
                reward_xp INTEGER,
                reward_gold INTEGER,
                drop_chance REAL,
                image_path TEXT, 
                FOREIGN KEY (hero_id) REFERENCES heroes (id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    # --- Auth & Hero ---
    def create_hero(self, hero: Hero):
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO heroes (id, nickname, hero_class, gender, appearance, level, hp, max_hp, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(hero.id), hero.nickname, hero.hero_class.value, hero.gender.value,
                hero.appearance, hero.level, hero.hp, hero.max_hp, hero.last_login.isoformat()
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Цей нікнейм вже зайнятий!")
        finally:
            conn.close()

    def get_hero_by_nickname(self, nickname: str) -> Optional[Hero]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM heroes WHERE nickname = ?", (nickname,))
        row = cursor.fetchone()
        conn.close()
        return self._map_row_to_hero(row) if row else None

    def get_hero_by_id(self, hero_id: str) -> Optional[Hero]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM heroes WHERE id = ?", (hero_id,))
        self.fetchone = cursor.fetchone()
        row = self.fetchone
        conn.close()
        return self._map_row_to_hero(row) if row else None

    def _map_row_to_hero(self, row) -> Hero:
        return Hero(
            id=uuid.UUID(row[0]),
            nickname=row[1],
            hero_class=HeroClass(row[2]),
            gender=Gender(row[3]),
            appearance=row[4],
            level=row[5], current_xp=row[6], xp_to_next_level=row[7],
            gold=row[8], streak_days=row[9], hp=row[10], max_hp=row[11],
            last_login=datetime.fromisoformat(row[12])
        )

    def update_hero(self, hero: Hero):
        conn = self._get_connection()
        conn.execute("""
            UPDATE heroes SET level=?, current_xp=?, xp_to_next_level=?, gold=?, streak_days=?, hp=?, max_hp=?, last_login=? WHERE id=?
        """, (hero.level, hero.current_xp, hero.xp_to_next_level, hero.gold, hero.streak_days, hero.hp, hero.max_hp,
              hero.last_login.isoformat(), str(hero.id)))
        conn.commit()
        conn.close()

    # --- Goals ---
    def save_goal(self, goal: Goal, hero_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Додано penalty_applied в запит
            cursor.execute("""
                INSERT OR REPLACE INTO goals (id, hero_id, title, description, deadline, difficulty, created_at, is_completed, penalty_applied)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(goal.id), hero_id, goal.title, goal.description,
                goal.deadline.isoformat(), goal.difficulty.value,
                goal.created_at.isoformat(),
                1 if goal.is_completed else 0,
                1 if goal.penalty_applied else 0  # <--- Зберігаємо
            ))
            cursor.execute("DELETE FROM sub_goals WHERE goal_id = ?", (str(goal.id),))
            for sub in goal.subgoals:
                cursor.execute("INSERT INTO sub_goals (id, goal_id, title, is_completed) VALUES (?, ?, ?, ?)",
                               (str(sub.id), str(goal.id), sub.title, 1 if sub.is_completed else 0))
            conn.commit()
        finally:
            conn.close()

    def load_goals(self, hero_id: str) -> List[Goal]:
        conn = self._get_connection()
        cursor = conn.cursor()
        goals_list = []
        # Додано читання penalty_applied
        cursor.execute(
            "SELECT id, title, description, deadline, difficulty, created_at, is_completed, penalty_applied FROM goals WHERE hero_id = ?",
            (hero_id,))
        rows = cursor.fetchall()
        for row in rows:
            # row: 0=id, 1=title, 2=desc, 3=dl, 4=diff, 5=created, 6=is_comp, 7=penalty
            g_id, title, desc, dl_str, diff_val, ca_str, is_comp, is_penalized = row
            goal = Goal(
                title=title, description=desc, deadline=datetime.fromisoformat(dl_str), difficulty=Difficulty(diff_val)
            )
            goal.id = uuid.UUID(g_id)
            goal.created_at = datetime.fromisoformat(ca_str)
            goal.is_completed = bool(is_comp)
            goal.penalty_applied = bool(is_penalized)  # <--- Відновлюємо
            cursor.execute("SELECT id, title, is_completed FROM sub_goals WHERE goal_id = ?", (g_id,))
            for s_row in cursor.fetchall():
                sub = SubGoal(title=s_row[1])
                sub.id = uuid.UUID(s_row[0])
                sub.is_completed = bool(s_row[2])
                goal.add_subgoal(sub)
            goals_list.append(goal)
        conn.close()
        return goals_list

    def delete_goal(self, goal_id: uuid.UUID):
        conn = self._get_connection()
        conn.execute("DELETE FROM goals WHERE id = ?", (str(goal_id),))
        conn.commit()
        conn.close()

    # --- Long Term Goals ---
    def save_long_term_goal(self, goal: LongTermGoal, hero_id: str):
        conn = self._get_connection()
        last_checkin_str = goal.last_checkin.isoformat() if goal.last_checkin else None
        conn.execute("""
            INSERT OR REPLACE INTO long_term_goals 
            (id, hero_id, title, description, total_days, start_date, time_frame, current_day, checked_days, missed_days, is_completed, last_checkin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(goal.id), hero_id, goal.title, goal.description, goal.total_days, goal.start_date.isoformat(),
              goal.time_frame, goal.current_day, goal.checked_days, goal.missed_days, 1 if goal.is_completed else 0,
              last_checkin_str))
        conn.commit()
        conn.close()

    def load_long_term_goals(self, hero_id: str) -> List[LongTermGoal]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM long_term_goals WHERE hero_id = ? AND is_completed = 0", (hero_id,))
        rows = cursor.fetchall()
        goals = []
        for row in rows:
            g = LongTermGoal(
                title=row[2], description=row[3], total_days=row[4],
                start_date=datetime.fromisoformat(row[5]), time_frame=row[6]
            )
            g.id = uuid.UUID(row[0])
            g.current_day = row[7]
            g.checked_days = row[8]
            g.missed_days = row[9]
            g.is_completed = bool(row[10])
            if row[11]: g.last_checkin = datetime.fromisoformat(row[11])
            goals.append(g)
        conn.close()
        return goals

    # --- Enemy Management (ОНОВЛЕНО) ---
    def save_enemy(self, enemy: Enemy, hero_id: str):
        conn = self._get_connection()
        # Додано image_path в INSERT
        conn.execute("""
            INSERT OR REPLACE INTO current_enemies 
            (hero_id, id, name, rarity, level, current_hp, max_hp, damage, reward_xp, reward_gold, drop_chance, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            hero_id, str(enemy.id), enemy.name, enemy.rarity.value, enemy.level,
            enemy.current_hp, enemy.max_hp, enemy.damage, enemy.reward_xp, enemy.reward_gold, enemy.drop_chance,
            enemy.image_path
        ))
        conn.commit()
        conn.close()

    def load_enemy(self, hero_id: str) -> Optional[Enemy]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM current_enemies WHERE hero_id = ?", (hero_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            # Зчитуємо image_path (індекс 11)
            return Enemy(
                id=uuid.UUID(row[1]),
                name=row[2],
                rarity=EnemyRarity(row[3]),
                level=row[4],
                current_hp=row[5],
                max_hp=row[6],
                damage=row[7],
                reward_xp=row[8],
                reward_gold=row[9],
                drop_chance=row[10],
                image_path=row[11] if len(row) > 11 else ""
            )
        return None

    def delete_enemy(self, hero_id: str):
        conn = self._get_connection()
        conn.execute("DELETE FROM current_enemies WHERE hero_id = ?", (hero_id,))
        conn.commit()
        conn.close()


## logic.py

from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import random

from .models import Goal, Hero, Difficulty, LongTermGoal, HeroClass, Gender, Enemy
from .storage import StorageService
from .longterm_mechanics import LongTermManager
from .session import SessionManager
from .enemy_mechanics import EnemyGenerator


class ValidationUtils:
    @staticmethod
    def validate_title(title: str) -> bool:
        return bool(title and title.strip())


class AuthService:
    def __init__(self, storage: StorageService):
        self.storage = storage

    def register(self, nickname: str, h_class: HeroClass, gender: Gender, appearance: str) -> Hero:
        if not nickname: raise ValueError("Введіть нікнейм!")
        hero = Hero(nickname=nickname, hero_class=h_class, gender=gender, appearance=appearance)
        self.storage.create_hero(hero)
        SessionManager.save_session(str(hero.id))
        return hero

    def login(self, nickname: str) -> Hero:
        hero = self.storage.get_hero_by_nickname(nickname)
        if not hero: raise ValueError("Героя з таким нікнеймом не знайдено.")
        SessionManager.save_session(str(hero.id))
        return hero

    def logout(self):
        SessionManager.clear_session()

    def get_current_user_id(self) -> Optional[str]:
        return SessionManager.load_session()


class GoalService:
    def __init__(self, storage: StorageService, hero_id: str):
        self.storage = storage
        self.hero_id = hero_id

    def get_hero(self) -> Hero:
        hero = self.storage.get_hero_by_id(self.hero_id)
        if not hero: raise ValueError("Помилка сесії")
        self._check_streak(hero)
        return hero

    def _check_streak(self, hero: Hero):
        today = datetime.now().date()
        last_login_date = hero.last_login.date()
        if today > last_login_date:
            if today == last_login_date + timedelta(days=1):
                hero.streak_days += 1
            else:
                hero.streak_days = 1
            hero.last_login = datetime.now()
            self.storage.update_hero(hero)

    # --- Enemy Logic ---
    def get_current_enemy(self) -> Enemy:
        enemy = self.storage.load_enemy(self.hero_id)
        if not enemy:
            hero = self.get_hero()
            enemy = EnemyGenerator.generate_enemy(hero)
            self.storage.save_enemy(enemy, self.hero_id)
        return enemy

    def attack_enemy(self, damage: int) -> Tuple[str, bool, Optional[str]]:
        """
        Наносить урон ворогу.
        Повертає: (Повідомлення, Чи вмер ворог, Лут-інфо)
        """
        enemy = self.get_current_enemy()
        enemy.current_hp -= damage

        msg = f"Ви нанесли {damage} урону по {enemy.name}!"
        is_dead = False
        loot_info = None

        if enemy.current_hp <= 0:
            is_dead = True
            hero = self.get_hero()

            # Нагорода
            hero.current_xp += enemy.reward_xp
            hero.gold += enemy.reward_gold
            loot_info = f"Отримано: {enemy.reward_xp} XP, {enemy.reward_gold} монет."

            # Шанс дропу
            if random.random() < enemy.drop_chance:
                loot_info += "\n🎁 Випав предмет спорядження! (В розробці)"

            msg = f"{msg}\n💀 {enemy.name} переможено!\n{loot_info}"

            # Level Up Check
            while hero.current_xp >= hero.xp_to_next_level:
                hero.current_xp -= hero.xp_to_next_level
                hero.level += 1
                hero.xp_to_next_level = int(hero.level * 100 * 1.5)
                hero.hp = hero.max_hp

            self.storage.update_hero(hero)
            self.storage.delete_enemy(self.hero_id)

            # Spawn new
            new_enemy = EnemyGenerator.generate_enemy(hero)
            self.storage.save_enemy(new_enemy, self.hero_id)
            msg += f"\n⚔️ З'явився новий ворог: {new_enemy.name}!"
        else:
            self.storage.save_enemy(enemy, self.hero_id)

        return msg, is_dead, loot_info

    # --- Goals ---
    def create_goal(self, title: str, description: str, deadline: datetime, difficulty: Difficulty) -> Goal:
        if not ValidationUtils.validate_title(title): raise ValueError("Назва не може бути порожньою!")
        new_goal = Goal(title=title.strip(), description=description.strip(), deadline=deadline, difficulty=difficulty)
        self.storage.save_goal(new_goal, self.hero_id)
        return new_goal

    def get_all_goals(self) -> List[Goal]:
        return self.storage.load_goals(self.hero_id)

    def delete_goal(self, goal_id):
        self.storage.delete_goal(goal_id)

    def complete_goal(self, goal: Goal) -> str:
        if goal.is_completed: return "Вже виконано"

        goal.is_completed = True
        self.storage.save_goal(goal, self.hero_id)

        hero = self.get_hero()
        xp_reward, gold_reward = self._calculate_rewards(goal)
        self._add_rewards(hero, xp_reward, gold_reward)

        # Attack Logic
        attack_msg, killed, loot = self.attack_enemy(hero.base_damage)

        return f"Квест завершено!\n+{xp_reward} XP, +{gold_reward} Gold\n{attack_msg}"

    def _calculate_rewards(self, goal: Goal):
        rewards = {Difficulty.EASY: 50, Difficulty.MEDIUM: 100, Difficulty.HARD: 200, Difficulty.EPIC: 500}
        xp = rewards.get(goal.difficulty, 50)
        return xp, xp

    def _add_rewards(self, hero: Hero, xp: int, gold: int):
        hero.current_xp += xp
        hero.gold += gold
        while hero.current_xp >= hero.xp_to_next_level:
            hero.current_xp -= hero.xp_to_next_level
            hero.level += 1
            hero.xp_to_next_level = int(hero.level * 100 * 1.5)
            hero.hp = hero.max_hp
        self.storage.update_hero(hero)

    # --- Long Term Goals ---
    def create_long_term_goal(self, title: str, description: str, total_days: int, time_frame: str):
        if not ValidationUtils.validate_title(title): raise ValueError("Назва не може бути порожньою!")
        quest = LongTermGoal(title=title, description=description, total_days=total_days, start_date=datetime.now(),
                             time_frame=time_frame)
        self.storage.save_long_term_goal(quest, self.hero_id)

    def get_long_term_goals(self) -> List[LongTermGoal]:
        goals = self.storage.load_long_term_goals(self.hero_id)
        today = datetime.now().date()
        for goal in goals:
            days_passed = (today - goal.start_date.date()).days + 1
            target_day = min(days_passed, goal.total_days)
            if target_day > goal.current_day:
                missed = target_day - goal.current_day
                goal.missed_days += missed
                goal.current_day = target_day
                self.storage.save_long_term_goal(goal, self.hero_id)
        return goals

    def checkin_long_term(self, goal: LongTermGoal) -> Tuple[str, bool]:
        today = datetime.now().date()
        if goal.last_checkin and goal.last_checkin.date() == today: return "Сьогодні вже відмічено!", False

        hero = self.get_hero()
        xp, gold = LongTermManager.calculate_interval_reward()
        self._add_rewards(hero, xp, gold)

        goal.checked_days += 1
        goal.last_checkin = datetime.now()
        is_finished = False
        msg = f"Відмічено! +{xp} XP, +{gold} Gold"

        if goal.current_day >= goal.total_days:
            goal.is_completed = True
            is_finished = True
            report, final_xp, final_gold = LongTermManager.finalize_quest(goal, hero)
            self._add_rewards(hero, final_xp, final_gold)
            msg = f"{msg}\n\n🏁 КВЕСТ ЗАВЕРШЕНО!\n{report}"

        self.storage.save_long_term_goal(goal, self.hero_id)
        return msg, is_finished

    def check_deadlines(self) -> List[str]:
        """
        Перевіряє прострочені дедлайни.
        Якщо дедлайн пройшов і штраф ще не був застосований -> ворог атакує.
        Повертає список повідомлень про атаку.
        """
        hero = self.get_hero()
        enemy = self.get_current_enemy()
        goals = self.get_all_goals()

        alerts = []
        damage_taken = False

        now = datetime.now()

        for goal in goals:
            # Умова: Не виконано, Час вийшов, Ще не покарано
            if not goal.is_completed and not goal.penalty_applied and now > goal.deadline:

                # Застосовуємо покарання
                dmg = enemy.damage
                hero.hp -= dmg
                if hero.hp < 0: hero.hp = 0

                goal.penalty_applied = True
                self.storage.save_goal(goal, self.hero_id)
                damage_taken = True

                alerts.append(f"⏰ Дедлайн квесту '{goal.title}' пропущено!\n💥 {enemy.name} наніс {dmg} урону!")

        if damage_taken:
            self.storage.update_hero(hero)

        return alerts



## main_window.py

from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QFrame,
    QScrollArea, QMessageBox, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from src.logic import GoalService
from src.models import Goal, Difficulty, LongTermGoal
from src.ui.dialogs import AddGoalDialog
from src.ui.longterm_dialog import AddLongTermDialog
from src.ui.enemy_panel import EnemyWidget



class MainWindow(QMainWindow):
    # Сигнал для main.py, щоб повідомити про вихід з акаунту
    logout_signal = pyqtSignal()

    def __init__(self, service: GoalService):
        super().__init__()
        self.service = service

        # Налаштування головного вікна
        self.setWindowTitle("Learning Goals RPG 🛡️")
        self.resize(900, 700)  # Трохи ширше для комфортного розміщення ворога
        self.setStyleSheet("background-color: #f0f2f5;")

        # Основний віджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Головний леаут (Горизонтальний: Зліва Гра, Справа Ворог)
        self.root_layout = QHBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(10, 10, 10, 10)
        self.root_layout.setSpacing(10)

        # --- ЛІВА КОЛОНКА (ГЕРОЙ + КВЕСТИ) ---
        self.left_column = QWidget()
        self.left_layout = QVBoxLayout(self.left_column)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(10)

        # 1. Верхня панель героя
        self.create_hero_panel()

        # 2. Вкладки (Tabs) для Квестів та Звичок
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab { 
                background: #dfe6e9; 
                padding: 10px 20px; 
                margin-right: 2px; 
                border-top-left-radius: 4px; 
                border-top-right-radius: 4px; 
                font-weight: bold;
                color: #2d3436;
            }
            QTabBar::tab:selected { 
                background: white; 
                color: #2980b9;
                border-top: 3px solid #3498db; 
            }
        """)
        self.left_layout.addWidget(self.tabs)

        # Вкладка 1: Звичайні квести
        self.tab_quests = QWidget()
        self.quests_layout = QVBoxLayout(self.tab_quests)
        self.quests_layout.setContentsMargins(0, 10, 0, 0)

        self.create_quest_controls(self.quests_layout, self.on_add_goal, "➕ Новий Квест")
        self.quest_list_layout = self.create_scroll_area(self.quests_layout)

        self.tabs.addTab(self.tab_quests, "⚔️ Квести")

        # Вкладка 2: Довгострокові звички
        self.tab_longterm = QWidget()
        self.longterm_layout = QVBoxLayout(self.tab_longterm)
        self.longterm_layout.setContentsMargins(0, 10, 0, 0)

        self.create_quest_controls(self.longterm_layout, self.on_add_longterm, "📅 Нова Звичка")
        self.longterm_list_layout = self.create_scroll_area(self.longterm_layout)

        self.tabs.addTab(self.tab_longterm, "📅 Звички")

        # Додаємо ліву колонку в головний леаут (розтягується на 3 частини)
        self.root_layout.addWidget(self.left_column, stretch=3)

        # --- ПРАВА КОЛОНКА (ВОРОГ) ---
        self.right_column = QVBoxLayout()
        self.right_column.setContentsMargins(5, 0, 5, 0)

        # Віджет ворога
        self.enemy_widget = EnemyWidget()
        self.right_column.addWidget(self.enemy_widget)

        # Пустий простір знизу, щоб ворог був зверху
        self.right_column.addStretch()

        # Додаємо праву колонку (розтягується на 1 частину)
        self.root_layout.addLayout(self.right_column, stretch=1)

        # Завантаження даних при старті
        self.refresh_data()

    def create_hero_panel(self):
        """Створення панелі з інформацією про героя та кнопкою виходу."""
        self.hero_frame = QFrame()
        self.hero_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50; 
                border-radius: 8px;
                border: 1px solid #34495e;
            }
        """)
        hero_layout = QHBoxLayout(self.hero_frame)
        hero_layout.setContentsMargins(20, 15, 20, 15)

        # Аватар
        lbl_avatar = QLabel("🧙‍♂️")
        lbl_avatar.setStyleSheet("font-size: 50px; border: none; background: transparent;")
        hero_layout.addWidget(lbl_avatar)

        # Статистика (Рівень, HP, XP, Gold)
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(5)

        # Рядок: Рівень + HP
        top_row = QHBoxLayout()
        self.lbl_level = QLabel("Lvl 1")
        self.lbl_level.setStyleSheet(
            "font-size: 20px; color: #f1c40f; font-weight: bold; background: transparent; border: none;")

        self.lbl_hp = QLabel("❤️ 100/100")
        self.lbl_hp.setStyleSheet(
            "font-size: 15px; color: #e74c3c; font-weight: bold; margin-left: 15px; background: transparent; border: none;")

        top_row.addWidget(self.lbl_level)
        top_row.addWidget(self.lbl_hp)
        top_row.addStretch()
        stats_layout.addLayout(top_row)

        # XP Bar
        self.xp_bar = QProgressBar()
        self.xp_bar.setFixedHeight(10)
        self.xp_bar.setTextVisible(False)
        self.xp_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #7f8c8d;
                border-radius: 5px;
                background-color: #34495e;
            }
            QProgressBar::chunk { background-color: #f1c40f; border-radius: 4px; }
        """)
        stats_layout.addWidget(self.xp_bar)

        # Золото
        self.lbl_gold = QLabel("💰 0")
        self.lbl_gold.setStyleSheet(
            "color: #f1c40f; font-weight: bold; margin-top: 2px; background: transparent; border: none;")
        stats_layout.addWidget(self.lbl_gold)

        hero_layout.addLayout(stats_layout)
        hero_layout.addStretch()

        # --- Кнопка Виходу ---
        btn_logout = QPushButton("Вийти")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton { 
                background-color: #c0392b; 
                color: white; 
                border: none; 
                padding: 8px 15px; 
                border-radius: 5px; 
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #e74c3c; }
            QPushButton:pressed { background-color: #a93226; }
        """)
        btn_logout.clicked.connect(self.on_logout)
        hero_layout.addWidget(btn_logout)

        self.left_layout.addWidget(self.hero_frame)

    def create_quest_controls(self, parent_layout, add_command, btn_text):
        """Створення панелі кнопок (Додати, Оновити)."""
        controls = QHBoxLayout()
        controls.setContentsMargins(5, 0, 5, 0)

        btn_add = QPushButton(btn_text)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_add.clicked.connect(add_command)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setFixedWidth(50)
        btn_refresh.setStyleSheet("""
            QPushButton { 
                background-color: #95a5a6; 
                color: white; 
                border-radius: 5px; 
                padding: 10px; 
                font-weight: bold; 
                font-size: 14px;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        btn_refresh.clicked.connect(self.refresh_data)

        controls.addWidget(btn_add)
        controls.addWidget(btn_refresh)
        parent_layout.addLayout(controls)

    def create_scroll_area(self, parent_layout):
        """Створення прокручуваної області для списків."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: #f0f2f5; }
            QScrollBar:vertical { background: #dfe6e9; width: 10px; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #b2bec3; border-radius: 5px; }
        """)

        container = QWidget()
        container.setStyleSheet("background: #f0f2f5;")

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(12)  # Відступ між картками
        layout.setContentsMargins(5, 10, 5, 10)

        scroll.setWidget(container)
        parent_layout.addWidget(scroll)
        return layout

    def refresh_data(self):
        """Оновлення всіх даних на екрані."""
        try:
            # 1. Оновлення Героя
            hero = self.service.get_hero()
            self.lbl_level.setText(f"Lvl {hero.level}")
            self.lbl_hp.setText(f"❤️ {hero.hp}/{hero.max_hp}")
            self.lbl_gold.setText(f"💰 {hero.gold}")

            self.xp_bar.setMaximum(hero.xp_to_next_level)
            self.xp_bar.setValue(hero.current_xp)
            self.xp_bar.setToolTip(f"XP: {hero.current_xp} / {hero.xp_to_next_level}")

            # 2. Оновлення Ворога
            enemy = self.service.get_current_enemy()
            self.enemy_widget.update_enemy(enemy)

        except ValueError:
            # Ігноруємо помилки, якщо сесія не ініціалізована (наприклад, при першому запуску до логіну)
            pass

        # 3. Оновлення Звичайних квестів
        self.clear_layout(self.quest_list_layout)
        goals = self.service.get_all_goals()
        # Сортування: спочатку невиконані, потім за дедлайном
        goals.sort(key=lambda x: (x.is_completed, x.deadline))

        if not goals:
            lbl = QLabel("Немає активних квестів.", styleSheet="color: #7f8c8d; font-size: 14px; margin-top: 20px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.quest_list_layout.addWidget(lbl)
        else:
            for g in goals:
                self.add_goal_card(g)

        # 4. Оновлення Довгострокових звичок
        self.clear_layout(self.longterm_list_layout)
        lt_goals = self.service.get_long_term_goals()

        if not lt_goals:
            lbl = QLabel("Немає активних звичок.", styleSheet="color: #7f8c8d; font-size: 14px; margin-top: 20px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.longterm_list_layout.addWidget(lbl)
        else:
            for g in lt_goals:
                self.add_longterm_card(g)

    def clear_layout(self, layout):
        """Очищення layout від віджетів."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # --- КАРТКИ ---
    def add_goal_card(self, goal: Goal):
        """Малює картку звичайного квесту."""
        card = QFrame()

        # Візуалізація статусу
        if goal.is_completed:
            bg_col = "#e0e0e0"
            border_col = "#bdc3c7"
            title_col = "#7f8c8d"
            icon = "✅"
        else:
            bg_col = "white"
            title_col = "#2c3e50"
            # Колір рамки залежить від складності
            colors = {
                Difficulty.EASY: "#2ecc71",  # Зелений
                Difficulty.MEDIUM: "#3498db",  # Синій
                Difficulty.HARD: "#e67e22",  # Оранжевий
                Difficulty.EPIC: "#9b59b6"  # Фіолетовий
            }
            border_col = colors.get(goal.difficulty, "#bdc3c7")
            icon = "⚔️"

        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_col};
                border: 1px solid {border_col};
                border-left: 5px solid {border_col};
                border-radius: 6px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)

        # Заголовок + Кнопки
        header = QHBoxLayout()
        title_lbl = QLabel(f"{icon} {goal.title}")
        title_lbl.setStyleSheet(
            f"font-weight: bold; font-size: 15px; border: none; background: transparent; color: {title_col};")
        header.addWidget(title_lbl)

        header.addStretch()

        if not goal.is_completed:
            btn_complete = QPushButton("Завершити")
            btn_complete.setCursor(Qt.PointingHandCursor)
            btn_complete.setStyleSheet("""
                QPushButton { 
                    background-color: #f1c40f; 
                    border: none; 
                    padding: 5px 10px; 
                    border-radius: 4px; 
                    font-weight: bold; 
                    color: #2c3e50; 
                }
                QPushButton:hover { background-color: #f39c12; }
            """)
            btn_complete.clicked.connect(lambda _, g=goal: self.complete_goal(g))
            header.addWidget(btn_complete)

        btn_del = QPushButton("✕")
        btn_del.setFixedSize(30, 30)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setStyleSheet("""
            QPushButton { 
                color: #e74c3c; 
                border: none; 
                background: transparent; 
                font-weight: bold; 
                font-size: 14px;
            }
            QPushButton:hover { background-color: #fadbd8; border-radius: 15px; }
        """)
        btn_del.clicked.connect(lambda _, g=goal: self.delete_goal(g))
        header.addWidget(btn_del)

        layout.addLayout(header)

        # Інфо рядок
        info_layout = QHBoxLayout()
        diff_lbl = QLabel(f"Складність: {goal.difficulty.name}")
        diff_lbl.setStyleSheet("font-size: 11px; color: gray; border: none; background: transparent;")

        date_lbl = QLabel(f"⏳ {goal.deadline.strftime('%Y-%m-%d %H:%M')}")
        if goal.is_overdue():
            date_lbl.setStyleSheet(
                "color: #e74c3c; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        else:
            date_lbl.setStyleSheet("color: gray; font-size: 12px; border: none; background: transparent;")

        info_layout.addWidget(diff_lbl)
        info_layout.addStretch()
        info_layout.addWidget(date_lbl)
        layout.addLayout(info_layout)

        self.quest_list_layout.addWidget(card)

    def add_longterm_card(self, goal: LongTermGoal):
        """Малює картку довгострокової звички."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white; 
                border: 1px solid #bdc3c7;
                border-left: 5px solid #8e44ad; 
                border-radius: 6px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)

        # Header
        h = QHBoxLayout()
        h.addWidget(QLabel(f"📅 {goal.title}",
                           styleSheet="font-weight: bold; font-size: 15px; color: #2c3e50; border: none; background: transparent;"))
        h.addStretch()

        layout.addLayout(h)

        # Info
        info = QLabel(f"День: {goal.current_day}/{goal.total_days} | Час: {goal.time_frame}")
        info.setStyleSheet("color: #7f8c8d; font-size: 12px; border: none; background: transparent;")
        layout.addWidget(info)

        # Stats
        stats = QLabel(f"✅ Виконано: {goal.checked_days} | ❌ Пропущено: {goal.missed_days}")
        stats.setStyleSheet(
            f"border: none; background: transparent; font-weight: bold; {'color: #27ae60' if goal.missed_days == 0 else 'color: #e74c3c'}")
        layout.addWidget(stats)

        # Progress bar
        pb = QProgressBar()
        pb.setValue(int(goal.calculate_progress()))
        pb.setFixedHeight(12)
        pb.setStyleSheet("""
            QProgressBar { 
                border: 1px solid #bdc3c7; 
                border-radius: 5px; 
                background: #ecf0f1;
            } 
            QProgressBar::chunk { 
                background-color: #8e44ad; 
                border-radius: 4px;
            }
        """)
        layout.addWidget(pb)

        # Action Button (Check-in)
        if not goal.is_completed:
            btn_check = QPushButton("Відмітити виконання на сьогодні")
            btn_check.setCursor(Qt.PointingHandCursor)

            # Перевіряємо, чи вже відмічено
            today = datetime.now().date()
            if goal.last_checkin and goal.last_checkin.date() == today:
                btn_check.setText("Сьогодні вже зараховано ✅")
                btn_check.setEnabled(False)
                btn_check.setStyleSheet("""
                    background-color: #dfe6e9; 
                    color: #636e72; 
                    border: none; 
                    padding: 8px; 
                    border-radius: 4px;
                """)
            else:
                btn_check.setStyleSheet("""
                    QPushButton { 
                        background-color: #8e44ad; 
                        color: white; 
                        font-weight: bold; 
                        border: none; 
                        padding: 8px; 
                        border-radius: 4px; 
                    }
                    QPushButton:hover { background-color: #9b59b6; }
                """)
                btn_check.clicked.connect(lambda _, g=goal: self.checkin_longterm(g))

            layout.addWidget(btn_check)

        self.longterm_list_layout.addWidget(card)

    # --- Actions / Slots ---
    def on_add_goal(self):
        """Відкриває діалог створення квесту."""
        if AddGoalDialog(self, self.service).exec_():
            self.refresh_data()

    def on_add_longterm(self):
        """Відкриває діалог створення звички."""
        if AddLongTermDialog(self, self.service).exec_():
            self.refresh_data()

    def complete_goal(self, goal):
        """Завершення звичайного квесту."""
        msg = self.service.complete_goal(goal)
        QMessageBox.information(self, "Результат Квесту", msg)
        self.refresh_data()

    def delete_goal(self, goal):
        """Видалення квесту."""
        reply = QMessageBox.question(
            self, 'Видалити?',
            f"Видалити квест '{goal.title}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.service.delete_goal(goal.id)
            self.refresh_data()

    def checkin_longterm(self, goal):
        """Відмітка виконання звички."""
        msg, is_finished = self.service.checkin_long_term(goal)
        QMessageBox.information(self, "Результат", msg)
        self.refresh_data()

    def on_logout(self):
        """Обробка натискання кнопки виходу."""
        reply = QMessageBox.question(
            self, 'Вихід',
            "Вийти з акаунту? (Потрібно буде ввести нікнейм знову)",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.logout_signal.emit()  # Сигналимо в main.py
            self.close()


## enemy_mechanics.py

import random
import uuid
from .models import Enemy, EnemyRarity, Hero


class EnemyGenerator:
    """
    Відповідає за спавн та характеристики противників.
    """

    @staticmethod
    def generate_enemy(hero: Hero) -> Enemy:
        """Створює нового противника на основі рівня героя."""

        # 1. Визначаємо рідкість, Ім'я та Картинку
        roll = random.randint(1, 100)

        image_file = ""

        if roll <= 50:
            rarity = EnemyRarity.EASY
            name = "Лінивий Гоблін"
            image_file = "goblin.png"
            hp_mult = 1.0
            xp_mult = 1.0
            dmg_mult = 0.5
            drop = 0.0
        elif roll <= 85:
            rarity = EnemyRarity.MEDIUM
            name = "Горгона Прокрастинації"
            image_file = "gorgon.png"
            hp_mult = 2.0
            xp_mult = 2.0
            dmg_mult = 1.0
            drop = 0.05
        else:
            rarity = EnemyRarity.HARD
            name = "Мінотавр Інертності"
            image_file = "minotaur.png"
            hp_mult = 4.0
            xp_mult = 4.0
            dmg_mult = 1.5
            drop = 0.25

        # 2. Скалювання рівня (Герой +/- 2)
        level_offset = random.randint(-2, 2)
        enemy_level = max(1, hero.level + level_offset)

        # 3. Розрахунок характеристик
        # Базове HP = 50 * Рівень. Далі множимо на рідкість.
        base_hp = 50 * enemy_level
        max_hp = int(base_hp * hp_mult)

        # Базовий урон ворога (для атак по герою)
        # Наприклад: 5 * рівень * мультиплікатор
        damage = int(5 * enemy_level * dmg_mult)

        # Нагороди
        base_xp = 20 * enemy_level
        reward_xp = int(base_xp * xp_mult)
        reward_gold = reward_xp  # Золото = XP (поки що)

        return Enemy(
            name=name,
            rarity=rarity,
            level=enemy_level,
            current_hp=max_hp,
            max_hp=max_hp,
            damage=damage,
            reward_xp=reward_xp,
            reward_gold=reward_gold,
            drop_chance=drop,
            image_path=image_file  # <--- Додаємо шлях до картинки
        )


## enemy_panel.py

import os
import sys
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from src.models import Enemy, EnemyRarity


# Утиліта, яка надійно повертає шлях до папки, де запущено main.py
def get_project_root():
    """Повертає абсолютний шлях до кореневої папки проєкту (де знаходиться main.py)."""
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class EnemyWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 2px solid #c0392b;
                border-radius: 10px;
            }
        """)
        self.setFixedWidth(200)

        self.layout = QVBoxLayout(self)

        # Заголовок
        lbl_title = QLabel("ПОТОЧНИЙ ВОРОГ")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 10px; border: none;")
        self.layout.addWidget(lbl_title)

        # Іконка (поки текст)
        self.lbl_icon = QLabel("👹")
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setStyleSheet("font-size: 60px; border: none; background: transparent;")
        self.layout.addWidget(self.lbl_icon)

        # Ім'я та Рівень
        self.lbl_name = QLabel("Name")
        self.lbl_name.setAlignment(Qt.AlignCenter)
        self.lbl_name.setStyleSheet("color: white; font-weight: bold; font-size: 14px; border: none;")
        self.lbl_name.setWordWrap(True)
        self.layout.addWidget(self.lbl_name)

        self.lbl_info = QLabel("Lvl ? | Rarity")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        self.lbl_info.setStyleSheet("color: #bdc3c7; font-size: 11px; border: none;")
        self.layout.addWidget(self.lbl_info)

        # HP Bar
        self.hp_bar = QProgressBar()
        self.hp_bar.setFixedHeight(15)
        self.hp_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #7f8c8d;
                border-radius: 5px;
                background-color: #34495e;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk { background-color: #c0392b; border-radius: 4px; }
        """)
        self.layout.addWidget(self.hp_bar)

        # Stats info
        self.lbl_stats = QLabel("Dmg: ?")
        self.lbl_stats.setAlignment(Qt.AlignCenter)
        self.lbl_stats.setStyleSheet("color: #f39c12; font-size: 11px; border: none;")
        self.layout.addWidget(self.lbl_stats)

    def update_enemy(self, enemy: Enemy):
        self.lbl_name.setText(enemy.name)
        self.lbl_info.setText(f"Lvl {enemy.level} | {enemy.rarity.value}")

        self.hp_bar.setMaximum(enemy.max_hp)
        self.hp_bar.setValue(enemy.current_hp)
        self.hp_bar.setFormat(f"{enemy.current_hp}/{enemy.max_hp}")

        self.lbl_stats.setText(f"⚔️ Урон: {enemy.damage}")

        # --- ВІДОБРАЖЕННЯ КАРТИНКИ (Виправлення шляху) ---
        base_path = get_project_root()
        image_full_path = os.path.join(base_path, "assets", "enemies", enemy.image_path)

        if enemy.image_path and os.path.exists(image_full_path):
            pixmap = QPixmap(image_full_path)
            # Масштабуємо піксель-арт
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.lbl_icon.setPixmap(pixmap)
            self.lbl_icon.setText("")  # Прибираємо текст, якщо є картинка
        else:
            # Якщо картинки немає або шлях неправильний - показуємо смайлик
            self.lbl_icon.setPixmap(QPixmap())
            self.lbl_icon.setText("👹")

        # Зміна кольору рамки від рідкості
        color = "#c0392b"  # Red default
        if enemy.rarity == EnemyRarity.EASY:
            color = "#2ecc71"
        elif enemy.rarity == EnemyRarity.MEDIUM:
            color = "#f39c12"
        elif enemy.rarity == EnemyRarity.HARD:
            color = "#c0392b"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2c3e50;
                border: 3px solid {color};
                border-radius: 10px;
            }}
        """)


## auth.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox, QHBoxLayout, QFrame
)
from PyQt5.QtCore import pyqtSignal
from src.logic import AuthService
from src.models import HeroClass, Gender


class LoginWindow(QWidget):
    # Сигнал, який повідомляє main.py, що вхід виконано успішно
    login_successful = pyqtSignal()

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.setWindowTitle("Вхід 🛡️")
        self.resize(300, 250)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Введіть Нікнейм вашого Героя:", styleSheet="font-size: 14px; font-weight: bold;"))

        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("Нікнейм")
        layout.addWidget(self.nick_input)

        btn_login = QPushButton("Увійти")
        btn_login.setStyleSheet("background-color: #3498db; color: white; padding: 10px; font-weight: bold;")
        btn_login.clicked.connect(self.do_login)
        layout.addWidget(btn_login)

        layout.addStretch()

        layout.addWidget(QLabel("Перший раз тут?"))
        btn_create = QPushButton("Створити Персонажа")
        btn_create.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
        btn_create.clicked.connect(self.open_creation)
        layout.addWidget(btn_create)

    def do_login(self):
        nick = self.nick_input.text().strip()
        try:
            self.auth_service.login(nick)
            self.login_successful.emit()  # Надсилаємо сигнал успіху
        except ValueError as e:
            QMessageBox.warning(self, "Помилка", str(e))

    def open_creation(self):
        self.creation_window = CreationWindow(self.auth_service)
        self.creation_window.creation_successful.connect(self.on_creation_success)
        self.creation_window.show()
        self.close()

    def on_creation_success(self):
        self.login_successful.emit()
        self.creation_window.close()


class CreationWindow(QWidget):
    creation_successful = pyqtSignal()

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.setWindowTitle("Створення Персонажа ✨")
        self.resize(400, 500)
        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout(self)

        # 1. Нікнейм
        self.layout.addWidget(QLabel("1. Оберіть ім'я:", styleSheet="font-weight: bold;"))
        self.nick_input = QLineEdit()
        self.layout.addWidget(self.nick_input)

        # 2. Клас
        self.layout.addWidget(QLabel("2. Оберіть клас:", styleSheet="font-weight: bold; margin-top: 10px;"))
        self.class_combo = QComboBox()
        for hc in HeroClass:
            self.class_combo.addItem(hc.value, hc)
        self.layout.addWidget(self.class_combo)

        # 3. Стать
        self.layout.addWidget(QLabel("3. Оберіть стать:", styleSheet="font-weight: bold; margin-top: 10px;"))
        self.gender_combo = QComboBox()
        for g in Gender:
            self.gender_combo.addItem(g.value, g)
        self.layout.addWidget(self.gender_combo)

        # 4. Зовнішність (Базовий редактор - поки що вибір параметрів)
        self.layout.addWidget(QLabel("4. Зовнішність:", styleSheet="font-weight: bold; margin-top: 10px;"))

        self.hair_combo = QComboBox()
        self.hair_combo.addItems(["Коротке волосся", "Довге волосся", "Лисина", "Ірокез"])
        self.layout.addWidget(QLabel("Зачіска:"))
        self.layout.addWidget(self.hair_combo)

        self.color_combo = QComboBox()
        self.color_combo.addItems(["Чорне", "Блонд", "Руде", "Каштанове", "Синє"])
        self.layout.addWidget(QLabel("Колір волосся:"))
        self.layout.addWidget(self.color_combo)

        self.layout.addStretch()

        btn_create = QPushButton("Створити Героя")
        btn_create.setStyleSheet(
            "background-color: #8e44ad; color: white; padding: 12px; font-weight: bold; font-size: 14px;")
        btn_create.clicked.connect(self.create_character)
        self.layout.addWidget(btn_create)

    def create_character(self):
        nick = self.nick_input.text().strip()
        h_class = self.class_combo.currentData()
        gender = self.gender_combo.currentData()

        # Формуємо рядок зовнішності
        appearance = f"Hair: {self.hair_combo.currentText()}, Color: {self.color_combo.currentText()}"

        try:
            self.auth_service.register(nick, h_class, gender, appearance)
            QMessageBox.information(self, "Успіх", "Героя створено! Пригоди починаються!")
            self.creation_successful.emit()
        except ValueError as e:
            QMessageBox.warning(self, "Помилка", str(e))


## session.py

import json
import os
from typing import Optional

SESSION_FILE = "session.json"


class SessionManager:
    """
    Керує файлом сесії для автоматичного входу.
    """

    @staticmethod
    def save_session(hero_id: str):
        """Зберігає ID поточного героя у файл."""
        data = {"current_hero_id": hero_id}
        with open(SESSION_FILE, "w") as f:
            json.dump(data, f)

    @staticmethod
    def load_session() -> Optional[str]:
        """
        Повертає ID героя, якщо сесія існує.
        Якщо ні - повертає None.
        """
        if not os.path.exists(SESSION_FILE):
            return None

        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                return data.get("current_hero_id")
        except:
            return None

    @staticmethod
    def clear_session():
        """Видаляє файл сесії (вихід з акаунту)."""
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

## longterm_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QSpinBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from src.logic import GoalService


class AddLongTermDialog(QDialog):
    def __init__(self, parent, service: GoalService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Нова Довгострокова Ціль 📅")
        self.resize(400, 450)
        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout(self)

        # 1. Назва
        self.layout.addWidget(QLabel("Назва (напр. 'Вчити Python'):"))
        self.title_input = QLineEdit()
        self.layout.addWidget(self.title_input)

        # 2. Тривалість
        self.layout.addWidget(QLabel("Тривалість (днів):"))
        self.days_input = QSpinBox()
        self.days_input.setRange(1, 365)
        self.days_input.setValue(30)
        self.layout.addWidget(self.days_input)

        # 3. Час виконання
        self.layout.addWidget(QLabel("Часовий проміжок (текст, напр. '16:00 - 18:00'):"))
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("напр. 2 години ввечері")
        self.layout.addWidget(self.time_input)

        # 4. Опис
        self.layout.addWidget(QLabel("Опис:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.layout.addWidget(self.desc_input)

        # Кнопка
        btn_save = QPushButton("Почати Челендж")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton { 
                background-color: #8e44ad; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #9b59b6; }
        """)
        btn_save.clicked.connect(self.save_goal)
        self.layout.addWidget(btn_save)

    def save_goal(self):
        title = self.title_input.text()
        days = self.days_input.value()
        time_frame = self.time_input.text()
        desc = self.desc_input.toPlainText()

        try:
            self.service.create_long_term_goal(title, desc, days, time_frame)
            self.accept()
        except Exception as e:  # <--- Ловимо ВСІ помилки (в т.ч. базу даних)
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити звичку:\n{str(e)}")


# Додамо імпорт Qt, який використовується в стилях курсору
from PyQt5.QtCore import Qt


## __init__.py

"""
Головний пакет додатку Learning Goals RPG.
Містить бізнес-логіку, моделі даних, роботу з БД та допоміжні сервіси.
"""

# Версія додатку
__version__ = '1.0.0'

# Імпортуємо основні моделі, щоб їх можна було дістати прямо з src
from .models import (
    Hero,
    Enemy,
    Goal,
    SubGoal,
    LongTermGoal,
    Difficulty,
    HeroClass,
    Gender,
    EnemyRarity
)

# Імпортуємо сервіси
from .storage import StorageService
from .logic import GoalService, AuthService
from .session import SessionManager
from .enemy_mechanics import EnemyGenerator
from .longterm_mechanics import LongTermManager

# Список того, що буде доступно, якщо хтось напише: from src import *
__all__ = [
    # Моделі
    'Hero', 'Enemy', 'Goal', 'SubGoal', 'LongTermGoal',
    'Difficulty', 'HeroClass', 'Gender', 'EnemyRarity',

    # Сервіси
    'StorageService',
    'GoalService',
    'AuthService',
    'SessionManager',

    # Механіки
    'EnemyGenerator',
    'LongTermManager'
]