from ..models import Hero, HeroClass, Gender
from ..session import SessionManager


class AuthService:
    def __init__(self, storage):
        self.storage = storage

    def register(self, nickname: str, h_class: HeroClass, gender: Gender, appearance: str) -> Hero:
        if not nickname or not nickname.strip():
            raise ValueError("Введіть нікнейм!")

        hero = Hero(nickname=nickname, hero_class=h_class, gender=gender, appearance=appearance)
        # Оновлюємо похідні стати (HP/Mana) при створенні
        hero.update_derived_stats()
        # При створенні HP повне
        hero.hp = hero.max_hp
        hero.mana = hero.max_mana

        self.storage.create_hero(hero)
        SessionManager.save_session(str(hero.id))
        return hero

    def login(self, nickname: str) -> Hero:
        hero = self.storage.get_hero_by_nickname(nickname)
        if not hero:
            raise ValueError("Героя з таким нікнеймом не знайдено.")
        SessionManager.save_session(str(hero.id))
        return hero

    def logout(self):
        SessionManager.clear_session()

    def get_current_user_id(self):
        return SessionManager.load_session()