from datetime import datetime, timedelta
from typing import List, Tuple
from ..models import LongTermGoal
from ..longterm_mechanics import LongTermManager


class HabitLogic:
    """Міксин: Звички."""

    def create_long_term_goal(self, title: str, description: str, total_days: int, time_frame: str):
        if not title or not title.strip():
            raise ValueError("Назва не може бути порожньою!")
        # Старт завтра
        start_date = datetime.now() + timedelta(days=1)
        quest = LongTermGoal(title=title, description=description, total_days=total_days, start_date=start_date,
                             time_frame=time_frame, daily_state='pending')
        self.storage.save_long_term_goal(quest, self.hero_id)

    def delete_long_term_goal(self, goal_id):
        """Видаляє звичку."""
        self.storage.delete_long_term_goal(goal_id)

    def get_long_term_goals(self, custom_now: datetime = None) -> Tuple[List[LongTermGoal], List[str]]:
        goals = self.storage.load_long_term_goals(self.hero_id)
        hero = self.get_hero()
        enemy = self.get_current_enemy()
        alerts = []
        updated_hero = False

        current_dt = custom_now if custom_now else datetime.now()
        today_date = current_dt.date()

        for goal in goals:
            if today_date < goal.start_date.date(): continue

            # Перевірка зміни дня
            if goal.last_update_date and goal.last_update_date.date() < today_date:
                if goal.daily_state in ['pending', 'started']:
                    goal.missed_days += 1
                    dmg_dealt = self.take_damage(hero, enemy)
                    if dmg_dealt == 0:
                        alerts.append(f"📅 Пропущено день звички '{goal.title}'!\n💨 УХИЛЕННЯ!")
                    else:
                        alerts.append(f"📅 Пропущено день звички '{goal.title}'!\n💥 {dmg_dealt} урону.")
                    updated_hero = True

                goal.daily_state = 'pending'
                days_passed = (today_date - goal.start_date.date()).days + 1
                goal.current_day = min(days_passed, goal.total_days)
                goal.last_update_date = current_dt
                self.storage.save_long_term_goal(goal, self.hero_id)

            # Перевірка таймінгів
            habit_alerts = self.check_habit_deadlines(goal, current_dt, enemy, hero)
            if habit_alerts:
                alerts.extend(habit_alerts)
                updated_hero = True
                self.storage.save_long_term_goal(goal, self.hero_id)

        if updated_hero:
            self.storage.update_hero(hero)
        return goals, alerts

    def check_habit_deadlines(self, goal: LongTermGoal, now: datetime, enemy, hero) -> List[str]:
        if now.date() < goal.start_date.date(): return []
        alerts = []
        try:
            t_start_str, t_end_str = goal.time_frame.split(" - ")
            t_start = datetime.strptime(t_start_str, "%H:%M").time()
            t_end = datetime.strptime(t_end_str, "%H:%M").time()
            dt_start = datetime.combine(now.date(), t_start)
            dt_end = datetime.combine(now.date(), t_end)
            deadline_start = dt_start + timedelta(minutes=5)
            deadline_end = dt_end + timedelta(minutes=5)

            fail_msg = ""
            trigger_fail = False

            if now > deadline_start and goal.daily_state == 'pending':
                trigger_fail = True
                fail_msg = f"⏰ Час старту звички '{goal.title}' пропущено!"
            elif now > deadline_end and goal.daily_state == 'started':
                trigger_fail = True
                fail_msg = f"⏰ Час завершення звички '{goal.title}' пропущено!"

            if trigger_fail:
                goal.daily_state = 'failed'
                goal.missed_days += 1
                dmg_dealt = self.take_damage(hero, enemy)
                if dmg_dealt == 0:
                    alerts.append(f"{fail_msg}\n💨 УХИЛЕННЯ!")
                else:
                    alerts.append(f"{fail_msg}\n💥 {dmg_dealt} урону.")

        except ValueError:
            pass
        return alerts

    def checkin_long_term(self, goal: LongTermGoal, custom_now: datetime = None) -> Tuple[str, bool]:
        return self.finish_habit(goal, custom_now)

    def start_habit(self, goal: LongTermGoal, custom_now: datetime = None):
        current_dt = custom_now if custom_now else datetime.now()
        goal.daily_state = 'started'
        goal.last_update_date = current_dt
        self.storage.save_long_term_goal(goal, self.hero_id)
        return "Звичку розпочато!"

    def finish_habit(self, goal: LongTermGoal, custom_now: datetime = None):
        current_dt = custom_now if custom_now else datetime.now()
        hero = self.get_hero()
        xp, gold = LongTermManager.calculate_interval_reward()
        self._add_rewards(hero, xp, gold)

        goal.daily_state = 'finished'
        goal.checked_days += 1
        goal.last_update_date = current_dt

        msg = f"Звичку зараховано! +{xp} XP, +{gold} Gold"

        if goal.current_day >= goal.total_days:
            goal.is_completed = True
            report, final_xp, final_gold = LongTermManager.finalize_quest(goal, hero)
            self._add_rewards(hero, final_xp, final_gold)
            msg += f"\n\n🏁 ЧЕЛЕНДЖ ЗАВЕРШЕНО!\n{report}"

        self.storage.save_long_term_goal(goal, self.hero_id)
        return msg