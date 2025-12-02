import json
import uuid
from datetime import datetime, timedelta
from typing import List
from ..models import Goal, Difficulty, DamageType, Enemy, EnemyRarity
from .utils import ValidationUtils


class QuestLogic:
    """Міксин: Звичайні квести."""

    def create_goal(self, title: str, description: str, deadline: datetime, difficulty: Difficulty) -> Goal:
        if not ValidationUtils.validate_title(title):
            raise ValueError("Назва не може бути порожньою!")
        new_goal = Goal(title=title.strip(), description=description.strip(), deadline=deadline, difficulty=difficulty)
        self.storage.save_goal(new_goal, self.hero_id)
        return new_goal

    def get_all_goals(self) -> List[Goal]:
        return self.storage.load_goals(self.hero_id)

    def delete_goal(self, goal_id):
        self.storage.delete_goal(goal_id)

    def complete_goal(self, goal: Goal) -> str:
        if goal.is_completed: return "Вже виконано"

        hero = self.get_hero()
        enemy = self.get_current_enemy()

        # --- SNAPSHOT: Зберігаємо стан героя ТА ворога ---
        hero_snapshot = {
            "level": hero.level,
            "current_xp": hero.current_xp,
            "xp_to_next_level": hero.xp_to_next_level,
            "gold": hero.gold,
            "hp": hero.hp,
            "mana": hero.mana,
            "stat_points": hero.stat_points,
            "str_stat": hero.str_stat,
            "int_stat": hero.int_stat,
            "dex_stat": hero.dex_stat,
            "vit_stat": hero.vit_stat,
            "def_stat": hero.def_stat
        }

        enemy_snapshot = {
            "id": str(enemy.id),
            "name": enemy.name,
            "rarity": enemy.rarity.value,
            "level": enemy.level,
            "current_hp": enemy.current_hp,
            "max_hp": enemy.max_hp,
            "damage": enemy.damage,
            "damage_type": enemy.damage_type.value,
            "reward_xp": enemy.reward_xp,
            "reward_gold": enemy.reward_gold,
            "drop_chance": enemy.drop_chance,
            "image_path": enemy.image_path
        }

        full_snapshot = {
            "hero": hero_snapshot,
            "enemy": enemy_snapshot
        }

        goal.previous_state = json.dumps(full_snapshot)

        goal.is_completed = True
        self.storage.save_goal(goal, self.hero_id)

        xp_reward, gold_reward = self._calculate_rewards(goal)
        self._add_rewards(hero, xp_reward, gold_reward)

        # Атака (0,0 = авто)
        attack_msg, killed, loot = self.attack_enemy(0, 0)

        return f"Квест завершено!\n+{xp_reward} XP, +{gold_reward} Gold\n{attack_msg}"

    def undo_complete_goal(self, goal: Goal) -> str:
        """
        Скасовує виконання квесту:
        1. Відновлює стан героя (рівень, мани, hp).
        2. Відновлює стан ворога (hp, або воскрешає попереднього).
        """
        if not goal.is_completed:
            return "Ціль ще не виконана."

        hero = self.get_hero()

        # Спроба відновити з snapshot
        if goal.previous_state:
            try:
                full_data = json.loads(goal.previous_state)

                # 1. Відновлення Героя
                hero_data = full_data.get("hero")
                if hero_data:
                    # self.restore_hero_state знаходиться в HeroLogic (міксин)
                    self.restore_hero_state(hero, hero_data)

                # 2. Відновлення Ворога
                enemy_data = full_data.get("enemy")
                if enemy_data:
                    restored_enemy = Enemy(
                        id=uuid.UUID(enemy_data["id"]),
                        name=enemy_data["name"],
                        rarity=EnemyRarity(enemy_data["rarity"]),
                        level=enemy_data["level"],
                        current_hp=enemy_data["current_hp"],
                        max_hp=enemy_data["max_hp"],
                        damage=enemy_data["damage"],
                        damage_type=DamageType(enemy_data["damage_type"]),
                        reward_xp=enemy_data["reward_xp"],
                        reward_gold=enemy_data["reward_gold"],
                        drop_chance=enemy_data["drop_chance"],
                        image_path=enemy_data["image_path"]
                    )
                    # Зберігаємо відновленого ворога в базу
                    self.storage.save_enemy(restored_enemy, self.hero_id)

                # Очищаємо snapshot після відновлення
                goal.previous_state = ""
                goal.is_completed = False
                self.storage.save_goal(goal, self.hero_id)

                return "Виконання скасовано. Стан героя та ворога відновлено."
            except Exception as e:
                print(f"Error restoring state: {e}")
                # Fallback, якщо щось пішло не так

        # --- ФОЛБЕК (лише математичний відкат, якщо немає снепшота) ---
        goal.is_completed = False
        self.storage.save_goal(goal, self.hero_id)

        xp_reward, gold_reward = self._calculate_rewards(goal)
        hero.gold = max(0, hero.gold - gold_reward)
        hero.current_xp = max(0, hero.current_xp - xp_reward)
        self.storage.update_hero(hero)

        return f"Нагороди скасовано (частковий відкат): -{xp_reward} XP, -{gold_reward} Gold"

    def check_deadlines(self, custom_now: datetime = None) -> List[str]:
        hero = self.get_hero()
        enemy = self.get_current_enemy()
        goals = self.get_all_goals()
        alerts = []
        damage_taken = False
        now = custom_now if custom_now else datetime.now()

        for goal in goals:
            # 5 хвилин толерантності
            deadline_with_grace = goal.deadline + timedelta(minutes=5)

            if not goal.is_completed and not goal.penalty_applied and now > deadline_with_grace:
                dmg_dealt = self.take_damage(hero, enemy)

                goal.penalty_applied = True
                self.storage.save_goal(goal, self.hero_id)
                damage_taken = True

                type_str = "Магічного" if enemy.damage_type == DamageType.MAGICAL else "Фізичного"
                if dmg_dealt == 0:
                    alerts.append(f"⏰ Дедлайн квесту '{goal.title}' пропущено!\n💨 Ви УХИЛИЛИСЯ від атаки!")
                else:
                    alerts.append(
                        f"⏰ Дедлайн квесту '{goal.title}' пропущено!\n💥 {enemy.name} наніс {dmg_dealt} {type_str} урону!")

        if damage_taken:
            self.storage.update_hero(hero)
        return alerts

    def _calculate_rewards(self, goal: Goal):
        rewards = {Difficulty.EASY: 50, Difficulty.MEDIUM: 100, Difficulty.HARD: 200, Difficulty.EPIC: 500}
        xp = rewards.get(goal.difficulty, 50)
        return xp, xp