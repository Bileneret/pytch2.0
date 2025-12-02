import uuid
from typing import List
from ..models import Item, InventoryItem, EquipmentSlot


class ItemLogic:
    """Міксин: Логіка предметів та інвентаря."""

    def get_inventory(self) -> List[InventoryItem]:
        return self.storage.get_inventory(self.hero_id)

    def add_item(self, item: Item):
        self.storage.add_item_to_inventory(self.hero_id, item)

    def give_test_items(self):
        """Видає герою весь набір тестових предметів з бібліотеки."""
        all_items = self.storage.get_all_library_items()
        for item in all_items:
            self.add_item(item)

    def equip_item(self, inventory_item_id: uuid.UUID, slot):
        slot_val = slot.value if hasattr(slot, 'value') else slot
        self.storage.equip_item(self.hero_id, inventory_item_id, slot_val)
        hero = self.get_hero()
        hero.update_derived_stats()  # Перераховуємо HP/Mana
        self.storage.update_hero(hero)

    def unequip_item(self, inventory_item_id: uuid.UUID):
        self.storage.unequip_item(inventory_item_id)
        hero = self.get_hero()
        hero.update_derived_stats()
        self.storage.update_hero(hero)

    def get_equipped_items(self) -> List[InventoryItem]:
        inventory = self.get_inventory()
        return [i for i in inventory if i.is_equipped]

    def calculate_equipment_bonuses(self):
        """Розрахунок всіх бонусів від спорядження."""
        equipped = self.get_equipped_items()

        bonuses = {
            'str': 0, 'int': 0, 'dex': 0, 'vit': 0, 'def': 0,
            'base_dmg': 0,
            'double_attack_chance': 0
        }

        for inv_item in equipped:
            item = inv_item.item
            bonuses['str'] += item.bonus_str
            bonuses['int'] += item.bonus_int
            bonuses['dex'] += item.bonus_dex
            bonuses['vit'] += item.bonus_vit
            bonuses['def'] += item.bonus_def
            bonuses['base_dmg'] += item.base_dmg

            # Додаємо шанс, якщо атрибут існує у предмета (безпечна перевірка)
            if hasattr(item, 'double_attack_chance'):
                bonuses['double_attack_chance'] += item.double_attack_chance

        return bonuses

    def get_all_library_items(self) -> List[Item]:
        """Повертає всі існуючі в грі предмети."""
        return self.storage.get_all_library_items()