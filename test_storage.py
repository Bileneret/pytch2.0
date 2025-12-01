import os
from datetime import datetime, timedelta
from src.models import Goal, SubGoal
from src.storage import StorageService

# Ім'я файлу БД
DB_FILE = "test_goals.db"

# 1. Очищення (видаляємо стару базу, якщо є, для чистоти тесту)
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# 2. Ініціалізація сервісу
storage = StorageService(db_path=DB_FILE)
print(f"Базу даних створено: {os.path.exists(DB_FILE)}") # Має бути True

# 3. Створення тестових даних
goal = Goal(
    title="Вивчити SQL",
    description="Розібратися з SELECT та INSERT",
    deadline=datetime.now() + timedelta(days=7)
)
goal.add_subgoal(SubGoal(title="Прочитати статтю"))
goal.add_subgoal(SubGoal(title="Зробити практику"))

# 4. Збереження
print("Зберігаємо ціль...")
storage.save_goal(goal)

# 5. Завантаження (симуляція перезапуску програми)
print("Завантажуємо цілі з БД...")
loaded_goals = storage.load_goals()

if len(loaded_goals) == 1:
    g = loaded_goals[0]
    print(f"✅ Завантажено: {g.title}")
    print(f"   Кількість підцілей: {len(g.subgoals)}") # Має бути 2
    print(f"   ID співпадають: {g.id == goal.id}")
else:
    print("❌ Помилка: Ціль не знайдено!")

# 6. Видалення
print("Видаляємо ціль...")
storage.delete_goal(goal.id)
loaded_goals_after = storage.load_goals()
print(f"✅ Кількість цілей після видалення: {len(loaded_goals_after)}") # Має бути 0