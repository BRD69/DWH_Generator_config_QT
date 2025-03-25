from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtCore import Qt


class ViewTextWidget(QWidget):
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
        with open(self.working_dir / "resources" / "styles" / "ViewTextWidget.qss", "r") as f_view_text_widget:
            self.stylesheet = f_view_text_widget.read()

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
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)  # Перенос по ширине виджета
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Вертикальная прокрутка
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Горизонтальная прокрутка
        self.text_edit.setPlainText(self.text)  # Устанавливаем текст
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        text_layout.addWidget(self.text_edit)
        layout.addWidget(text_container)

        # Устанавливаем основной layout
        self.setLayout(layout)

    def set_text(self, text: str):
        """Установка текста в виджет."""
        self.text = text
        self.text_edit.setPlainText(text)

    def get_text(self) -> str:
        """Получение текста из виджета."""
        return self.text_edit.toPlainText()
