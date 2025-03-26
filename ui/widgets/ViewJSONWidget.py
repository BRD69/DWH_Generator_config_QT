import os
import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class JSONHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Формат для ключей
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#0550AE"))
        self.key_format.setFontWeight(QFont.Bold)

        # Формат для строковых значений
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#22863A"))

        # Формат для чисел
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#0550AE"))

        # Формат для булевых значений и null
        self.boolean_format = QTextCharFormat()
        self.boolean_format.setForeground(QColor("#0550AE"))

        # Формат для скобок и запятых
        self.punctuation_format = QTextCharFormat()
        self.punctuation_format.setForeground(QColor("#24292E"))

    def highlightBlock(self, text):
        """Подсветка синтаксиса JSON."""
        import re

        # Подсветка ключей
        key_pattern = r'"([^"]+)"\s*:'
        for match in re.finditer(key_pattern, text):
            start, end = match.span()
            self.setFormat(start, end - start, self.key_format)

        # Подсветка строковых значений
        string_pattern = r':\s*"([^"]*)"'
        for match in re.finditer(string_pattern, text):
            start, end = match.span()
            self.setFormat(start, end - start, self.string_format)

        # Подсветка чисел
        number_pattern = r':\s*(-?\d+\.?\d*)'
        for match in re.finditer(number_pattern, text):
            start, end = match.span()
            self.setFormat(start, end - start, self.number_format)

        # Подсветка булевых значений и null
        boolean_pattern = r':\s*(true|false|null)'
        for match in re.finditer(boolean_pattern, text, re.IGNORECASE):
            start, end = match.span()
            self.setFormat(start, end - start, self.boolean_format)

        # Подсветка скобок и запятых
        punctuation_pattern = r'[{}\[\],]'
        for match in re.finditer(punctuation_pattern, text):
            start, end = match.span()
            self.setFormat(start, end - start, self.punctuation_format)


class ViewJSONWidget(QWidget):
    def __init__(self, text: str = "", working_dir: Path = None, parent=None):
        super().__init__(parent)
        self.text = text
        self.working_dir = working_dir
        self.setup_ui()
        self.setObjectName("view_text_widget")

        # Устанавливаем политику размера для растягивания
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._load_stylesheet()

    def _load_stylesheet(self):
        """Загружает стили для виджета."""
        style_path = self.app.file_service.get_stylesheet_path("ViewTextWidget.qss")
        try:
            with open(style_path, "r", encoding='utf-8') as f:
                self.stylesheet = f.read()
            self.setStyleSheet(self.stylesheet)
        except Exception as e:
            print(f"Ошибка загрузки стилей: {e}")
            print(f"Путь к файлу стилей: {style_path}")
            print(f"Текущая директория: {os.getcwd()}")
            print(f"MEIPASS: {getattr(sys, '_MEIPASS', 'Не установлен')}")

    def setup_ui(self):
        """Настройка интерфейса виджета."""
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Контейнер для текста
        text_container = QFrame()
        text_container.setObjectName("text_container")
        text_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)

        # Поле для текста
        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("view_text")
        self.text_edit.setReadOnly(True)  # Текст нельзя редактировать
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)  # Отключаем перенос строк для JSON
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Вертикальная прокрутка
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Горизонтальная прокрутка
        self.text_edit.setPlainText(self.text)  # Устанавливаем текст
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Устанавливаем моноширинный шрифт
        font = QFont("Consolas", 10)  # или другой моноширинный шрифт
        self.text_edit.setFont(font)

        # Добавляем подсветку синтаксиса
        self.highlighter = JSONHighlighter(self.text_edit.document())

        text_layout.addWidget(self.text_edit)
        layout.addWidget(text_container)

        # Устанавливаем основной layout
        self.setLayout(layout)

    def set_text(self, text: str):
        """Установка текста в виджет."""
        self.text = text
        self.text_edit.setPlainText(text)
        # Перезапускаем подсветку
        self.highlighter.rehighlight()

    def get_text(self) -> str:
        """Получение текста из виджета."""
        return self.text_edit.toPlainText()
