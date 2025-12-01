
# Імпорт міксинів
from .hero_logic import HeroLogic
from .combat_logic import CombatLogic
from .quest_logic import QuestLogic
from .habit_logic import HabitLogic
from .item_logic import ItemLogic
from .shop_logic import ShopLogic
from .skill_logic import SkillLogic  # <--- ВАЖЛИВО: Імпорт SkillLogic

class ValidationUtils:
    @staticmethod
    def validate_title(title: str) -> bool:
        return bool(title and title.strip())

# Додаємо SkillLogic до спадкування
class GoalService(HeroLogic, CombatLogic, QuestLogic, HabitLogic, ItemLogic, ShopLogic, SkillLogic):
    """
    Головний сервіс логіки.
    Об'єднує всі міксини.
    """
    def __init__(self, storage, hero_id: str):
        self.storage = storage
        self.hero_id = hero_id