import os
from datetime import datetime, timedelta
from src.storage import StorageService
from src.logic import GoalService, ValidationUtils

# Налаштування
DB_FILE = "test_logic.db"
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

storage = StorageService(DB_FILE)
service = GoalService(storage)

# 1. Тест Валідації (R38)
try:
    service.create_goal("", "Опис", datetime.now())
    print("❌ Помилка: Валідація пропустила порожню назву!")
except ValueError:
    print("✅ Валідація працює: порожню назву відхилено.")

# 2. Створення даних для сортування
now = datetime.now()

# Ціль 1: Дедлайн завтра, прогрес 0%
g1 = service.create_goal("А. Термінова", "Опис", now + timedelta(days=1))

# Ціль 2: Дедлайн через місяць, але виконана (100%)
g2 = service.create_goal("Б. Виконана", "Опис", now + timedelta(days=30))
g2.is_completed = True
service.edit_goal(g2) # Зберігаємо зміни

# Ціль 3: Дедлайн через тиждень
g3 = service.create_goal("В. Середня", "Опис", now + timedelta(days=7))

print(f"Створено цілей: {len(service.get_all_goals())}")

# 3. Тест Пошуку (R14)
results = service.search_goals("термін")
if len(results) == 1 and results[0].title == "А. Термінова":
    print("✅ Пошук працює.")
else:
    print("❌ Помилка пошуку.")

# 4. Тест Сортування за Дедлайном (R15)
sorted_deadline = service.sort_goals('deadline')
# Очікуємо: g1 (завтра), g3 (тиждень), g2 (місяць)
if sorted_deadline[0].title == "А. Термінова" and sorted_deadline[-1].title == "Б. Виконана":
    print("✅ Сортування за дедлайном працює.")
else:
    print("❌ Помилка сортування за дедлайном.")

# 5. Тест Сортування за Прогресом
sorted_progress = service.sort_goals('progress')
# Очікуємо: g2 (100%) перша
if sorted_progress[0].title == "Б. Виконана":
    print("✅ Сортування за прогресом працює.")
else:
    print("❌ Помилка сортування за прогресом.")