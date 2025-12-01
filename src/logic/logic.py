from .hero_logic import HeroLogic
from .combat_logic import CombatLogic
from .quest_logic import QuestLogic
from .habit_logic import HabitLogic

class ValidationUtils:
    """
    Утиліти валідації.
    """
    @staticmethod
    def validate_title(title: str) -> bool:
        return bool(title and title.strip())

class GoalService(HeroLogic, CombatLogic, QuestLogic, HabitLogic):
    """
    Головний сервіс логіки.
    Об'єднує всі міксини (Hero, Combat, Quest, Habit).
    """
    def __init__(self, storage, hero_id: str):
        self.storage = storage
        self.hero_id = hero_id

