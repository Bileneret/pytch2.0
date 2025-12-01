import json
import os
from typing import Optional

SESSION_FILE = "session.json"


class SessionManager:
    """
    Керує файлом сесії для автоматичного входу.
    """

    @staticmethod
    def save_session(hero_id: str):
        """Зберігає ID поточного героя у файл."""
        data = {"current_hero_id": hero_id}
        with open(SESSION_FILE, "w") as f:
            json.dump(data, f)

    @staticmethod
    def load_session() -> Optional[str]:
        """
        Повертає ID героя, якщо сесія існує.
        Якщо ні - повертає None.
        """
        if not os.path.exists(SESSION_FILE):
            return None

        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                return data.get("current_hero_id")
        except:
            return None

    @staticmethod
    def clear_session():
        """Видаляє файл сесії (вихід з акаунту)."""
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)