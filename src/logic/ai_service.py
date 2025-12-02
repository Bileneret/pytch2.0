import google.generativeai as genai
import json
from src.config import Config
from src.models import Difficulty


class AIService:
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("API Key not found in .env file")

        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Використовуємо вашу модель, як ви просили
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_subgoals(self, goal_title: str, goal_desc: str, difficulty: Difficulty) -> list:
        """
        Генерує список підцілей на основі назви, опису та складності.
        Повертає список словників: [{'title': '...', 'description': '...'}, ...]
        """

        # Визначаємо кількість підцілей залежно від складності
        if difficulty == Difficulty.EASY:
            count_range = "2-3"
        elif difficulty == Difficulty.MEDIUM:
            count_range = "3-4"
        elif difficulty == Difficulty.HARD:
            count_range = "5-6"
        elif difficulty == Difficulty.EPIC:
            count_range = "8-10"
        else:
            count_range = "3-5"

        prompt = f"""
        Ти - коуч-помічник для розбиття цілей на конкретні описані підцілі.
        Користувач має ціль: "{goal_title}".
        Опис цілі: "{goal_desc}".
        Рівень складності: {difficulty.name} (Це важливо!).

        Твоє завдання: Розбий цю ціль на {count_range} конкретних, досяжних підцілей (кроків).
        Для кожної підцілі дай коротку назву.
        Для кожної підцілі дай опис-пояснення як виконати підціль та що необхідно виконати. 

        Відповідь СУВОРО у форматі JSON (список об'єктів), без зайвого тексту чи markdown форматування (без ```json).
        Приклад формату:
        [
            {{"title": "Назва кроку 1", "description": "Опис кроку 1"}},
            {{"title": "Назва кроку 2", "description": "Опис кроку 2"}}
        ]
        Мова: Українська.

        Перевір свою відповідь на галюцинації та актуальність інформації.
        Для створення максимально якісних та актуальних кроків використовуй наступні авторитетні джерела залежно від тематики цілі:
        - IT та програмування: [https://roadmap.sh](https://roadmap.sh)
        - Дизайн (UI/UX, Графічний): [https://roadmap.sh/ux-design](https://roadmap.sh/ux-design) та [https://www.canva.com/design-school/](https://www.canva.com/design-school/)
        - Маркетинг та реклама: [https://academy.hubspot.com/](https://academy.hubspot.com/) та [https://learning.google/](https://learning.google/)
        - Вивчення іноземних мов: [https://refold.la/roadmap/](https://refold.la/roadmap/)
        - Бізнес та стартапи: [https://www.ycombinator.com/library](https://www.ycombinator.com/library)
        - Фундаментальні науки (Математика, Біологія, тощо): [https://www.khanacademy.org/](https://www.khanacademy.org/)
        """

        try:
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()

            # Очистка від можливих markdown тегів, якщо AI їх все ж додав
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]

            subgoals_data = json.loads(text_response)
            return subgoals_data

        except Exception as e:
            print(f"AI Error: {e}")
            raise e