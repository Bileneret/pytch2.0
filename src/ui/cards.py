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
            bg, border, title_col, icon = "#e0e0e0", "#bdc3c7", "#7f8c8d", "✅"
        else:
            bg, title_col, icon = "white", "#2c3e50", "⚔️"
            colors = {
                Difficulty.EASY: "#2ecc71", Difficulty.MEDIUM: "#3498db",
                Difficulty.HARD: "#e67e22", Difficulty.EPIC: "#9b59b6"
            }
            border = colors.get(self.goal.difficulty, "#bdc3c7")
            if self.goal.penalty_applied:
                border, bg = "#e74c3c", "#fadbd8"

        self.setStyleSheet(f"""
            QFrame {{ background-color: {bg}; border: 1px solid {border}; border-left: 5px solid {border}; border-radius: 6px; }}
            QLabel {{ border: none; background: transparent; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Header
        header = QHBoxLayout()
        lbl_title = QLabel(f"{icon} {self.goal.title}")
        lbl_title.setStyleSheet(f"font-weight: bold; font-size: 15px; color: {title_col};")
        header.addWidget(lbl_title)
        header.addStretch()

        if not self.goal.is_completed:
            btn_ok = QPushButton("Завершити")
            btn_ok.setCursor(Qt.PointingHandCursor)
            btn_ok.setStyleSheet(
                "QPushButton { background-color: #f1c40f; border: none; padding: 5px 10px; border-radius: 4px; font-weight: bold; color: #2c3e50; } QPushButton:hover { background-color: #f39c12; }")
            btn_ok.clicked.connect(lambda: on_complete(self.goal))
            header.addWidget(btn_ok)

        btn_del = QPushButton("✕")
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setFixedSize(30, 30)
        btn_del.setStyleSheet(
            "QPushButton { color: #e74c3c; font-weight: bold; font-size: 14px; } QPushButton:hover { background-color: #fadbd8; border-radius: 15px; }")
        btn_del.clicked.connect(lambda: on_delete(self.goal))
        header.addWidget(btn_del)
        layout.addLayout(header)

        # Info
        info = QHBoxLayout()
        info.addWidget(QLabel(f"Складність: {self.goal.difficulty.name}", styleSheet="font-size: 11px; color: gray;"))
        info.addStretch()

        date_col = "#e74c3c" if self.goal.is_overdue() else "gray"
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
            'pending': "#3498db", 'started': "#f1c40f",
            'finished': "#2ecc71", 'failed': "#e74c3c"
        }
        color = "#95a5a6" if is_future else state_colors.get(self.goal.daily_state, "#bdc3c7")

        self.setStyleSheet(f"""
            QFrame {{ background-color: white; border: 1px solid #bdc3c7; border-left: 5px solid {color}; border-radius: 6px; }}
            QLabel {{ border: none; background: transparent; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Header
        layout.addWidget(
            QLabel(f"📅 {self.goal.title}", styleSheet="font-weight: bold; font-size: 15px; color: #2c3e50;"))
        layout.addWidget(QLabel(f"День: {self.goal.current_day}/{self.goal.total_days} | Час: {self.goal.time_frame}",
                                styleSheet="color: #7f8c8d; font-size: 12px;"))

        # Progress
        pb = QProgressBar()
        pb.setValue(int(self.goal.calculate_progress()))
        pb.setFixedHeight(12)
        pb.setStyleSheet(
            f"QProgressBar {{ border: 1px solid #bdc3c7; border-radius: 5px; background: #ecf0f1; }} QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}")
        layout.addWidget(pb)

        # Buttons
        if not self.goal.is_completed:
            if is_future:
                layout.addWidget(QLabel(f"⏳ Старт: {self.goal.start_date.strftime('%d.%m')}",
                                        styleSheet="color: gray; font-style: italic;", alignment=Qt.AlignCenter))
            else:
                if self.goal.daily_state == 'pending':
                    btn = QPushButton("Розпочати")
                    btn.setCursor(Qt.PointingHandCursor)
                    btn.setStyleSheet(
                        "QPushButton { background-color: #3498db; color: white; font-weight: bold; border-radius: 4px; padding: 8px; }")
                    btn.clicked.connect(lambda: on_start(self.goal))
                    layout.addWidget(btn)
                elif self.goal.daily_state == 'started':
                    btn = QPushButton("Закінчити")
                    btn.setCursor(Qt.PointingHandCursor)
                    btn.setStyleSheet(
                        "QPushButton { background-color: #f1c40f; color: #2c3e50; font-weight: bold; border-radius: 4px; padding: 8px; }")
                    btn.clicked.connect(lambda: on_finish(self.goal))
                    layout.addWidget(btn)
                elif self.goal.daily_state == 'finished':
                    layout.addWidget(QLabel("На сьогодні все ✅", styleSheet="color: #2ecc71; font-weight: bold;",
                                            alignment=Qt.AlignCenter))
                elif self.goal.daily_state == 'failed':
                    layout.addWidget(QLabel("Пропущено ❌", styleSheet="color: #e74c3c; font-weight: bold;",
                                            alignment=Qt.AlignCenter))