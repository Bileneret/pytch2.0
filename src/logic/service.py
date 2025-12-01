from .hero_logic import HeroLogic
from .combat_logic import CombatLogic
from .quest_logic import QuestLogic
from .habit_logic import HabitLogic
from .item_logic import ItemLogic
from .shop_logic import ShopLogic
from .skill_logic import SkillLogic

class GoalService(HeroLogic, CombatLogic, QuestLogic, HabitLogic, ItemLogic, ShopLogic): # <--- Додано ShopLogic
    """
    Головний сервіс логіки.
    Об'єднує всі міксини (Hero, Combat, Quest, Habit, Item, Shop).
    """
    def __init__(self, storage, hero_id: str):
        self.storage = storage
        self.hero_id = hero_id