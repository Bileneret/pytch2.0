from datetime import datetime
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt5.QtCore import Qt
from src.models import Difficulty


class QuestCard(QFrame):
    def __init__(self, goal, on_complete, on_delete):
        super().__init__()
        self.goal = goal
        self.setup_ui(on_complete, on_delete)

    def setup_ui(self, on_complete, on_delete):
        # Стилізація
        if self.goal.is_completed:
            # Завершено: сіра рамка, сірий текст, без спеціального фону (темний з теми)
            border = "#555555"
            title_col = "#7f8c8d"
            icon = "✅"
        else:
            # Активно: кольорова рамка, білий текст
            title_col = "white"
            icon = "⚔️"
            colors = {
                Difficulty.EASY: "#2ecc71",  # Green
                Difficulty.MEDIUM: "#3498db",  # Blue
                Difficulty.HARD: "#e67e22",  # Orange
                Difficulty.EPIC: "#9b59b6"  # Purple
            }
            border = colors.get(self.goal.difficulty, "#bdc3c7")

            # Якщо прострочено і застосовано штраф - червона рамка
            if self.goal.penalty_applied:
                border = "#e74c3c"

        # Встановлюємо тільки рамку. Фон підтягнеться з QSS (темний).
        self.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {border};
                border-left: 5px solid {border};
                border-radius: 6px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Header
        header = QHBoxLayout()
        lbl_title = QLabel(f"{icon} {self.goal.title}")
        # title_col тепер білий або сірий
        lbl_title.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {title_col};")
        header.addWidget(lbl_title)
        header.addStretch()

        if not self.goal.is_completed:
            btn_ok = QPushButton("Завершити")
            btn_ok.setCursor(Qt.PointingHandCursor)
            # Жовта кнопка - залишаємо темний текст для контрасту
            btn_ok.setStyleSheet("""
                QPushButton { 
                    background-color: #f1c40f; 
                    border: none; 
                    padding: 5px 10px; 
                    border-radius: 4px; 
                    font-weight: bold; 
                    color: #2c3e50; 
                } 
                QPushButton:hover { background-color: #f39c12; }
            """)
            btn_ok.clicked.connect(lambda: on_complete(self.goal))
            header.addWidget(btn_ok)

        btn_del = QPushButton("✕")
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setFixedSize(30, 30)
        btn_del.setStyleSheet("""
            QPushButton { 
                color: #e74c3c; 
                background-color: transparent;
                font-weight: bold; 
                font-size: 14px; 
                border: none;
            } 
            QPushButton:hover { background-color: #3e3e3e; border-radius: 15px; }
        """)
        btn_del.clicked.connect(lambda: on_delete(self.goal))
        header.addWidget(btn_del)
        layout.addLayout(header)

        # Info
        info = QHBoxLayout()
        info.addWidget(
            QLabel(f"Складність: {self.goal.difficulty.name}", styleSheet="font-size: 11px; color: #bdc3c7;"))
        info.addStretch()

        date_col = "#e74c3c" if self.goal.is_overdue() else "#bdc3c7"
        info.addWidget(QLabel(f"⏳ {self.goal.deadline.strftime('%Y-%m-%d %H:%M')}",
                              styleSheet=f"font-size: 12px; color: {date_col};"))
        layout.addLayout(info)


class HabitCard(QFrame):
    def __init__(self, goal, simulated_now, on_start, on_finish):
        super().__init__()
        self.goal = goal
        self.simulated_now = simulated_now
        self.setup_ui(on_start, on_finish)

    def setup_ui(self, on_start, on_finish):
        is_future = self.simulated_now.date() < self.goal.start_date.date()

        state_colors = {
            'pending': "#3498db",  # Blue
            'started': "#f1c40f",  # Yellow
            'finished': "#2ecc71",  # Green
            'failed': "#e74c3c"  # Red
        }
        # Сірий колір для майбутнього, інакше колір стану
        color = "#95a5a6" if is_future else state_colors.get(self.goal.daily_state, "#bdc3c7")

        # Тільки рамка, фон прозорий/темний з теми
        self.setStyleSheet(f"""
            QFrame {{
                border: 1px solid #555;
                border-left: 5px solid {color};
                border-radius: 6px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Header
        # Змінив колір на білий
        layout.addWidget(
            QLabel(f"📅 {self.goal.title}", styleSheet="font-weight: bold; font-size: 14px; color: white;"))

        # Info text світло-сірий
        layout.addWidget(QLabel(f"День: {self.goal.current_day}/{self.goal.total_days} | Час: {self.goal.time_frame}",
                                styleSheet="color: #bdc3c7; font-size: 12px;"))

        # Progress
        pb = QProgressBar()
        pb.setValue(int(self.goal.calculate_progress()))
        pb.setFixedHeight(12)
        # Фон бара темніший, чанк бере колір від статусу
        pb.setStyleSheet(f"""
            QProgressBar {{ 
                border: 1px solid #555; 
                border-radius: 5px; 
                background: #2d2d2d; 
                text-align: center;
            }} 
            QProgressBar::chunk {{ 
                background-color: {color}; 
                border-radius: 4px; 
            }}
        """)
        layout.addWidget(pb)

        # Buttons
        if not self.goal.is_completed:
            if is_future:
                layout.addWidget(QLabel(f"⏳ Старт: {self.goal.start_date.strftime('%d.%m')}",
                                        styleSheet="color: #7f8c8d; font-style: italic;", alignment=Qt.AlignCenter))
            else:
                if self.goal.daily_state == 'pending':
                    btn = QPushButton("Розпочати")
                    btn.setCursor(Qt.PointingHandCursor)
                    btn.setStyleSheet("""
                        QPushButton { 
                            background-color: #3498db; 
                            color: white; 
                            font-weight: bold; 
                            border-radius: 4px; 
                            padding: 8px; 
                        }
                        QPushButton:hover { background-color: #2980b9; }
                    """)
                    btn.clicked.connect(lambda: on_start(self.goal))
                    layout.addWidget(btn)

                elif self.goal.daily_state == 'started':
                    btn = QPushButton("Закінчити")
                    btn.setCursor(Qt.PointingHandCursor)
                    # Жовта кнопка - темний текст
                    btn.setStyleSheet("""
                        QPushButton { 
                            background-color: #f1c40f; 
                            color: #2c3e50; 
                            font-weight: bold; 
                            border-radius: 4px; 
                            padding: 8px; 
                        }
                        QPushButton:hover { background-color: #f39c12; }
                    """)
                    btn.clicked.connect(lambda: on_finish(self.goal))
                    layout.addWidget(btn)

                elif self.goal.daily_state == 'finished':
                    layout.addWidget(QLabel("На сьогодні все ✅", styleSheet="color: #2ecc71; font-weight: bold;",
                                            alignment=Qt.AlignCenter))
                elif self.goal.daily_state == 'failed':
                    layout.addWidget(QLabel("Пропущено ❌", styleSheet="color: #e74c3c; font-weight: bold;",
                                            alignment=Qt.AlignCenter))