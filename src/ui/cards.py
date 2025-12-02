from datetime import datetime
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QWidget
from PyQt5.QtCore import Qt
from src.models import Difficulty


class QuestCard(QFrame):
    def __init__(self, goal, on_complete, on_delete, on_edit, on_subgoals):
        super().__init__()
        self.goal = goal
        self.on_edit = on_edit
        self.on_subgoals = on_subgoals
        self.setup_ui(on_complete, on_delete)

    def setup_ui(self, on_complete, on_delete):
        # Стилізація рамки
        if self.goal.is_completed:
            border = "#555555"
            title_col = "#7f8c8d"
            icon = "✅"
        else:
            title_col = "white"
            icon = "⚔️"
            colors = {
                Difficulty.EASY: "#2ecc71",  # Green
                Difficulty.MEDIUM: "#3498db",  # Blue
                Difficulty.HARD: "#e67e22",  # Orange
                Difficulty.EPIC: "#9b59b6"  # Purple
            }
            border = colors.get(self.goal.difficulty, "#bdc3c7")

            if self.goal.penalty_applied:
                border = "#e74c3c"

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

        # 1. Header (Назва + Кнопки)
        header = QHBoxLayout()
        lbl_title = QLabel(f"{icon} {self.goal.title}")
        lbl_title.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {title_col};")
        header.addWidget(lbl_title, stretch=1)

        # Спільний стиль для кнопок дій
        base_btn_style = """
            QPushButton { 
                border: none; 
                border-radius: 4px; 
                padding: 5px 10px; 
                font-weight: bold; 
                font-size: 11px;
            }
        """

        # Кнопка "Підцілі" (СИНЯ)
        btn_subs = QPushButton("📝 Підцілі")
        btn_subs.setCursor(Qt.PointingHandCursor)
        btn_subs.setStyleSheet(base_btn_style + """
            QPushButton { background-color: #3498db; color: white; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        btn_subs.clicked.connect(lambda: self.on_subgoals(self.goal))
        header.addWidget(btn_subs)

        # Кнопка "Редагувати" (ЖОВТА) - ТЕКСТОМ
        btn_edit = QPushButton("✏️ Редагувати")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet(base_btn_style + """
            QPushButton { background-color: #f1c40f; color: #2c3e50; }
            QPushButton:hover { background-color: #f39c12; }
        """)
        btn_edit.clicked.connect(lambda: self.on_edit(self.goal))
        header.addWidget(btn_edit)

        # Кнопка "Завершити" (ЗЕЛЕНА)
        if not self.goal.is_completed:
            btn_ok = QPushButton("✅ Завершити")
            btn_ok.setCursor(Qt.PointingHandCursor)
            btn_ok.setStyleSheet(base_btn_style + """
                QPushButton { background-color: #27ae60; color: white; }
                QPushButton:hover { background-color: #2ecc71; }
            """)
            btn_ok.clicked.connect(lambda: on_complete(self.goal))
            header.addWidget(btn_ok)

        # Кнопка "Видалити" (Червона іконка)
        btn_del = QPushButton("✕")
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setFixedSize(24, 24)
        btn_del.setStyleSheet("""
            QPushButton { 
                color: #e74c3c; 
                background-color: transparent;
                font-weight: bold; 
                font-size: 14px; 
                border: none;
            } 
            QPushButton:hover { background-color: #3e3e3e; border-radius: 12px; }
        """)
        btn_del.clicked.connect(lambda: on_delete(self.goal))
        header.addWidget(btn_del)
        layout.addLayout(header)

        # 2. Опис
        if self.goal.description:
            lbl_desc = QLabel(self.goal.description)
            lbl_desc.setWordWrap(True)
            lbl_desc.setStyleSheet("color: #aaa; font-size: 12px; font-style: italic; margin-bottom: 5px;")
            layout.addWidget(lbl_desc)

        # 3. Прогрес підцілей
        if self.goal.subgoals:
            sub_layout = QVBoxLayout()
            sub_layout.setSpacing(2)

            progress = self.goal.calculate_progress()
            pb = QProgressBar()
            pb.setValue(int(progress))
            pb.setFixedHeight(6)
            pb.setTextVisible(False)
            pb.setStyleSheet(f"""
                QProgressBar {{ border: none; background: #333; border-radius: 3px; }}
                QProgressBar::chunk {{ background-color: {border}; border-radius: 3px; }}
            """)
            sub_layout.addWidget(pb)

            done_count = sum(1 for s in self.goal.subgoals if s.is_completed)
            lbl_subs_count = QLabel(f"Підцілі: {done_count}/{len(self.goal.subgoals)}")
            lbl_subs_count.setStyleSheet("color: #777; font-size: 10px;")
            sub_layout.addWidget(lbl_subs_count)

            layout.addLayout(sub_layout)

        # 4. Info
        info = QHBoxLayout()
        info.addWidget(
            QLabel(f"{self.goal.difficulty.name}",
                   styleSheet="font-size: 11px; color: #bdc3c7; border: 1px solid #444; padding: 2px 4px; border-radius: 3px;"))

        created_str = self.goal.created_at.strftime('%d.%m.%Y')
        info.addWidget(QLabel(f"Створено: {created_str}", styleSheet="font-size: 11px; color: #666; margin-left: 5px;"))

        info.addStretch()

        date_col = "#e74c3c" if self.goal.is_overdue() else "#bdc3c7"
        info.addWidget(QLabel(f"⏳ {self.goal.deadline.strftime('%Y-%m-%d %H:%M')}",
                              styleSheet=f"font-size: 12px; color: {date_col}; font-weight: bold;"))
        layout.addLayout(info)


class HabitCard(QFrame):
    def __init__(self, goal, simulated_now, on_start, on_finish, on_edit):
        super().__init__()
        self.goal = goal
        self.simulated_now = simulated_now
        self.on_edit = on_edit
        self.setup_ui(on_start, on_finish)

    def setup_ui(self, on_start, on_finish):
        is_future = self.simulated_now.date() < self.goal.start_date.date()

        state_colors = {
            'pending': "#3498db",
            'started': "#f1c40f",
            'finished': "#2ecc71",
            'failed': "#e74c3c"
        }
        color = "#95a5a6" if is_future else state_colors.get(self.goal.daily_state, "#bdc3c7")

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
        header = QHBoxLayout()
        lbl_title = QLabel(f"📅 {self.goal.title}")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        header.addWidget(lbl_title)
        header.addStretch()

        # Кнопка редагування (Жовта, текстом)
        btn_edit = QPushButton("✏️ Редагувати")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet("""
            QPushButton { 
                background-color: #f1c40f; 
                color: #2c3e50; 
                border: none; 
                border-radius: 4px; 
                padding: 4px 8px; 
                font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #f39c12; }
        """)
        btn_edit.clicked.connect(lambda: self.on_edit(self.goal))
        header.addWidget(btn_edit)

        layout.addLayout(header)

        # Info
        layout.addWidget(QLabel(f"День: {self.goal.current_day}/{self.goal.total_days} | Час: {self.goal.time_frame}",
                                styleSheet="color: #bdc3c7; font-size: 12px;"))

        if self.goal.description:
            layout.addWidget(
                QLabel(self.goal.description, styleSheet="color: #666; font-size: 11px; font-style: italic;"))

        # Progress
        pb = QProgressBar()
        pb.setValue(int(self.goal.calculate_progress()))
        pb.setFixedHeight(12)
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