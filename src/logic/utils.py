class ValidationUtils:
    """
    Утилітний клас для перевірки вхідних даних.
    Використовується в quest_logic.py та habit_logic.py.
    """
    @staticmethod
    def validate_title(title: str) -> bool:
        return bool(title and title.strip())