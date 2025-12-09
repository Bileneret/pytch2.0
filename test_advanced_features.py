import unittest
import json
import uuid
from unittest.mock import MagicMock, patch
from src.models import Hero, HeroClass, Gender, Enemy, EnemyRarity, DamageType, Goal, Difficulty, Item, ItemType, \
    EquipmentSlot

# Імпортуємо всі міксини для створення повного тестового класу
from src.logic.shop_logic import ShopLogic
from src.logic.habit_logic import HabitLogic
from src.logic.combat_logic import CombatLogic
from src.logic.skill_logic import SkillLogic
from src.logic.quest_logic import QuestLogic
from src.logic.hero_logic import HeroLogic
from src.logic.item_logic import ItemLogic


class FullGameService(ShopLogic, HabitLogic, CombatLogic, SkillLogic, QuestLogic, HeroLogic, ItemLogic):
    """
    Повний клас сервісу, який об'єднує ВСІ міксини.
    Це імітує реальний Service/AppController.
    """

    def __init__(self, storage, hero_id):
        self.storage = storage
        self.hero_id = hero_id

    def get_hero(self):
        # Перевизначаємо для тестів, щоб не лізти в БД, а брати мок
        hero = self.storage.get_hero_by_id(self.hero_id)
        # Імітуємо перевірку стріка (hero_logic), але без дат
        return hero

    def get_current_enemy(self):
        return self.storage.load_enemy(self.hero_id)


class TestAdvancedFeatures(unittest.TestCase):

    def setUp(self):
        self.mock_storage = MagicMock()
        self.hero_id = str(uuid.uuid4())
        self.service = FullGameService(self.mock_storage, self.hero_id)

        # --- Базовий Герой ---
        self.hero = Hero(nickname="AdvancedTester", hero_class=HeroClass.MAGE, gender=Gender.MALE, appearance="img")
        self.hero.id = self.hero_id
        self.hero.hp = 50
        self.hero.max_hp = 100
        self.hero.mana = 50
        self.hero.max_mana = 100
        self.hero.gold = 0
        self.hero.current_xp = 0
        self.hero.level = 10  # Рівень достатній для деяких скілів
        self.hero.int_stat = 10
        self.hero.str_stat = 10

        # Налаштування storage
        self.mock_storage.get_hero_by_id.return_value = self.hero
        self.mock_storage.get_inventory.return_value = []  # Спочатку пустий інвентар

        # --- Базовий Ворог ---
        self.enemy = Enemy(
            name="Test Dummy", rarity=EnemyRarity.EASY, level=1,
            current_hp=200, max_hp=200, damage=10, damage_type=DamageType.PHYSICAL,
            reward_xp=50, reward_gold=50, drop_chance=0
        )
        self.mock_storage.load_enemy.return_value = self.enemy

    # === ТЕСТИ НАВИЧОК (SkillLogic) ===

    def test_skill_heal(self):
        """Перевірка навички лікування (Skill 3)."""
        # Skill 3: level_req=15. Піднімемо рівень героя.
        self.hero.level = 20
        self.hero.hp = 10  # Мало здоров'я

        # Симулюємо заглушку для get_skills, щоб не залежати від хардкоду в класі
        # Або використовуємо реальний метод, якщо він просто повертає список
        # В даному коді get_skills повертає хардкод, це ок.

        # Skill 3 value = 0.25 (25% від MaxHP). MaxHP=100 -> +25 HP.
        # Mana cost = 10.

        msg = self.service.use_skill(3)  # ID 3 = Heal

        self.assertIn("Відновлено", msg)
        self.assertEqual(self.hero.hp, 35)  # 10 + 25
        self.assertEqual(self.hero.mana, 40)  # 50 - 10
        self.mock_storage.update_hero.assert_called()

    def test_skill_buff(self):
        """Перевірка баффа (Skill 4)."""
        self.hero.level = 25

        self.service.use_skill(4)  # ID 4 = Buff

        self.assertEqual(self.hero.buff_multiplier, 1.5)
        self.assertEqual(self.hero.mana, 35)  # 50 - 15

    def test_skill_not_enough_mana(self):
        """Перевірка нестачі мани."""
        self.hero.level = 25
        self.hero.mana = 0

        with self.assertRaises(ValueError) as cm:
            self.service.use_skill(1)  # Будь-який скіл
        self.assertEqual(str(cm.exception), "Недостатньо мани!")

    # === ТЕСТИ КВЕСТІВ І UNDO (QuestLogic) ===

    def test_quest_completion_and_undo(self):
        """
        Критичний тест: Виконання квесту -> Створення Snapshot -> Скасування (Undo).
        """
        # 1. Підготовка
        goal = Goal(title="Test Goal", description="Desc", deadline=datetime.now(), difficulty=Difficulty.EASY)
        initial_gold = self.hero.gold  # 0
        initial_xp = self.hero.current_xp  # 0

        # Мок для attack_enemy, бо complete_goal викликає атаку
        # Повертає (msg, is_dead, loot)
        self.service.attack_enemy = MagicMock(return_value=("Hit", False, None))

        # 2. Виконання
        self.service.complete_goal(goal)

        # Перевірки після виконання
        self.assertTrue(goal.is_completed)
        self.assertTrue(len(goal.previous_state) > 0)  # Снепшот записався
        self.assertEqual(self.hero.gold, 50)  # +50 за Easy
        self.assertEqual(self.hero.current_xp, 50)

        # Змінимо стан героя, ніби пройшов час
        self.hero.hp = 1  # Його побили

        # 3. Скасування (Undo)
        msg = self.service.undo_complete_goal(goal)

        # Перевірки після Undo
        self.assertFalse(goal.is_completed)
        self.assertEqual(self.hero.gold, 0)  # Повернулось
        self.assertEqual(self.hero.current_xp, 0)  # Повернулось
        self.assertEqual(self.hero.hp, 50)  # HP відновилось зі снепшота (було 50 в setUp)
        self.assertIn("відновлено", msg)

    # === ТЕСТИ БОЙОВОЇ СИСТЕМИ (CombatLogic + ItemLogic) ===

    def test_defense_reduction(self):
        """Перевірка, чи працює захист (Defense)."""
        # Формула в combat_logic: reduction = stats['def'] * 2
        # final_damage = enemy.damage - reduction

        self.hero.def_stat = 2  # Зменшення має бути 4
        # self.enemy.damage = 10 (в setUp)

        # Щоб тест спрацював, треба щоб метод take_damage викликав _get_total_stats
        # А _get_total_stats викликає calculate_equipment_bonuses
        # Оскільки ми наслідуємо ItemLogic, це має спрацювати штатно.

        dmg = self.service.take_damage(self.hero, self.enemy)

        # Очікуємо: 10 - (2 * 2) = 6
        # Але тут є рандом на ухилення (dex).
        # Якщо dex малий (в setUp не задали явно, але стат поінти 0), ухилення малоймовірне.
        # Мокнемо random, щоб точно не було ухилення.

        with patch('random.uniform', return_value=100):  # 100 > dodge_chance
            dmg = self.service.take_damage(self.hero, self.enemy)
            self.assertEqual(dmg, 6)

    def test_equipment_bonus_calculation(self):
        """Перевірка підрахунку статів від речей."""
        # Створюємо 2 предмета
        item1 = Item(name="Helm", item_type=ItemType.ARMOR, slot=EquipmentSlot.HEAD, bonus_str=5)
        item2 = Item(name="Sword", item_type=ItemType.WEAPON, slot=EquipmentSlot.MAIN_HAND, base_dmg=10)

        # Робимо з них InventoryItem і кажемо, що вони одягнені
        inv_item1 = MagicMock()
        inv_item1.item = item1
        inv_item1.is_equipped = True

        inv_item2 = MagicMock()
        inv_item2.item = item2
        inv_item2.is_equipped = True

        # Мокаємо get_inventory, щоб він повернув ці речі
        self.mock_storage.get_inventory.return_value = [inv_item1, inv_item2]

        # Викликаємо метод ItemLogic
        bonuses = self.service.calculate_equipment_bonuses()

        self.assertEqual(bonuses['str'], 5)
        self.assertEqual(bonuses['base_dmg'], 10)
        self.assertEqual(bonuses['int'], 0)


from datetime import datetime, timedelta

if __name__ == '__main__':
    unittest.main()