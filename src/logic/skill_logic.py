import random
import uuid
from ..models import DamageType


class SkillLogic:
    """Міксин: Логіка використання навичок."""

    def get_skills(self):
        """Повертає список доступних навичок (словники з даними)."""
        hero = self.get_hero()

        skills = [
            {
                "id": 1,
                "name": "Skill 1",
                "desc": "Наносить 75% фізичного урону",
                "level_req": 5,
                "mana_cost": 5,
                "type": "damage_phys",
                "value": 0.75
            },
            {
                "id": 2,
                "name": "Skill 2",
                "desc": "Наносить 75% магічного урону",
                "level_req": 10,
                "mana_cost": 5,
                "type": "damage_magic",
                "value": 0.75
            },
            {
                "id": 3,
                "name": "Skill 3",
                "desc": "Лікує 25% макс. здоров'я",
                "level_req": 15,
                "mana_cost": 10,
                "type": "heal",
                "value": 0.25
            },
            {
                "id": 4,
                "name": "Skill 4",
                "desc": "Посилення наступної атаки +50%",
                "level_req": 20,
                "mana_cost": 15,
                "type": "buff",
                "value": 1.5
            },
            {
                "id": 5,
                "name": "Skill 5",
                "desc": "Наносить 50% + 1 від здоров'я ворога",
                "level_req": 25,
                "mana_cost": 20,
                "type": "ultimate",
                "value": 0.5
            }
        ]
        return skills

    def use_skill(self, skill_id: int) -> str:
        hero = self.get_hero()
        skills = self.get_skills()
        skill = next((s for s in skills if s["id"] == skill_id), None)

        if not skill: raise ValueError("Навичку не знайдено!")

        if hero.level < skill["level_req"]:
            raise ValueError(f"Потрібен рівень {skill['level_req']}!")

        if hero.mana < skill["mana_cost"]:
            raise ValueError("Недостатньо мани!")

        enemy = self.get_current_enemy()
        msg = ""

        # --- СПИСАННЯ МАНИ ТА ЗБЕРЕЖЕННЯ ---
        hero.mana -= skill["mana_cost"]
        self.storage.update_hero(hero)

        # --- РОЗРАХУНОК ШАНСУ ПОДВІЙНОЇ ДІЇ ---
        # Шанс для скілів = Шанс подвійної атаки спорядження / 2
        bonuses = self.calculate_equipment_bonuses()
        base_da_chance = bonuses.get('double_attack_chance', 0)
        skill_da_chance = base_da_chance // 2

        # Логіка ефектів
        if skill["type"] == "damage_phys":
            phys_dmg, _ = self.calculate_hero_damage(hero)
            dmg = int(phys_dmg * skill["value"])
            # Передаємо override_da_chance, щоб attack_enemy обробив подвійну атаку
            msg_atk, _, _ = self.attack_enemy(phys_dmg=dmg, magic_dmg=0, override_da_chance=skill_da_chance)
            msg = f"Використано {skill['name']}!\n{msg_atk}"

        elif skill["type"] == "damage_magic":
            _, magic_dmg = self.calculate_hero_damage(hero)
            if magic_dmg == 0: magic_dmg = hero.int_stat * 2
            dmg = int(magic_dmg * skill["value"])
            msg_atk, _, _ = self.attack_enemy(phys_dmg=0, magic_dmg=dmg, override_da_chance=skill_da_chance)
            msg = f"Використано {skill['name']}!\n{msg_atk}"

        elif skill["type"] == "heal":
            heal = int(hero.max_hp * skill["value"])

            # Власна логіка подвійної дії для лікування
            is_double_heal = False
            if skill_da_chance > 0 and random.randint(1, 100) <= skill_da_chance:
                is_double_heal = True
                # Додаємо 50% ефекту як "друге спрацювання"
                heal_bonus = int(heal * 0.5)
                heal += heal_bonus
                msg = f"✨ ПОДВІЙНЕ ЛІКУВАННЯ! ✨\nВикористано {skill['name']}! Відновлено {heal} HP (основа + бонус)."
            else:
                msg = f"Використано {skill['name']}! Відновлено {heal} HP."

            hero.hp = min(hero.hp + heal, hero.max_hp)
            self.storage.update_hero(hero)

        elif skill["type"] == "buff":
            hero.buff_multiplier = skill["value"]
            msg = f"Використано {skill['name']}! Наступна атака посилена на 50%."
            self.storage.update_hero(hero)

        elif skill["type"] == "ultimate":
            dmg = int(enemy.current_hp * skill["value"]) + 1
            # Ультімейт також може спрацювати двічі (як фіз урон)
            msg_atk, _, _ = self.attack_enemy(phys_dmg=dmg, magic_dmg=0, override_da_chance=skill_da_chance)
            msg = f"Використано {skill['name']}!\n{msg_atk}"

        return msg