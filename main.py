import sys
import os
# Додаємо QtGui для роботи з палітрою, якщо знадобиться, але тут головне QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, QTextStream

from src.storage import StorageService
from src.logic import GoalService, AuthService
from src.ui.main_window import MainWindow
from src.ui.auth import LoginWindow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # 1. Завантаження шрифту
        font = self.app.font()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.app.setFont(font)

        # 2. ЗАВАНТАЖЕННЯ QSS СТИЛЮ
        self.load_stylesheet()

        self.storage = StorageService(DB_PATH)
        self.auth_service = AuthService(self.storage)
        self.check_auth_and_run()

    def load_stylesheet(self):
        """Завантажує глобальний файл стилів."""
        style_path = os.path.join(BASE_DIR, "assets", "style.qss")
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    self.app.setStyleSheet(f.read())
                print("Global style loaded successfully.")
            except Exception as e:
                print(f"Error loading style: {e}")
        else:
            print("style.qss not found!")

    def check_auth_and_run(self):
        user_id = self.auth_service.get_current_user_id()
        if user_id:
            self.show_main_window(user_id)
        else:
            self.show_login_window()

    def show_login_window(self):
        self.login_window = LoginWindow(self.auth_service)
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()

    def on_login_success(self):
        self.login_window.close()
        user_id = self.auth_service.get_current_user_id()
        self.show_main_window(user_id)

    def show_main_window(self, user_id):
        goal_service = GoalService(self.storage, user_id)
        self.main_window = MainWindow(goal_service)
        self.main_window.logout_signal.connect(self.on_logout)
        self.main_window.show()

    def on_logout(self):
        self.auth_service.logout()
        self.main_window.close()
        self.show_login_window()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    controller = AppController()
    controller.run()