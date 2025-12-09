import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, time, timedelta
import uuid

from src.logic.auth import AuthService
from src.logic.shop_logic import ShopLogic
from src.logic.habit_logic import HabitLogic
from src.logic.combat_logic import CombatLogic
from src.models import Hero, HeroClass, Gender, Item, ItemType, LongTermGoal


class GameService(ShopLogic, HabitLogic, CombatLogic):
    """Тестовий клас, що об'єднує міксини."""

    def __init__(self, storage, hero_id):
        self.storage = storage
        self.hero_id = hero_id

    def get_hero(self):
        return self.storage.get_hero_by_id(self.hero_id)

    def get_current_enemy(self):
        enemy = MagicMock()
        enemy.damage = 10
        return enemy

    # --- ДОДАНО ЗАГЛУШКИ ДЛЯ ВИПРАВЛЕННЯ ПОМИЛОК ---

    def calculate_equipment_bonuses(self):
        """Заглушка для розрахунку бонусів (повертає нулі)."""
        return {
            'str': 0, 'int': 0, 'dex': 0, 'vit': 0, 'def': 0,
            'base_dmg': 0, 'double_attack_chance': 0
        }

    def _add_rewards(self, hero, xp, gold):
        """Заглушка для нарахування нагород."""
        hero.current_xp += xp
        hero.gold += gold
        # Логіку підвищення рівня тут можна спростити або опустити для юніт-тестів
    # -----------------------------------------------


class TestBusinessLogic(unittest.TestCase):

    def setUp(self):
        self.mock_storage = MagicMock()
        self.hero_id = str(uuid.uuid4())
        self.service = GameService(self.mock_storage, self.hero_id)

        # Базовий герой для тестів
        self.hero = Hero("LogicHero", HeroClass.WARRIOR, Gender.MALE, "img")
        self.hero.id = self.hero_id
        self.hero.gold = 1000
        self.hero.hp = 100
        self.hero.def_stat = 0
        self.hero.str_stat = 5  # Базова сила для бою

        # Налаштовуємо mock_storage
        self.mock_storage.get_hero_by_id.return_value = self.hero

    # --- ТЕСТИ AUTH (auth.py) ---
    def test_auth_register_normal(self):
        auth = AuthService(self.mock_storage)
        hero = auth.register("NewUser", HeroClass.WARRIOR, Gender.MALE, "img")

        self.assertEqual(hero.level, 1)
        self.mock_storage.create_hero.assert_called_once()

    def test_auth_register_tester_cheat(self):
        auth = AuthService(self.mock_storage)
        hero = auth.register("tester", HeroClass.MAGE, Gender.FEMALE, "img")
        self.assertEqual(hero.level, 24)

    def test_auth_login_fail(self):
        auth = AuthService(self.mock_storage)
        self.mock_storage.get_hero_by_nickname.return_value = None
        with self.assertRaises(ValueError):
            auth.login("UnknownUser")

    # --- ТЕСТИ SHOP (shop_logic.py) ---
    def test_shop_buy_item_success(self):
        item_id = uuid.uuid4()
        item = Item(id=item_id, name="Sword", price=500, item_type=ItemType.WEAPON, slot=None)
        self.mock_storage.get_all_library_items.return_value = [item]

        msg = self.service.buy_item(item_id)

        self.assertIn("Куплено", msg)
        self.assertEqual(self.hero.gold, 500)
        self.mock_storage.add_item_to_inventory.assert_called_with(self.hero_id, item)

    def test_shop_buy_insufficient_funds(self):
        item_id = uuid.uuid4()
        item = Item(id=item_id, name="Expensive", price=2000, item_type=ItemType.WEAPON, slot=None)
        self.mock_storage.get_all_library_items.return_value = [item]

        with self.assertRaises(ValueError):
            self.service.buy_item(item_id)

    # --- ТЕСТИ HABIT (habit_logic.py) ---
    def test_create_habit(self):
        self.service.create_long_term_goal("Run", "Daily", 30, "08:00 - 09:00")
        self.mock_storage.save_long_term_goal.assert_called_once()

    def test_check_habit_deadlines_missed_start(self):
        """Тест пропуску часу старту звички."""
        goal = LongTermGoal(
            title="Morning Run", description="", total_days=10,
            start_date=datetime.now(),
            time_frame="08:00 - 09:00", daily_state="pending"
        )

        # Час 08:10 (пропуск старту)
        now = datetime.combine(datetime.now().date(), time(8, 10))

        enemy = MagicMock()
        enemy.damage = 10

        alerts = self.service.check_habit_deadlines(goal, now, enemy, self.hero)

        self.assertTrue(len(alerts) > 0)
        self.assertIn("Час старту звички", alerts[0])
        self.assertEqual(goal.daily_state, 'failed')

    @patch('src.logic.habit_logic.LongTermManager.calculate_interval_reward')
    def test_finish_habit(self, mock_reward):
        """Тест завершення звички та отримання нагороди."""
        mock_reward.return_value = (50, 20)

        goal = LongTermGoal(title="Habit", description="", total_days=5, start_date=datetime.now())
        goal.current_day = 1

        initial_xp = self.hero.current_xp
        initial_gold = self.hero.gold

        self.service.finish_habit(goal)

        self.assertEqual(goal.daily_state, 'finished')
        self.assertEqual(self.hero.current_xp, initial_xp + 50)
        self.assertEqual(self.hero.gold, initial_gold + 20)


if __name__ == '__main__':
    unittest.main()