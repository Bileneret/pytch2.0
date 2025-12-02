import google.generativeai as genai
import json
import re
from datetime import datetime
from src.config import Config
from src.models import Difficulty


class AIService:
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("API Key not found in .env file")

        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Використовуємо вашу модель
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_subgoals(self, goal_title: str, goal_desc: str, difficulty: Difficulty) -> list:
        """
        Старий метод для генерації підцілей (одноразовий запит).
        """
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
            return self._parse_json_response(response.text)
        except Exception as e:
            print(f"AI Error: {e}")
            raise e

    # --- НОВІ МЕТОДИ ДЛЯ ЧАТУ ---

    def start_goal_chat(self):
        """
        Розпочинає чат-сесію з AI для створення нової цілі.
        Повертає об'єкт чату.
        """
        # Отримуємо актуальну дату
        current_date = datetime.now().strftime("%Y-%m-%d")

        system_instruction = f"""
        СЬОГОДНІШНЯ ДАТА: {current_date}. Враховуй це при плануванні.

        Ти - професійний RPG-коуч з планування. Твоя мета: допомогти користувачу сформулювати ціль, визначити її складність та дедлайн.

        Твоя поведінка:
        1.  Привітайся (якщо це перший запит) і запитай про ціль.
        2.  Задавай уточнюючі питання, якщо користувач пише надто абстрактно.
        3.  ОБОВ'ЯЗКОВО з'ясуй або запропонуй дедлайн. Якщо користувач не знає, запропонуй реалістичний термін у днях.
        4.  Састійно оціни складність цілі (EASY, MEDIUM, HARD, EPIC) на основі опису.
        5.  Запропонуй розбити ціль на підцілі.

        ФІНАЛІЗАЦІЯ:
        Коли ти зрозумів суть, є дедлайн і ти готовий створити ціль, ти маєш надіслати фінальне повідомлення, яке містить ТІЛЬКИ JSON блок у такому форматі:

        ```json
        {{
            "title": "Чітка назва цілі",
            "description": "Детальний мотиваційний опис",
            "deadline_days": 14, 
            "difficulty": "HARD",
            "subgoals": [
                {{"title": "Крок 1", "description": "Опис"}},
                {{"title": "Крок 2", "description": "Опис"}}
            ]
        }}
        ```

        Важливо:
        - "deadline_days" - це кількість днів від сьогодні (integer).
        - "difficulty" має бути одним з: "EASY", "MEDIUM", "HARD", "EPIC".
        - Мова спілкування: Українська.
        """

        # Ініціалізуємо чат із системним промптом
        chat = self.model.start_chat(history=[
            {"role": "user", "parts": [system_instruction]},
            {"role": "model", "parts": ["Зрозумів. Я готовий допомагати користувачу формулювати цілі. Чекаю на ввід."]}
        ])
        return chat

    def send_to_chat(self, chat, message: str) -> tuple[str, dict]:
        """
        Відправляє повідомлення в чат.
        Повертає кортеж: (текст_відповіді, json_data_якщо_є_або_None).
        """
        try:
            response = chat.send_message(message)
            text = response.text.strip()

            # Перевіряємо, чи є в відповіді JSON (фіналізація)
            json_data = None
            if "```json" in text or text.strip().startswith("{"):
                try:
                    json_str = self._extract_json_string(text)
                    if json_str:
                        json_data = json.loads(json_str)
                except:
                    pass

            return text, json_data

        except Exception as e:
            return f"Помилка з'єднання з AI: {str(e)}", None

    def _extract_json_string(self, text):
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
        if text.strip().startswith("{") and text.strip().endswith("}"):
            return text.strip()
        return None

    def _parse_json_response(self, text_response):
        text_response = text_response.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
        return json.loads(text_response)