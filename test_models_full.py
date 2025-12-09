import unittest
from datetime import datetime, timedelta
from src.models import (
    Hero, HeroClass, Gender, Goal, SubGoal, LongTermGoal,
    Item, ItemType, EquipmentSlot
)


class TestModels(unittest.TestCase):

    def test_hero_initialization_and_stats(self):
        """Перевірка створення героя та розрахунку похідних характеристик."""
        hero = Hero(
            nickname="TestHero",
            hero_class=HeroClass.WARRIOR,
            gender=Gender.MALE,
            appearance="img.png",
            vit_stat=10,
            int_stat=5
        )

        # Перевірка базових значень
        self.assertEqual(hero.level, 1)
        self.assertEqual(hero.gold, 0)

        # Перевірка update_derived_stats
        hero.update_derived_stats()
        # Max HP = 100 + (vit * 5) = 100 + 50 = 150
        self.assertEqual(hero.max_hp, 150)
        # Max Mana = 10 + (int * 5) = 10 + 25 = 35
        self.assertEqual(hero.max_mana, 35)

    def test_goal_progress_calculation(self):
        """Перевірка розрахунку прогресу цілі."""
        goal = Goal(title="Test Goal", description="Desc", deadline=datetime.now())

        # Без підзадач - 0%
        self.assertEqual(goal.calculate_progress(), 0.0)

        # Додаємо підзадачі
        s1 = SubGoal(title="S1", is_completed=True)
        s2 = SubGoal(title="S2", is_completed=False)
        goal.add_subgoal(s1)
        goal.add_subgoal(s2)

        # 1 з 2 виконано = 50%
        self.assertEqual(goal.calculate_progress(), 50.0)

        s2.mark_done()
        self.assertEqual(goal.calculate_progress(), 100.0)

    def test_long_term_goal_logic(self):
        """Перевірка логіки довгострокових звичок."""
        ltg = LongTermGoal(
            title="Habit",
            description="Run",
            total_days=10,
            start_date=datetime.now()
        )

        ltg.current_day = 5
        self.assertEqual(ltg.calculate_progress(), 50.0)

        # Перевірка статусів
        ltg.daily_state = 'finished'
        self.assertTrue(ltg.daily_state == 'finished')

    def test_item_creation(self):
        """Перевірка моделі предмету."""
        item = Item(
            name="Super Sword",
            item_type=ItemType.WEAPON,
            slot=EquipmentSlot.MAIN_HAND,
            price=100
        )
        self.assertEqual(item.price, 100)
        self.assertEqual(item.item_type, ItemType.WEAPON)


if __name__ == '__main__':
    unittest.main()