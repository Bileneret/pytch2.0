import uuid
from ..models import Item, InventoryItem


class ShopLogic:
    """Міксин для магазину."""

    def buy_item(self, item_id: uuid.UUID) -> str:
        """Купує предмет з бібліотеки за ID."""
        hero = self.get_hero()

        all_items = self.storage.get_all_library_items()
        target_item = next((i for i in all_items if i.id == item_id), None)

        if not target_item:
            raise ValueError("Предмет не знайдено!")

        if hero.gold < target_item.price:
            raise ValueError(f"Недостатньо золота! Потрібно: {target_item.price}, Є: {hero.gold}")

        # Списуємо золото
        hero.gold -= target_item.price
        self.storage.update_hero(hero)

        # Додаємо в інвентар
        self.storage.add_item_to_inventory(self.hero_id, target_item)

        return f"Куплено: {target_item.name}!"