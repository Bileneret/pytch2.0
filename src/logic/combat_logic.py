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
        """
        bonuses = self.calculate_equipment_bonuses()

        return {
            'str': hero.str_stat + bonuses['str'],
            'int': hero.int_stat + bonuses['int'],
            'dex': hero.dex_stat + bonuses['dex'],
            'vit': hero.vit_stat + bonuses['vit'],
            'def': hero.def_stat + bonuses['def'],
            'double_attack_chance': bonuses['double_attack_chance']
        }

    def calculate_hero_damage(self, hero) -> Tuple[int, int]:
        stats = self._get_total_stats(hero)
        bonuses = self.calculate_equipment_bonuses()

        bonus_phys = (stats['str'] * 2) + bonuses['base_dmg']
        bonus_magic = stats['int'] * 2

        total_phys = hero.base_damage + bonus_phys
        total_magic = bonus_magic

        return total_phys, total_magic

    def take_damage(self, hero, enemy) -> int:
        stats = self._get_total_stats(hero)
        dodge_chance = stats['dex'] * 1.0
        if random.uniform(0, 100) < dodge_chance:
            return 0

        reduction = stats['def'] * 2
        final_damage = max(1, enemy.damage - reduction)

        hero.hp -= final_damage
        if hero.hp < 0: hero.hp = 0
        return final_damage

    def attack_enemy(self, phys_dmg: int = 0, magic_dmg: int = 0, override_da_chance: int = None) -> Tuple[
        str, bool, Optional[str]]:
        """
        :param override_da_chance: Якщо передано, використовується цей шанс подвійної атаки замість статів героя.
        """
        hero = self.get_hero()
        enemy = self.get_current_enemy()

        # Авто-розрахунок для звичайної атаки
        if phys_dmg == 0 and magic_dmg == 0:
            phys_dmg, magic_dmg = self.calculate_hero_damage(hero)

        # --- ЗАСТОСУВАННЯ БАФФУ (SKILL 4) ---
        if hero.buff_multiplier > 1.0:
            phys_dmg = int(phys_dmg * hero.buff_multiplier)
            magic_dmg = int(magic_dmg * hero.buff_multiplier)
            hero.buff_multiplier = 1.0
            self.storage.update_hero(hero)

        # --- ЛОГІКА ПОДВІЙНОЇ АТАКИ ---
        if override_da_chance is not None:
            da_chance = override_da_chance
        else:
            stats = self._get_total_stats(hero)
            da_chance = stats.get('double_attack_chance', 0)

        attacks = []
        attacks.append((phys_dmg, magic_dmg))

        is_double_attack = False
        if da_chance > 0 and random.randint(1, 100) <= da_chance:
            is_double_attack = True
            # Додаткова атака: 50% від основної
            sec_phys = int(phys_dmg * 0.5)
            sec_magic = int(magic_dmg * 0.5)
            attacks.append((sec_phys, sec_magic))

        total_damage_dealt = 0
        hits_info = []

        for p, m in attacks:
            dmg_sum = p + m
            enemy.current_hp -= dmg_sum
            total_damage_dealt += dmg_sum
            hits_info.append(f"(⚔️{p} + ✨{m})")

        damage_details = " + ".join(hits_info)

        if is_double_attack:
            msg = f"⚔️ ПОДВІЙНА АТАКА! ⚔️\nВи нанесли {total_damage_dealt} урону {damage_details} по {enemy.name}!"
        else:
            msg = f"Ви нанесли {total_damage_dealt} урону {damage_details} по {enemy.name}!"

        is_dead = False
        loot_info = None

        if enemy.current_hp <= 0:
            is_dead = True
            hero.current_xp += enemy.reward_xp
            hero.gold += enemy.reward_gold
            loot_info = f"Отримано: {enemy.reward_xp} XP, {enemy.reward_gold} монет."

            if random.random() < enemy.drop_chance:
                loot_info += "\n🎁 Випав предмет спорядження! (В розробці)"

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