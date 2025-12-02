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

    def restore_hero_state(self, hero, state_data: dict):
        """Відновлює стан героя з словника (snapshot)."""
        hero.level = state_data.get('level', 1)
        hero.current_xp = state_data.get('current_xp', 0)
        hero.xp_to_next_level = state_data.get('xp_to_next_level', 100)
        hero.gold = state_data.get('gold', 0)

        # Відновлюємо стат поінти та характеристики
        hero.stat_points = state_data.get('stat_points', 0)
        hero.str_stat = state_data.get('str_stat', 0)
        hero.int_stat = state_data.get('int_stat', 0)
        hero.dex_stat = state_data.get('dex_stat', 0)
        hero.vit_stat = state_data.get('vit_stat', 0)
        hero.def_stat = state_data.get('def_stat', 0)

        # Оновлюємо похідні (max_hp, max_mana) перед встановленням поточних
        hero.update_derived_stats()

        # Відновлюємо поточні HP/Mana (навіть якщо вони були не повні)
        hero.hp = state_data.get('hp', hero.max_hp)
        hero.mana = state_data.get('mana', hero.max_mana)

        self.storage.update_hero(hero)