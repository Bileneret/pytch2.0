from .hero_logic import HeroLogic
from .combat_logic import CombatLogic
from .quest_logic import QuestLogic
from .habit_logic import HabitLogic
from .item_logic import ItemLogic  # <--- Додано

class GoalService(HeroLogic, CombatLogic, QuestLogic, HabitLogic, ItemLogic): # <--- Додано ItemLogic
    """
    Головний сервіс логіки.
    Об'єднує всі міксини (Hero, Combat, Quest, Habit, Item).
    """
    def __init__(self, storage, hero_id: str):
        self.storage = storage
        self.hero_id = hero_id