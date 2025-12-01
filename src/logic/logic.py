from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import random

# Імпорт міксинів (з поточної папки - одна крапка)
from .hero_logic import HeroLogic
from .combat_logic import CombatLogic
from .quest_logic import QuestLogic
from .habit_logic import HabitLogic
from .item_logic import ItemLogic
from .shop_logic import ShopLogic

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