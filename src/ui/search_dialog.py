import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QLabel, QAbstractItemView, QWidget, QHBoxLayout
)
from PyQt5.QtCore import Qt
from src.models import Goal


class SearchDialog(QDialog):
    def __init__(self, parent, goals: list[Goal]):
        super().__init__(parent)
        self.setWindowTitle("Пошук цілей 🔍")
        self.resize(500, 600)
        self.goals = sorted(goals, key=lambda g: g.title.lower())  # Сортировка по алфавиту
        self.selected_goal = None

        self.setup_ui()
        # Инициализируем список всеми целями
        self.update_list("")

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 1. Список результатов (Сверху)
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        # Подключаем двойной клик
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Стилизация списка
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #444;
                border: 1px solid #9b59b6;
            }
        """)
        layout.addWidget(self.list_widget)

        # 2. Поле ввода (Снизу)
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Введіть текст для пошуку...")
        self.input_search.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #9b59b6;
                border-radius: 5px;
                background-color: #333;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #8e44ad;
            }
        """)
        # Живой поиск
        self.input_search.textChanged.connect(self.update_list)
        layout.addWidget(self.input_search)

        # Фокус сразу на поле ввода
        self.input_search.setFocus()

    def update_list(self, text):
        """Фильтрует цели и подсвечивает совпадения."""
        self.list_widget.clear()
        query = text.strip()

        for goal in self.goals:
            # Проверяем совпадения
            match_found = False

            # Подготовка текста для отображения (HTML)
            title_html = goal.title
            desc_html = goal.description
            subs_html = []

            # Если запрос пустой, просто показываем все
            if not query:
                match_found = True
            else:
                # Поиск в заголовке
                if self._highlight_text(query, goal.title):
                    title_html = self._highlight_text(query, goal.title)
                    match_found = True

                # Поиск в описании
                if self._highlight_text(query, goal.description):
                    desc_html = self._highlight_text(query, goal.description)
                    match_found = True

                # Поиск в подцелях
                for sub in goal.subgoals:
                    if self._highlight_text(query, sub.title) or self._highlight_text(query, sub.description):
                        h_title = self._highlight_text(query, sub.title) or sub.title
                        # h_desc = self._highlight_text(query, sub.description) or sub.description
                        subs_html.append(f"• {h_title}")
                        match_found = True

            if match_found:
                item = QListWidgetItem()
                item.setData(Qt.UserRole, goal)  # Храним объект цели в элементе

                # Формируем HTML для отображения в списке
                display_html = f"<div style='font-weight: bold; font-size: 15px;'>{title_html}</div>"
                if desc_html:
                    display_html += f"<div style='color: #aaa; font-size: 12px; margin-top: 4px;'>{desc_html}</div>"

                if subs_html:
                    subs_str = "<br>".join(subs_html)
                    display_html += f"<div style='color: #888; font-size: 11px; margin-top: 4px; font-style: italic;'>Знайдено у підцілях:<br>{subs_str}</div>"

                # Создаем виджет для отображения HTML внутри Item
                lbl = QLabel(display_html)
                lbl.setWordWrap(True)
                lbl.setTextFormat(Qt.RichText)
                lbl.setStyleSheet("background: transparent;")

                # Расчет высоты
                # (Упрощенно, можно точнее через sizeHint)
                height = 50
                if len(desc_html) > 50: height += 20
                if subs_html: height += len(subs_html) * 15

                item.setSizeHint(lbl.sizeHint() + models_size_fix(50, 20))  # Небольшой фикс, лучше динамически

                # Добавляем в список
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, lbl)

    def _highlight_text(self, query, text):
        """Возвращает текст с HTML подсветкой или None, если совпадений нет."""
        if not text: return None
        if not query: return text

        # Экранируем спецсимволы и ищем без учета регистра
        pattern = re.compile(f"({re.escape(query)})", re.IGNORECASE)

        if pattern.search(text):
            # Заменяем на версию с желтым фоном
            # background-color: #f1c40f (желтый), color: #000 (черный)
            return pattern.sub(r'<span style="background-color: #f1c40f; color: #000; font-weight: bold;">\1</span>',
                               text)
        return None

    def on_item_double_clicked(self, item):
        self.selected_goal = item.data(Qt.UserRole)
        self.accept()


def models_size_fix(w, h):
    from PyQt5.QtCore import QSize
    return QSize(w, h)  # Заглушка для QSize, если импорт сверху не сработал корректно в контексте eval