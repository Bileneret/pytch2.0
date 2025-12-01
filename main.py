import sys
import os
from PyQt5.QtWidgets import QApplication

from src.storage import StorageService
from src.logic import GoalService, AuthService
from src.ui.main_window import MainWindow
from src.ui.auth import LoginWindow


# Налаштування шляхів до бази даних
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)


class AppController:
    """
    Головний контролер програми.
    Відповідає за перемикання між вікном входу та головним вікном.
    """

    def __init__(self):
        self.app = QApplication(sys.argv)

        # Налаштування шрифту для всієї програми (опціонально)
        font = self.app.font()
        font.setFamily("Segoe UI")  # Або Arial
        font.setPointSize(9)
        self.app.setFont(font)

        # Ініціалізація сервісів
        self.storage = StorageService(DB_PATH)
        self.auth_service = AuthService(self.storage)

        self.check_auth_and_run()

    def check_auth_and_run(self):
        """Перевіряє сесію при запуску."""
        # 1. Перевіряємо, чи є збережена сесія (хто останній грав)
        user_id = self.auth_service.get_current_user_id()

        if user_id:
            # Якщо є - запускаємо Головне вікно
            self.show_main_window(user_id)
        else:
            # Якщо немає - запускаємо Логін
            self.show_login_window()

    def show_login_window(self):
        self.login_window = LoginWindow(self.auth_service)
        # Коли вхід успішний -> запускаємо main
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()

    def on_login_success(self):
        """Викликається, коли користувач успішно увійшов/зареєструвався."""
        self.login_window.close()
        user_id = self.auth_service.get_current_user_id()
        self.show_main_window(user_id)

    def show_main_window(self, user_id):
        """Створює та показує головне вікно гри."""
        # Створюємо сервіс цілей конкретно для цього користувача
        goal_service = GoalService(self.storage, user_id)

        self.main_window = MainWindow(goal_service)
        # Підключаємо сигнал виходу
        self.main_window.logout_signal.connect(self.on_logout)
        self.main_window.show()

    def on_logout(self):
        """Обробка виходу з акаунту."""
        # Очищаємо сесію
        self.auth_service.logout()
        # Закриваємо головне вікно
        self.main_window.close()
        # Показуємо вікно входу
        self.show_login_window()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    controller = AppController()
    controller.run()