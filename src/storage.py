import sqlite3
import uuid
import os
import sys
import re
from datetime import datetime
from typing import List, Optional
from .models import (
    Goal, SubGoal, Hero, Difficulty, LongTermGoal, HeroClass, Gender,
    Enemy, EnemyRarity, DamageType, Item, ItemType, EquipmentSlot, InventoryItem,
    WeaponClass, WeaponHandType
)


def get_project_root():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


class StorageService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
        self.seed_items_from_folder()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        # Heroes
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS heroes (
                        id TEXT PRIMARY KEY,
                        nickname TEXT UNIQUE NOT NULL,
                        hero_class TEXT,
                        gender TEXT,
                        appearance TEXT,
                        level INTEGER DEFAULT 1,
                        current_xp INTEGER DEFAULT 0,
                        xp_to_next_level INTEGER DEFAULT 100,
                        gold INTEGER DEFAULT 0,
                        streak_days INTEGER DEFAULT 0,
                        hp INTEGER DEFAULT 100,
                        max_hp INTEGER DEFAULT 100,
                        stat_points INTEGER DEFAULT 0,
                        str_stat INTEGER DEFAULT 0,
                        int_stat INTEGER DEFAULT 0,
                        dex_stat INTEGER DEFAULT 0,
                        vit_stat INTEGER DEFAULT 0,
                        def_stat INTEGER DEFAULT 0,
                        mana INTEGER DEFAULT 10,
                        max_mana INTEGER DEFAULT 10,
                        buff_multiplier REAL DEFAULT 1.0,
                        last_login TEXT
                    )
                """)

        # Goals (з полем previous_state)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY, 
                hero_id TEXT NOT NULL, 
                title TEXT NOT NULL, 
                description TEXT, 
                deadline TEXT, 
                difficulty INTEGER, 
                created_at TEXT, 
                is_completed INTEGER DEFAULT 0, 
                penalty_applied INTEGER DEFAULT 0, 
                previous_state TEXT DEFAULT '',
                FOREIGN KEY (hero_id) REFERENCES heroes (id) ON DELETE CASCADE
            )
        """)

        # Міграція для goals (якщо бази вже створені)
        try:
            cursor.execute("ALTER TABLE goals ADD COLUMN previous_state TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass

        # Sub Goals
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sub_goals (
                id TEXT PRIMARY KEY, 
                goal_id TEXT NOT NULL, 
                title TEXT NOT NULL, 
                description TEXT DEFAULT '',
                is_completed INTEGER DEFAULT 0, 
                FOREIGN KEY (goal_id) REFERENCES goals (id) ON DELETE CASCADE
            )
        """)

        # Міграція для sub_goals
        try:
            cursor.execute("ALTER TABLE sub_goals ADD COLUMN description TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS long_term_goals (id TEXT PRIMARY KEY, hero_id TEXT NOT NULL, title TEXT NOT NULL, description TEXT, total_days INTEGER, start_date TEXT, time_frame TEXT, current_day INTEGER DEFAULT 1, checked_days INTEGER DEFAULT 0, missed_days INTEGER DEFAULT 0, is_completed INTEGER DEFAULT 0, daily_state TEXT DEFAULT 'pending', last_update_date TEXT, FOREIGN KEY (hero_id) REFERENCES heroes (id) ON DELETE CASCADE)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS current_enemies (hero_id TEXT PRIMARY KEY, id TEXT NOT NULL, name TEXT, rarity TEXT, level INTEGER, current_hp INTEGER, max_hp INTEGER, damage INTEGER, damage_type TEXT, reward_xp INTEGER, reward_gold INTEGER, drop_chance REAL, image_path TEXT, FOREIGN KEY (hero_id) REFERENCES heroes (id) ON DELETE CASCADE)")

        # Items Library
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items_library (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                item_type TEXT,
                slot TEXT,
                weapon_class TEXT,
                weapon_hands TEXT,
                damage_type TEXT,
                bonus_str INTEGER DEFAULT 0,
                bonus_int INTEGER DEFAULT 0,
                bonus_dex INTEGER DEFAULT 0,
                bonus_vit INTEGER DEFAULT 0,
                bonus_def INTEGER DEFAULT 0,
                base_dmg INTEGER DEFAULT 0,
                double_attack_chance INTEGER DEFAULT 0,
                price INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                image_path TEXT UNIQUE
            )
        """)

        try:
            cursor.execute("ALTER TABLE items_library ADD COLUMN double_attack_chance INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        # Inventory
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id TEXT PRIMARY KEY,
                hero_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                is_equipped INTEGER DEFAULT 0,
                FOREIGN KEY (hero_id) REFERENCES heroes (id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES items_library (id)
            )
        """)

        conn.commit()
        conn.close()

    def seed_items_from_folder(self):
        base_path = get_project_root()
        items_path = os.path.join(base_path, "assets", "items")

        if not os.path.exists(items_path): return

        files = os.listdir(items_path)
        conn = self._get_connection()
        cursor = conn.cursor()

        pattern_6 = re.compile(r"^(.*)_(\d+)_(\d+)_(\d+)_(\d+)_(\d+)_(\d+)\.png$", re.IGNORECASE)
        pattern_5 = re.compile(r"^(.*)_(\d+)_(\d+)_(\d+)_(\d+)_(\d+)\.png$", re.IGNORECASE)

        for filename in files:
            match = pattern_6.match(filename)
            double_attack = 0

            if match:
                raw_name = match.group(1)
                str_val = int(match.group(2))
                int_val = int(match.group(3))
                dex_val = int(match.group(4))
                vit_val = int(match.group(5))
                def_val = int(match.group(6))
                double_attack = int(match.group(7))
            else:
                match = pattern_5.match(filename)
                if match:
                    raw_name = match.group(1)
                    str_val = int(match.group(2))
                    int_val = int(match.group(3))
                    dex_val = int(match.group(4))
                    vit_val = int(match.group(5))
                    def_val = int(match.group(6))
                else:
                    continue

            clean_name = raw_name.replace("_", " ")
            item_type, slot, w_class = self._guess_item_type_and_slot(clean_name)

            price = 250
            lower = clean_name.lower()
            if "заліз" in lower or "iron" in lower:
                price = 750
            elif "крилат" in lower or "wing" in lower:
                price = 1250
            elif "крижан" in lower or "ice" in lower:
                price = 1750
            elif "вогн" in lower or "fire" in lower:
                price = 2500
            elif "профес" in lower:
                price = 750

            base_dmg = 0
            if item_type == ItemType.WEAPON:
                if w_class == WeaponClass.SHIELD:
                    base_dmg = 0
                else:
                    base_dmg = max(str_val, int_val, dex_val) * 2
                    if base_dmg == 0: base_dmg = 5

            try:
                item_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT OR IGNORE INTO items_library (
                        id, name, item_type, slot, weapon_class, weapon_hands, damage_type,
                        bonus_str, bonus_int, bonus_dex, bonus_vit, bonus_def, base_dmg,
                        double_attack_chance, price, level, image_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_id, clean_name, item_type.value, slot.value,
                    w_class.value, WeaponHandType.ONE_HANDED.value, DamageType.PHYSICAL.value,
                    str_val, int_val, dex_val, vit_val, def_val, base_dmg,
                    double_attack, price, 1, filename
                ))

                cursor.execute("""
                    UPDATE items_library 
                    SET base_dmg = ?, double_attack_chance = ?, 
                        bonus_str = ?, bonus_int = ?, bonus_dex = ?, bonus_vit = ?, bonus_def = ?
                    WHERE image_path = ?
                """, (base_dmg, double_attack, str_val, int_val, dex_val, vit_val, def_val, filename))

            except Exception as e:
                print(f"Error adding item {filename}: {e}")

        conn.commit()
        conn.close()

    def _guess_item_type_and_slot(self, name: str):
        name_lower = name.lower()
        if any(x in name_lower for x in
               ["меч", "sword", "клинок"]): return ItemType.WEAPON, EquipmentSlot.MAIN_HAND, WeaponClass.SWORD
        if any(
                x in name_lower for x in
                ["лук", "bow"]): return ItemType.WEAPON, EquipmentSlot.MAIN_HAND, WeaponClass.BOW
        if any(x in name_lower for x in
               ["посох", "staff"]): return ItemType.WEAPON, EquipmentSlot.MAIN_HAND, WeaponClass.STAFF
        if any(x in name_lower for x in
               ["кинджал", "ніж", "dagger"]): return ItemType.WEAPON, EquipmentSlot.MAIN_HAND, WeaponClass.DAGGER
        if any(x in name_lower for x in
               ["щит", "shield"]): return ItemType.WEAPON, EquipmentSlot.OFF_HAND, WeaponClass.SHIELD

        if any(x in name_lower for x in
               ["шолом", "капелюх", "шлем", "hat"]): return ItemType.ARMOR, EquipmentSlot.HEAD, WeaponClass.NONE
        if any(x in name_lower for x in ["обладунок", "тіло", "куртка", "сорочка",
                                         "chest"]): return ItemType.ARMOR, EquipmentSlot.BODY, WeaponClass.NONE
        if any(x in name_lower for x in
               ["штани", "поножі", "legs"]): return ItemType.ARMOR, EquipmentSlot.LEGS, WeaponClass.NONE
        if any(x in name_lower for x in
               ["чоботи", "взуття", "черевики", "чобіт",
                "boots"]): return ItemType.ARMOR, EquipmentSlot.FEET, WeaponClass.NONE
        if any(x in name_lower for x in
               ["рукавиці", "перчатки", "gloves"]): return ItemType.ARMOR, EquipmentSlot.HANDS, WeaponClass.NONE

        return ItemType.WEAPON, EquipmentSlot.MAIN_HAND, WeaponClass.NONE

    def add_item_to_inventory(self, hero_id: str, item: Item):
        conn = self._get_connection()
        inv_id = uuid.uuid4()
        conn.execute("INSERT INTO inventory (id, hero_id, item_id, is_equipped) VALUES (?, ?, ?, 0)",
                     (str(inv_id), hero_id, str(item.id)))
        conn.commit()
        conn.close()

    def get_inventory(self, hero_id: str) -> List[InventoryItem]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = "SELECT inv.id, inv.is_equipped, lib.* FROM inventory inv JOIN items_library lib ON inv.item_id = lib.id WHERE inv.hero_id = ?"
        cursor.execute(query, (hero_id,))
        rows = cursor.fetchall()
        conn.close()
        inventory = []
        for row in rows:
            item_type = next((t for t in ItemType if t.value == row[4]), None)
            slot = next((s for s in EquipmentSlot if s.value == row[5]), None)

            item = Item(
                id=uuid.UUID(row[2]),
                name=row[3],
                item_type=item_type,
                slot=slot,
                bonus_str=row[9],
                bonus_int=row[10],
                bonus_dex=row[11],
                bonus_vit=row[12],
                bonus_def=row[13],
                base_dmg=row[14],
                double_attack_chance=row[15],
                price=row[16],
                level=row[17],
                image_path=row[18]
            )
            inventory.append(InventoryItem(item=item, is_equipped=bool(row[1]), id=uuid.UUID(row[0])))
        return inventory

    def equip_item(self, hero_id: str, inventory_id: uuid.UUID, slot_value: str):
        conn = self._get_connection()
        conn.execute(
            "UPDATE inventory SET is_equipped = 0 WHERE hero_id = ? AND is_equipped = 1 AND item_id IN (SELECT id FROM items_library WHERE slot = ?)",
            (hero_id, slot_value))
        conn.execute("UPDATE inventory SET is_equipped = 1 WHERE id = ?", (str(inventory_id),))
        conn.commit()
        conn.close()

    def unequip_item(self, inventory_id: uuid.UUID):
        conn = self._get_connection()
        conn.execute("UPDATE inventory SET is_equipped = 0 WHERE id = ?", (str(inventory_id),))
        conn.commit()
        conn.close()

    def get_all_library_items(self) -> List[Item]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items_library")
        rows = cursor.fetchall()
        conn.close()
        items = []
        for row in rows:
            item_type = next((t for t in ItemType if t.value == row[2]), None)
            slot = next((s for s in EquipmentSlot if s.value == row[3]), None)
            item = Item(
                id=uuid.UUID(row[0]),
                name=row[1],
                item_type=item_type,
                slot=slot,
                bonus_str=row[7],
                bonus_int=row[8],
                bonus_dex=row[9],
                bonus_vit=row[10],
                bonus_def=row[11],
                base_dmg=row[12],
                double_attack_chance=row[13],
                price=row[14],
                level=row[15],
                image_path=row[16]
            )
            items.append(item)
        return items

    def create_hero(self, hero: Hero):
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO heroes (
                    id, nickname, hero_class, gender, appearance, level, hp, max_hp, last_login,
                    stat_points, str_stat, int_stat, dex_stat, vit_stat, def_stat, mana, max_mana, buff_multiplier
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(hero.id), hero.nickname, hero.hero_class.value, hero.gender.value,
                hero.appearance, hero.level, hero.hp, hero.max_hp, hero.last_login.isoformat(),
                hero.stat_points, hero.str_stat, hero.int_stat, hero.dex_stat,
                hero.vit_stat, hero.def_stat, hero.mana, hero.max_mana, hero.buff_multiplier
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Цей нікнейм вже зайнятий!")
        finally:
            conn.close()

    def get_hero_by_nickname(self, nickname: str) -> Optional[Hero]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM heroes WHERE nickname = ?", (nickname,))
        row = cursor.fetchone()
        conn.close()
        return self._map_row_to_hero(row) if row else None

    def get_hero_by_id(self, hero_id: str) -> Optional[Hero]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM heroes WHERE id = ?", (hero_id,))
        row = cursor.fetchone()
        conn.close()
        return self._map_row_to_hero(row) if row else None

    def _map_row_to_hero(self, row) -> Hero:
        return Hero(
            id=uuid.UUID(row[0]), nickname=row[1], hero_class=HeroClass(row[2]), gender=Gender(row[3]),
            appearance=row[4],
            level=row[5], current_xp=row[6], xp_to_next_level=row[7], gold=row[8], streak_days=row[9], hp=row[10],
            max_hp=row[11],
            stat_points=row[12], str_stat=row[13], int_stat=row[14], dex_stat=row[15],
            vit_stat=row[16], def_stat=row[17], mana=row[18], max_mana=row[19],
            buff_multiplier=row[20],
            last_login=datetime.fromisoformat(row[21])
        )

    def update_hero(self, hero: Hero):
        conn = self._get_connection()
        conn.execute("""
            UPDATE heroes SET 
                level=?, current_xp=?, xp_to_next_level=?, gold=?, streak_days=?, hp=?, max_hp=?, last_login=?,
                stat_points=?, str_stat=?, int_stat=?, dex_stat=?, vit_stat=?, def_stat=?, mana=?, max_mana=?, buff_multiplier=?
            WHERE id=?
        """, (
            hero.level, hero.current_xp, hero.xp_to_next_level, hero.gold, hero.streak_days,
            hero.hp, hero.max_hp, hero.last_login.isoformat(),
            hero.stat_points, hero.str_stat, hero.int_stat, hero.dex_stat,
            hero.vit_stat, hero.def_stat, hero.mana, hero.max_mana, hero.buff_multiplier,
            str(hero.id)
        ))
        conn.commit()
        conn.close()

    def save_goal(self, goal: Goal, hero_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Оновлено запит для збереження previous_state
            cursor.execute(
                "INSERT OR REPLACE INTO goals (id, hero_id, title, description, deadline, difficulty, created_at, is_completed, penalty_applied, previous_state) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (str(goal.id), hero_id, goal.title, goal.description, goal.deadline.isoformat(), goal.difficulty.value,
                 goal.created_at.isoformat(), 1 if goal.is_completed else 0, 1 if goal.penalty_applied else 0,
                 goal.previous_state))

            cursor.execute("DELETE FROM sub_goals WHERE goal_id = ?", (str(goal.id),))
            for sub in goal.subgoals:
                cursor.execute(
                    "INSERT INTO sub_goals (id, goal_id, title, description, is_completed) VALUES (?, ?, ?, ?, ?)",
                    (str(sub.id), str(goal.id), sub.title, sub.description, 1 if sub.is_completed else 0))
            conn.commit()
        finally:
            conn.close()

    def load_goals(self, hero_id: str) -> List[Goal]:
        conn = self._get_connection()
        cursor = conn.cursor()
        goals_list = []
        # Оновлено запит для завантаження previous_state
        cursor.execute(
            "SELECT id, title, description, deadline, difficulty, created_at, is_completed, penalty_applied, previous_state FROM goals WHERE hero_id = ?",
            (hero_id,))
        rows = cursor.fetchall()
        for row in rows:
            g_id, title, desc, dl_str, diff_val, ca_str, is_comp, is_penalized, prev_state = row
            goal = Goal(title=title, description=desc, deadline=datetime.fromisoformat(dl_str),
                        difficulty=Difficulty(diff_val))
            goal.id = uuid.UUID(g_id)
            goal.created_at = datetime.fromisoformat(ca_str)
            goal.is_completed = bool(is_comp)
            goal.penalty_applied = bool(is_penalized)
            # prev_state може бути None у старих БД, тому ставимо ""
            goal.previous_state = prev_state if prev_state else ""

            cursor.execute("SELECT id, title, is_completed, description FROM sub_goals WHERE goal_id = ?", (g_id,))
            for s_row in cursor.fetchall():
                description_val = s_row[3] if s_row[3] is not None else ""
                sub = SubGoal(title=s_row[1], description=description_val)
                sub.id = uuid.UUID(s_row[0])
                sub.is_completed = bool(s_row[2])
                goal.add_subgoal(sub)
            goals_list.append(goal)
        conn.close()
        return goals_list

    def delete_goal(self, goal_id: uuid.UUID):
        conn = self._get_connection()
        conn.execute("DELETE FROM goals WHERE id = ?", (str(goal_id),))
        conn.commit()
        conn.close()

    def save_long_term_goal(self, goal: LongTermGoal, hero_id: str):
        conn = self._get_connection()
        last_update = goal.last_update_date.isoformat() if goal.last_update_date else None
        conn.execute(
            "INSERT OR REPLACE INTO long_term_goals (id, hero_id, title, description, total_days, start_date, time_frame, current_day, checked_days, missed_days, is_completed, daily_state, last_update_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (str(goal.id), hero_id, goal.title, goal.description, goal.total_days, goal.start_date.isoformat(),
             goal.time_frame, goal.current_day, goal.checked_days, goal.missed_days, 1 if goal.is_completed else 0,
             goal.daily_state, last_update))
        conn.commit()
        conn.close()

    def load_long_term_goals(self, hero_id: str) -> List[LongTermGoal]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM long_term_goals WHERE hero_id = ? AND is_completed = 0", (hero_id,))
        rows = cursor.fetchall()
        goals = []
        for row in rows:
            g = LongTermGoal(title=row[2], description=row[3], total_days=row[4],
                             start_date=datetime.fromisoformat(row[5]), time_frame=row[6])
            g.id = uuid.UUID(row[0])
            g.current_day = row[7]
            g.checked_days = row[8]
            g.missed_days = row[9]
            g.is_completed = bool(row[10])
            g.daily_state = row[11]
            if row[12]: g.last_update_date = datetime.fromisoformat(row[12])
            goals.append(g)
        conn.close()
        return goals

    def delete_long_term_goal(self, goal_id: uuid.UUID):
        """Видаляє довгострокову звичку з БД."""
        conn = self._get_connection()
        conn.execute("DELETE FROM long_term_goals WHERE id = ?", (str(goal_id),))
        conn.commit()
        conn.close()

    def save_enemy(self, enemy: Enemy, hero_id: str):
        conn = self._get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO current_enemies (hero_id, id, name, rarity, level, current_hp, max_hp, damage, damage_type, reward_xp, reward_gold, drop_chance, image_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (hero_id, str(enemy.id), enemy.name, enemy.rarity.value, enemy.level, enemy.current_hp, enemy.max_hp,
             enemy.damage, enemy.damage_type.value, enemy.reward_xp, enemy.reward_gold, enemy.drop_chance,
             enemy.image_path))
        conn.commit()
        conn.close()

    def load_enemy(self, hero_id: str) -> Optional[Enemy]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM current_enemies WHERE hero_id = ?", (hero_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Enemy(id=uuid.UUID(row[1]), name=row[2], rarity=EnemyRarity(row[3]), level=row[4], current_hp=row[5],
                         max_hp=row[6], damage=row[7], damage_type=DamageType(row[8]), reward_xp=row[9],
                         reward_gold=row[10], drop_chance=row[11], image_path=row[12])
        return None

    def delete_enemy(self, hero_id: str):
        conn = self._get_connection()
        conn.execute("DELETE FROM current_enemies WHERE hero_id = ?", (hero_id,))
        conn.commit()
        conn.close()