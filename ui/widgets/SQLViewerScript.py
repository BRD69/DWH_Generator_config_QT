import os
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QFrame,
                             QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import (QSyntaxHighlighter, QTextCharFormat, QColor, QFont,
                        QPalette, QIcon, QPixmap)
from PyQt5.QtCore import (Qt, QSize)
import re
import sqlparse


class SQLHighlighter(QSyntaxHighlighter):
    """Подсветка синтаксиса SQL"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_formats()

    def _init_formats(self):
        """Инициализация форматов для различных элементов SQL"""
        # Ключевые слова
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#0033CC"))  # Синий
        self.keyword_format.setFontWeight(QFont.Bold)

        # Строки
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#008000"))  # Зеленый

        # Числа
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#FF6600"))  # Оранжевый

        # Комментарии
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#808080"))  # Серый
        self.comment_format.setFontItalic(True)

        # Функции
        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor("#CC00FF"))  # Фиолетовый

        # Определяем правила подсветки
        self.rules = []

        # Ключевые слова SQL
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'ORDER BY', 'GROUP BY',
            'HAVING', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'IN',
            'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'TABLE',
            'INDEX', 'VIEW', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'AS', 'CASE',
            'WHEN', 'THEN', 'ELSE', 'END', 'UNION', 'ALL', 'DISTINCT', 'TOP',
            'LIMIT', 'OFFSET', 'NULL', 'IS', 'NOT NULL', 'LIKE', 'BETWEEN',
            'ASC', 'DESC', 'INTO', 'VALUES', 'SET'
        ]

        for word in keywords:
            pattern = r'\b{}\b'.format(word)
            self.rules.append((re.compile(pattern, re.IGNORECASE), self.keyword_format))

        # Строки в одинарных кавычках
        self.rules.append((re.compile(r"'[^']*'"), self.string_format))

        # Числа
        self.rules.append((re.compile(r'\b\d+\b'), self.number_format))

        # Функции SQL
        functions = [
            'AVG', 'COUNT', 'FIRST', 'LAST', 'MAX', 'MIN', 'SUM', 'UCASE',
            'LCASE', 'MID', 'LEN', 'ROUND', 'NOW', 'FORMAT'
        ]

        for func in functions:
            pattern = r'\b{}\b'.format(func)
            self.rules.append((re.compile(pattern, re.IGNORECASE), self.function_format))

    def highlightBlock(self, text):
        """Подсветка блока текста"""
        # Применяем все правила подсветки
        for pattern, format in self.rules:
            for match in pattern.finditer(text):
                length = match.end() - match.start()
                self.setFormat(match.start(), length, format)

        # Подсветка комментариев
        # Однострочные комментарии
        pos = text.find('--')
        if pos >= 0:
            self.setFormat(pos, len(text) - pos, self.comment_format)

        # Многострочные комментарии
        start = text.find('/*')
        while start >= 0:
            end = text.find('*/', start)
            if end >= 0:
                self.setFormat(start, end - start + 2, self.comment_format)
                start = text.find('/*', end + 2)
            else:
                self.setFormat(start, len(text) - start, self.comment_format)
                break


class SQLViewerScript(QWidget):
    def __init__(self, parent=None, app=None, event_render_sql_script=None, event_run_sql_script=None):
        super().__init__(parent)
        self.app = app
        self.working_dir = app.working_dir
        self.key_render_sql_script = ""
        self.value_render_sql_script = ""
        self.event_render_sql_script = event_render_sql_script
        self.event_run_sql_script = event_run_sql_script
        self.icons = {}

        self._load_icons()
        self._setup_ui()
        self._load_stylesheet()
        self._connect_signals()
        self._load_data()

    def _load_icons(self):
        """Загрузка иконок"""
        self.icons["format"] = QIcon()
        self.icons["format"].addPixmap(QPixmap(":/icon_button/resources/icons/format.png"), QIcon.Normal, QIcon.Off)

        self.icons["clear"] = QIcon()
        self.icons["clear"].addPixmap(QPixmap(":/icon_button/resources/icons/x.png"), QIcon.Normal, QIcon.Off)

        self.icons["execute"] = QIcon()
        self.icons["execute"].addPixmap(QPixmap(":/icon_button/resources/icons/load_item.png"), QIcon.Normal, QIcon.Off)

    def _load_stylesheet(self):
        """Загрузка стилей"""
        style_path = self.app.file_service.get_stylesheet_path("SQLWidget.qss")
        try:
            with open(style_path, "r", encoding='utf-8') as f:
                self.stylesheet = f.read()
            self.setStyleSheet(self.stylesheet)
        except Exception as e:
            self.logger.error(f"Ошибка загрузки стилей: {e}")
            self.logger.error(f"Путь к файлу стилей: {style_path}")
            self.logger.error(f"Текущая директория: {os.getcwd()}")
            self.logger.error(f"MEIPASS: {getattr(sys, '_MEIPASS', 'Не установлен')}")

    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создаем основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Создаем контейнер
        container = QFrame(self)
        container.setObjectName("sql_viewer_container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(5, 5, 5, 5)
        container_layout.setSpacing(5)

        # Создаем панель инструментов
        toolbar = QFrame(self)
        toolbar.setObjectName("sql_toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(5)

        # Кнопка форматирования
        self.format_btn = QPushButton("", self)
        self.format_btn.setObjectName("format_btn")
        self.format_btn.setToolTip("")
        self.format_btn.setFixedSize(QSize(24, 24))
        self.format_btn.setIcon(self.icons["format"])
        self.format_btn.setIconSize(QSize(10, 10))
        self.format_btn.setCursor(Qt.PointingHandCursor)

        toolbar_layout.addWidget(self.format_btn)

        # Кнопка очистки
        self.clear_btn = QPushButton("", self)
        self.clear_btn.setObjectName("clear_btn")
        self.clear_btn.setToolTip("")
        self.clear_btn.setFixedSize(QSize(24, 24))
        self.clear_btn.setIcon(self.icons["clear"])
        self.clear_btn.setIconSize(QSize(16, 16))
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        toolbar_layout.addWidget(self.clear_btn)

        # Кнопка выполнить
        self.execute_btn = QPushButton("Выполнить", self)
        self.execute_btn.setObjectName("execute_btn")
        self.execute_btn.setIcon(self.icons["execute"])
        self.execute_btn.setIconSize(QSize(16, 16))
        self.execute_btn.setCursor(Qt.PointingHandCursor)
        toolbar_layout.addWidget(self.execute_btn)

        # Добавляем растягивающийся спейсер
        toolbar_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Добавляем панель инструментов в контейнер
        container_layout.addWidget(toolbar)

        # Создаем текстовый редактор
        self.editor = QTextEdit(self)
        self.editor.setObjectName("sql_editor")

        # Настраиваем шрифт
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.editor.setFont(font)

        # Устанавливаем ширину табуляции
        metrics = self.editor.fontMetrics()
        self.editor.setTabStopWidth(4 * metrics.width(' '))

        # Включаем нумерацию строк и подсветку текущей строки
        self.editor.setLineWrapMode(QTextEdit.NoWrap)

        # Устанавливаем цветовую схему
        palette = self.editor.palette()
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.Text, QColor("#000000"))
        self.editor.setPalette(palette)

        # Создаем подсветку синтаксиса
        self.highlighter = SQLHighlighter(self.editor.document())

        container_layout.addWidget(self.editor)

        # Добавляем редактор в основной layout
        self.editor_viewer = QTextEdit(self)
        self.editor_viewer.setObjectName("sql_editor_viewer")
        self.editor_viewer.setReadOnly(True)

        # Настраиваем шрифт
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.editor_viewer.setFont(font)

        # Устанавливаем ширину табуляции
        metrics = self.editor_viewer.fontMetrics()
        self.editor_viewer.setTabStopWidth(4 * metrics.width(' '))

        # Устанавливаем цветовую схему
        palette = self.editor.palette()
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.Text, QColor("#000000"))
        self.editor.setPalette(palette)

        # Создаем подсветку синтаксиса
        self.highlighter_viewer = SQLHighlighter(self.editor_viewer.document())

        container_layout.addWidget(self.editor_viewer)

        layout.addWidget(container)


    def _connect_signals(self):
        """Подключение сигналов"""
        self.format_btn.clicked.connect(self._format_sql)
        self.clear_btn.clicked.connect(self.clear)
        self.execute_btn.clicked.connect(lambda: self.event_run_sql_script(sql_script=self.get_text_viewer()))
        self.editor.textChanged.connect(self.set_text_viewer)

    def _load_data(self):
        """Загрузка данных"""
        pass

    def _format_sql(self):
        """Форматирование SQL запроса"""
        try:
            # Получаем текст из редактора
            sql_text = self.editor.toPlainText().strip()
            if not sql_text:
                return

            # Форматируем SQL с помощью sqlparse
            formatted_sql = sqlparse.format(
                sql_text,
                reindent=True,          # Включаем переформатирование отступов
                keyword_case='upper',    # Ключевые слова в верхнем регистре
                indent_width=4,          # Ширина отступа
                indent_tabs=False,       # Используем пробелы вместо табуляции
                wrap_after=80,           # Максимальная длина строки
                comma_first=False,       # Запятые в конце строки
                strip_comments=False,    # Сохраняем комментарии
                use_space_around_operators=True,  # Добавляем пробелы вокруг операторов
                reindent_aligned=True    # Выравниваем отступы
            )

            # Устанавливаем отформатированный текст
            self.editor.setText(formatted_sql)
        except Exception as e:
            print(f"Ошибка форматирования SQL: {str(e)}")

    def set_text(self, text: str, key: str = "", value: str = ""):
        """Установка текста в редактор"""
        self.editor.setText(text)
        self.key_render_sql_script = key
        self.value_render_sql_script = value
        self.set_text_viewer()

    def get_text(self) -> str:
        """Получение текста из редактора"""
        return self.editor.toPlainText()

    def clear(self):
        """Очистка редактора"""
        self.editor.clear()

    def set_text_viewer(self):
        """Установка текста в редактор"""
        if self.key_render_sql_script:
            self.editor_viewer.setText(
                self.event_render_sql_script(
                    key=self.key_render_sql_script,
                    value=self.value_render_sql_script,
                    sql_script=self.get_text()
                )
            )

    def get_text_viewer(self) -> str:
        """Получение текста из редактора"""
        return self.editor_viewer.toPlainText()
