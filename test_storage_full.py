import unittest
import uuid
import os
import tempfile
from src.storage import StorageService
from src.models import Hero, HeroClass, Gender, Item, ItemType, EquipmentSlot


class TestStorageService(unittest.TestCase):

    def setUp(self):
        # Створюємо тимчасовий файл для БД
        self.db_fd, self.db_path = tempfile.mkstemp()
        # Ініціалізуємо сервіс з цим файлом
        self.storage = StorageService(self.db_path)

    def tearDown(self):
        # Закриваємо дескриптор і видаляємо файл після тесту
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_hero_crud(self):
        """Тест створення та отримання героя."""
        hero = Hero(
            nickname="StorageTester",
            hero_class=HeroClass.MAGE,
            gender=Gender.FEMALE,
            appearance="mage.png"
        )
        self.storage.create_hero(hero)

        loaded_hero = self.storage.get_hero_by_nickname("StorageTester")
        self.assertIsNotNone(loaded_hero)
        self.assertEqual(loaded_hero.id, hero.id)
        self.assertEqual(loaded_hero.hero_class, HeroClass.MAGE)

        # Тест оновлення
        loaded_hero.gold = 500
        self.storage.update_hero(loaded_hero)

        updated_hero = self.storage.get_hero_by_id(str(hero.id))
        self.assertEqual(updated_hero.gold, 500)

    def test_items_library_and_inventory(self):
        """Тест роботи з предметами та інвентарем."""
        # 1. Створюємо героя
        hero = Hero("InvHero", HeroClass.ROGUE, Gender.MALE, "img")
        self.storage.create_hero(hero)

        # 2. Додаємо предмет в бібліотеку вручну
        item_id = uuid.uuid4()
        conn = self.storage._get_connection()
        conn.execute("""
            INSERT INTO items_library (id, name, item_type, slot, price)
            VALUES (?, ?, ?, ?, ?)
        """, (str(item_id), "Test Dagger", ItemType.WEAPON.value, EquipmentSlot.MAIN_HAND.value, 100))
        conn.commit()
        conn.close()

        # 3. Перевіряємо завантаження бібліотеки
        library = self.storage.get_all_library_items()
        target_item = next((i for i in library if i.id == item_id), None)
        self.assertIsNotNone(target_item)

        # 4. Додаємо в інвентар
        self.storage.add_item_to_inventory(str(hero.id), target_item)

        # 5. Перевіряємо інвентар
        inventory = self.storage.get_inventory(str(hero.id))
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0].item.name, "Test Dagger")

        # 6. Тест екіпірування
        inv_item_id = inventory[0].id
        self.storage.equip_item(str(hero.id), inv_item_id, EquipmentSlot.MAIN_HAND.value)

        inventory_after = self.storage.get_inventory(str(hero.id))
        self.assertTrue(inventory_after[0].is_equipped)

    def test_duplicate_nickname(self):
        """Перевірка унікальності нікнейму."""
        h1 = Hero("UniqueNick", HeroClass.WARRIOR, Gender.MALE, "1")
        self.storage.create_hero(h1)

        h2 = Hero("UniqueNick", HeroClass.ARCHER, Gender.FEMALE, "2")
        with self.assertRaises(ValueError):
            self.storage.create_hero(h2)


if __name__ == '__main__':
    unittest.main()