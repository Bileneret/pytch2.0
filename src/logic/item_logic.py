import uuid
from typing import List, Optional
from ..models import Item, InventoryItem, EquipmentSlot


class ItemLogic:
    """Міксин: Логіка предметів та інвентаря."""

    def get_inventory(self) -> List[InventoryItem]:
        """Отримує весь інвентар поточного героя."""
        return self.storage.get_inventory(self.hero_id)

    def add_item(self, item: Item):
        """Додає предмет в інвентар героя."""
        self.storage.add_item_to_inventory(self.hero_id, item)

    def equip_item(self, inventory_item_id: uuid.UUID, slot: EquipmentSlot):
        """
        Одягає предмет у відповідний слот.
        Автоматично знімає попередній предмет у цьому слоті (це робить storage).
        """
        # Передаємо value (рядок) слота, бо в БД зберігається рядок
        self.storage.equip_item(self.hero_id, inventory_item_id, slot.value)

        # Після зміни спорядження треба перерахувати стати героя
        # Але оскільки стати залежать від предметів динамічно, ми просто оновимо героя
        # (В майбутньому додамо метод recalculate_stats, якщо буде кешування)
        hero = self.get_hero()
        self.storage.update_hero(hero)

    def unequip_item(self, inventory_item_id: uuid.UUID):
        """Знімає предмет."""
        self.storage.unequip_item(inventory_item_id)

        hero = self.get_hero()
        self.storage.update_hero(hero)

    def get_all_library_items(self) -> List[Item]:
        """Повертає всі існуючі в грі предмети."""
        return self.storage.get_all_library_items()

    def get_equipped_items(self) -> List[InventoryItem]:
        """Повертає тільки вдягнуті предмети."""
        inventory = self.get_inventory()
        return [i for i in inventory if i.is_equipped]

    def calculate_equipment_bonuses(self):
        """
        Повертає сумарні бонуси від вдягнутого спорядження.
        Повертає словник: {'str': 0, 'int': 0, ...}
        """
        equipped = self.get_equipped_items()
        bonuses = {
            'str': 0, 'int': 0, 'dex': 0, 'vit': 0, 'def': 0
        }

        for inv_item in equipped:
            item = inv_item.item
            bonuses['str'] += item.bonus_str
            bonuses['int'] += item.bonus_int
            bonuses['dex'] += item.bonus_dex
            bonuses['vit'] += item.bonus_vit
            bonuses['def'] += item.bonus_def

        return bonuses