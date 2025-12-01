import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


# --- Enums ---
class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EPIC = 4


class HeroClass(Enum):
    WARRIOR = "Воїн"
    ARCHER = "Лучник"
    MAGE = "Маг"
    ROGUE = "Розбійник"


class Gender(Enum):
    MALE = "Чоловік"
    FEMALE = "Жінка"


class EnemyRarity(Enum):
    EASY = "Легкий"
    MEDIUM = "Середній"
    HARD = "Складний"
    BOSS = "Бос"


# НОВЕ: Тип нанесення урону
class DamageType(Enum):
    PHYSICAL = "Фізичний"
    MAGICAL = "Магічний"


# --- Models ---
@dataclass
class Hero:
    nickname: str
    hero_class: HeroClass
    gender: Gender
    appearance: str

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    level: int = 1
    current_xp: int = 0
    xp_to_next_level: int = 100
    gold: int = 0
    streak_days: int = 0
    hp: int = 100
    max_hp: int = 100

    # Характеристики
    stat_points: int = 0
    str_stat: int = 0  # Сила
    int_stat: int = 0  # Інтелект
    dex_stat: int = 0  # Спритність
    vit_stat: int = 0  # Витривалість
    def_stat: int = 0  # Захист

    mana: int = 10
    max_mana: int = 10

    base_damage: int = 15

    last_login: datetime = field(default_factory=datetime.now)

    def update_derived_stats(self):
        """Оновлює HP та Ману на основі статів."""
        self.max_hp = 100 + (self.vit_stat * 5)
        self.max_mana = 10 + (self.int_stat * 5)


@dataclass
class Enemy:
    name: str
    rarity: EnemyRarity
    level: int
    current_hp: int
    max_hp: int
    damage: int
    # НОВЕ: Тип атаки ворога
    damage_type: DamageType

    reward_xp: int
    reward_gold: int
    drop_chance: float
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    image_path: str = ""


@dataclass
class SubGoal:
    title: str
    is_completed: bool = False
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def mark_done(self): self.is_completed = True

    def mark_undone(self): self.is_completed = False


@dataclass
class Goal:
    title: str
    description: str
    deadline: datetime
    difficulty: Difficulty = Difficulty.EASY
    created_at: datetime = field(default_factory=datetime.now)
    is_completed: bool = False
    penalty_applied: bool = False
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    subgoals: List[SubGoal] = field(default_factory=list)

    def add_subgoal(self, subgoal: SubGoal):
        self.subgoals.append(subgoal)

    def calculate_progress(self) -> float:
        if not self.subgoals:
            return 100.0 if self.is_completed else 0.0
        completed_count = sum(1 for sg in self.subgoals if sg.is_completed)
        return (completed_count / len(self.subgoals)) * 100.0

    def is_overdue(self) -> bool:
        if self.is_completed: return False
        return datetime.now() > self.deadline


@dataclass
class LongTermGoal:
    title: str
    description: str
    total_days: int
    start_date: datetime
    time_frame: str = ""
    current_day: int = 1
    checked_days: int = 0
    missed_days: int = 0
    is_completed: bool = False
    is_failed: bool = False
    daily_state: str = "pending"
    last_update_date: Optional[datetime] = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def calculate_progress(self) -> float:
        return (self.current_day / self.total_days) * 100.0