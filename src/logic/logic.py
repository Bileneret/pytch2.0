from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import random

from .models import Goal, Hero, Difficulty, LongTermGoal, HeroClass, Gender, Enemy, DamageType
from .storage import StorageService
from .longterm_mechanics import LongTermManager
from .session import SessionManager
from .enemy_mechanics import EnemyGenerator

# Імпорт міксинів
from .hero_logic import HeroLogic
from .combat_logic import CombatLogic
from .quest_logic import QuestLogic
from .habit_logic import HabitLogic
from .item_logic import ItemLogic  # <--- ВАЖЛИВО: Імпорт ItemLogic

class ValidationUtils:
    """
    Утиліти валідації.
    """
    @staticmethod
    def validate_title(title: str) -> bool:
        return bool(title and title.strip())

# Додаємо ItemLogic до спадкування
class GoalService(HeroLogic, CombatLogic, QuestLogic, HabitLogic, ItemLogic):
    """
    Головний сервіс логіки.
    Об'єднує всі міксини (Hero, Combat, Quest, Habit, Item).
    """
    def __init__(self, storage, hero_id: str):
        self.storage = storage
        self.hero_id = hero_id