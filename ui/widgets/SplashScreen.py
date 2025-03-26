from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import os
import sys

class SplashScreen(QtWidgets.QWidget):
    """Виджет загрузки приложения."""

    def __init__(self, user_name):
        """Инициализирует виджет загрузки.

        Args:
            user_name (str): Имя пользователя
        """
        super().__init__()
        self.user_name = user_name
        self._setup_ui()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        # Устанавливаем размер и позицию
        self.setFixedSize(600, 400)
        self.setWindowFlags(Qt.FramelessWindowHint)  # Убираем рамку окна
        self.setAttribute(Qt.WA_TranslucentBackground)  # Делаем фон прозрачным

        # Создаем основной контейнер
        self.container = QtWidgets.QWidget(self)
        self.container.setObjectName("container")
        self.container.setGeometry(0, 0, 600, 400)

        # Создаем layout
        self.layout = QtWidgets.QVBoxLayout(self.container)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Создаем верхнюю часть с заголовком
        self.header_layout = QtWidgets.QHBoxLayout()

        # Добавляем иконку
        self.icon_label = QtWidgets.QLabel()
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "resources", "images", "icon512.png")
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "images", "icon512.png")

        icon = QtGui.QPixmap(icon_path)
        self.icon_label.setPixmap(icon.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.header_layout.addWidget(self.icon_label)

        # Добавляем заголовок
        self.title_label = QtWidgets.QLabel("DWH Generator config")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
            }
        """)
        self.header_layout.addWidget(self.title_label)

        self.layout.addLayout(self.header_layout)

        # Добавляем имя пользователя
        self.user_label = QtWidgets.QLabel(self.user_name)
        self.user_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #666666;
            }
        """)
        self.user_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.user_label)

        # Добавляем сообщение о загрузке
        self.loading_label = QtWidgets.QLabel("Загрузка...")
        self.loading_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666666;
            }
        """)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.loading_label)

        # Добавляем растягивающийся элемент
        self.layout.addStretch()

        # Добавляем нижнюю часть с информацией о разработчике
        self.footer_label = QtWidgets.QLabel("Разработка BRD Pro")
        self.footer_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
            }
        """)
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.footer_label)

        # Устанавливаем стили
        self.setStyleSheet("""
            QWidget#container {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 10px;
            }
        """)