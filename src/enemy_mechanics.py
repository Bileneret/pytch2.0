import random
import uuid
from .models import Enemy, EnemyRarity, Hero, DamageType


class EnemyGenerator:
    """
    Відповідає за спавн та характеристики противників.
    """

    @staticmethod
    def generate_enemy(hero: Hero) -> Enemy:
        """Створює нового противника на основі рівня героя."""

        roll = random.randint(1, 100)

        image_file = ""
        dmg_type = DamageType.PHYSICAL  # Дефолт

        if roll <= 50:
            rarity = EnemyRarity.EASY
            name = "Лінивий Гоблін"
            image_file = "goblin.png"
            hp_mult = 1.0
            xp_mult = 1.0
            dmg_mult = 0.5
            drop = 0.0
            dmg_type = DamageType.PHYSICAL
        elif roll <= 85:
            rarity = EnemyRarity.MEDIUM
            name = "Горгона Прокрастинації"
            image_file = "gorgon.png"
            hp_mult = 2.0
            xp_mult = 2.0
            dmg_mult = 1.0
            drop = 0.05
            dmg_type = DamageType.MAGICAL  # Горгона б'є магією
        else:
            rarity = EnemyRarity.HARD
            name = "Мінотавр Інертності"
            image_file = "minotaur.png"
            hp_mult = 4.0
            xp_mult = 4.0
            dmg_mult = 1.5
            drop = 0.25
            dmg_type = DamageType.PHYSICAL

        level_offset = random.randint(-2, 2)
        enemy_level = max(1, hero.level + level_offset)

        base_hp = 50 * enemy_level
        max_hp = int(base_hp * hp_mult)

        damage = int(5 * enemy_level * dmg_mult)

        base_xp = 20 * enemy_level
        reward_xp = int(base_xp * xp_mult)
        reward_gold = reward_xp

        return Enemy(
            name=name,
            rarity=rarity,
            level=enemy_level,
            current_hp=max_hp,
            max_hp=max_hp,
            damage=damage,
            damage_type=dmg_type,  # Призначаємо тип
            reward_xp=reward_xp,
            reward_gold=reward_gold,
            drop_chance=drop,
            image_path=image_file
        )