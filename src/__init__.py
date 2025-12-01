"""
Головний пакет додатку Learning Goals RPG.
Містить бізнес-логіку, моделі даних, роботу з БД та допоміжні сервіси.
"""

# Версія додатку
__version__ = '1.0.0'

# Імпортуємо основні моделі, щоб їх можна було дістати прямо з src
from .models import (
    Hero,
    Enemy,
    Goal,
    SubGoal,
    LongTermGoal,
    Difficulty,
    HeroClass,
    Gender,
    EnemyRarity
)

# Імпортуємо сервіси
from .storage import StorageService
from .logic import GoalService, AuthService
from .session import SessionManager
from .enemy_mechanics import EnemyGenerator
from .longterm_mechanics import LongTermManager

# Список того, що буде доступно, якщо хтось напише: from src import *
__all__ = [
    # Моделі
    'Hero', 'Enemy', 'Goal', 'SubGoal', 'LongTermGoal',
    'Difficulty', 'HeroClass', 'Gender', 'EnemyRarity',

    # Сервіси
    'StorageService',
    'GoalService',
    'AuthService',
    'SessionManager',

    # Механіки
    'EnemyGenerator',
    'LongTermManager'
]

