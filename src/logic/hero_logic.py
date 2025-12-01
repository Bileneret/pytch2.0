from datetime import datetime, timedelta


class HeroLogic:
    """Міксин: Управління станом героя."""

    def get_hero(self):
        # self.storage та self.hero_id будуть доступні в головному класі
        hero = self.storage.get_hero_by_id(self.hero_id)
        if not hero: raise ValueError("Помилка сесії")
        self._check_streak(hero)
        return hero

    def _check_streak(self, hero):
        today = datetime.now().date()
        last_login_date = hero.last_login.date()
        if today > last_login_date:
            if today == last_login_date + timedelta(days=1):
                hero.streak_days += 1
            else:
                hero.streak_days = 1
            hero.last_login = datetime.now()
            self.storage.update_hero(hero)

    def _check_level_up(self, hero):
        while hero.current_xp >= hero.xp_to_next_level:
            hero.current_xp -= hero.xp_to_next_level
            hero.level += 1
            hero.xp_to_next_level = int(hero.level * 100 * 1.5)

            # +1 Очко Характеристик
            hero.stat_points += 1

            # Оновлюємо статси і лікуємо
            hero.update_derived_stats()
            hero.hp = hero.max_hp
            hero.mana = hero.max_mana

    def _add_rewards(self, hero, xp: int, gold: int):
        hero.current_xp += xp
        hero.gold += gold
        self._check_level_up(hero)
        self.storage.update_hero(hero)