import sys
import os

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QFrame,
    QLabel,
    QWidget,
    QLayout,
    QSizePolicy,
    QSpacerItem,
)
from PyQt5.QtCore import Qt


class ContentForm(QDialog):
    def __init__(self, title: str, content, ok_callback=None, custom_buttons=None, parent=None, stretch_content=False, app=None):
        super().__init__(parent)
        self.title = title
        self.content = content
        self.ok_callback = ok_callback
        self.custom_buttons = custom_buttons
        self.stretch_content = stretch_content
        self.app = app
        self.working_dir = app.working_dir

        self._setup_ui()
        self._load_stylesheet()

    def _load_stylesheet(self):
        """Загрузка стилей."""
        style_path = self.app.file_service.get_content_form_stylesheet()
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
        """Настройка интерфейса."""

        # Настройка окна
        self.setWindowTitle(self.title)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        self.setModal(True)
        self.setObjectName("content_form")
        self.setBaseSize(500, 550)

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Контейнер для контента
        content_container = QFrame()
        content_container.setObjectName("content_container")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Обработка контента в зависимости от типа
        if isinstance(self.content, QLayout):
            content_layout.addLayout(self.content)
        elif isinstance(self.content, QWidget):
            content_layout.addWidget(self.content)
        else:
            raise TypeError("Content must be either QLayout or QWidget")

        main_layout.addWidget(content_container)

        if self.stretch_content:
            main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))

        # Контейнер для кнопок
        buttons_container = QFrame()
        buttons_container.setObjectName("buttons_container")
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(5, 5, 5, 5)
        buttons_layout.setSpacing(5)

        # Добавляем кастомные кнопки слева
        if self.custom_buttons:
            for button in self.custom_buttons:
                if isinstance(button, QPushButton):
                    button.setObjectName("action_button")
                    buttons_layout.addWidget(button)
                elif isinstance(button, QWidget):
                    buttons_layout.addWidget(button)

        # Добавляем растяжку между кастомными кнопками и кнопками OK/Закрыть
        buttons_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))

        # Кнопки OK и Закрыть
        if self.ok_callback:
            self.ok_button = QPushButton("OK")
            self.ok_button.setObjectName("action_button")
            self.ok_button.clicked.connect(self.ok_callback)
            buttons_layout.addWidget(self.ok_button)

        self.close_button = QPushButton("Закрыть")
        self.close_button.setObjectName("action_button")
        self.close_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_button)

        main_layout.addWidget(buttons_container)

        if not self.stretch_content:
            main_layout.setStretch(0, 1)
            main_layout.setStretch(1, 0)

        # Устанавливаем основной layout
        self.setLayout(main_layout)
