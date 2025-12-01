import random
from typing import Tuple, Optional
from ..models import DamageType
from ..enemy_mechanics import EnemyGenerator


class CombatLogic:
    """Міксин: Бойова система з урахуванням спорядження."""

    def get_current_enemy(self):
        enemy = self.storage.load_enemy(self.hero_id)
        if not enemy:
            hero = self.get_hero()
            enemy = EnemyGenerator.generate_enemy(hero)
            self.storage.save_enemy(enemy, self.hero_id)
        return enemy

    def _get_total_stats(self, hero):
        """
        Повертає реальні характеристики (База + Бонуси від речей).
        Повертає словник.
        """
        # Цей метод (calculate_equipment_bonuses) прийде з ItemLogic,
        # тому важливо, щоб GoalService успадковував і ItemLogic теж.
        bonuses = self.calculate_equipment_bonuses()

        return {
            'str': hero.str_stat + bonuses['str'],
            'int': hero.int_stat + bonuses['int'],
            'dex': hero.dex_stat + bonuses['dex'],
            'vit': hero.vit_stat + bonuses['vit'],
            'def': hero.def_stat + bonuses['def']
        }

    def calculate_hero_damage(self, hero) -> Tuple[int, int]:
        """
        Повертає (фіз. урон, маг. урон).
        Враховує бонуси від спорядження.
        """
        stats = self._get_total_stats(hero)

        # Формула: База + (Сила * 2)
        bonus_phys = stats['str'] * 2
        # Формула: (Інтелект * 2)
        bonus_magic = stats['int'] * 2

        total_phys = hero.base_damage + bonus_phys
        total_magic = bonus_magic

        return total_phys, total_magic

    def take_damage(self, hero, enemy) -> int:
        """
        Розрахунок отримання урону.
        Враховує бонуси захисту та спритності.
        """
        stats = self._get_total_stats(hero)

        # 1. Ухилення (Спритність)
        dodge_chance = stats['dex'] * 1.0
        if random.uniform(0, 100) < dodge_chance:
            return 0  # Ухилився!

        # 2. Зменшення урону (Захист)
        reduction = stats['def'] * 2
        final_damage = max(1, enemy.damage - reduction)

        hero.hp -= final_damage
        if hero.hp < 0: hero.hp = 0
        return final_damage

    def attack_enemy(self, phys_dmg: int = 0, magic_dmg: int = 0) -> Tuple[str, bool, Optional[str]]:
        hero = self.get_hero()
        enemy = self.get_current_enemy()

        if phys_dmg == 0 and magic_dmg == 0:
            phys_dmg, magic_dmg = self.calculate_hero_damage(hero)

        total_dmg = phys_dmg + magic_dmg
        enemy.current_hp -= total_dmg

        msg = f"Ви нанесли {total_dmg} урону (⚔️{phys_dmg} + ✨{magic_dmg}) по {enemy.name}!"
        is_dead = False
        loot_info = None

        if enemy.current_hp <= 0:
            is_dead = True

            hero.current_xp += enemy.reward_xp
            hero.gold += enemy.reward_gold
            loot_info = f"Отримано: {enemy.reward_xp} XP, {enemy.reward_gold} монет."

            if random.random() < enemy.drop_chance:
                loot_info += "\n🎁 Випав предмет спорядження! (В розробці)"
                # Тут можна буде додати логіку видачі рандомного предмета
                # self.give_random_loot()

            msg = f"{msg}\n💀 {enemy.name} переможено!\n{loot_info}"

            self._check_level_up(hero)
            self.storage.update_hero(hero)
            self.storage.delete_enemy(self.hero_id)

            new_enemy = EnemyGenerator.generate_enemy(hero)
            self.storage.save_enemy(new_enemy, self.hero_id)
            msg += f"\n⚔️ З'явився новий ворог: {new_enemy.name}!"
        else:
            self.storage.save_enemy(enemy, self.hero_id)

        return msg, is_dead, loot_info