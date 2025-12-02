import os
from dotenv import load_dotenv

# Завантажуємо змінні з .env файлу
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")