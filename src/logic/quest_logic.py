from datetime import datetime, timedelta
from typing import List
from ..models import Goal, Difficulty, DamageType
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

        goal.is_completed = True
        self.storage.save_goal(goal, self.hero_id)

        hero = self.get_hero()
        xp_reward, gold_reward = self._calculate_rewards(goal)
        self._add_rewards(hero, xp_reward, gold_reward)

        # Атака (0,0 = авто)
        attack_msg, killed, loot = self.attack_enemy(0, 0)

        # ВИПРАВЛЕНО: gold -> gold_reward
        return f"Квест завершено!\n+{xp_reward} XP, +{gold_reward} Gold\n{attack_msg}"

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