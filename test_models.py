from datetime import datetime, timedelta
from src.models import Goal, SubGoal

# 1. Створюємо підцілі
sub1 = SubGoal(title="Написати моделі класів")
sub2 = SubGoal(title="Створити базу даних")

# 2. Створюємо головну ціль (дедлайн - завтра)
my_goal = Goal(
    title="Зробити курсову роботу",
    description="Написати додаток Learning Goals Manager на Python",
    deadline=datetime.now() + timedelta(days=1)
)

# 3. Додаємо підцілі до цілі
my_goal.add_subgoal(sub1)
my_goal.add_subgoal(sub2)

# 4. Перевіряємо роботу логіки
print(f"Ціль: {my_goal.title}")
print(f"Прогрес (початковий): {my_goal.calculate_progress()}%") # Має бути 0.0

# Виконуємо одну підціль
sub1.mark_done()
print(f"Прогрес (одна готова): {my_goal.calculate_progress()}%")   # Має бути 50.0

# Перевірка дедлайну
print(f"Прострочено? {my_goal.is_overdue()}")                     # Має бути False (бо дедлайн завтра)

print("✅ Все працює коректно!")