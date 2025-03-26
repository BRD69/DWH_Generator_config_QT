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

        # Добавляем иконку слева
        self.icon_label = QtWidgets.QLabel()
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "resources", "images", "icon512.png")
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "images", "icon512.png")

        icon = QtGui.QPixmap(icon_path)
        self.icon_label.setPixmap(icon.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.header_layout.addWidget(self.icon_label)

        # Добавляем заголовок в центр
        self.title_label = QtWidgets.QLabel("DWH Generator config")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
            }
        """)
        self.header_layout.addWidget(self.title_label)

        # Добавляем логотип справа
        self.logo_label = QtWidgets.QLabel()
        if getattr(sys, 'frozen', False):
            logo_path = os.path.join(sys._MEIPASS, "resources", "images", "logo_upd.png")
        else:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "images", "logo_upd.png")

        logo = QtGui.QPixmap(logo_path)
        self.logo_label.setPixmap(logo.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.header_layout.addWidget(self.logo_label)

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

        # Создаем контейнер для списка проверок
        self.checks_container = QtWidgets.QWidget()
        self.checks_layout = QtWidgets.QVBoxLayout(self.checks_container)
        self.checks_layout.setSpacing(10)
        self.checks_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем иконки для статусов
        self.check_icon = QtGui.QIcon(":/icon_button/resources/icons/check.png")
        self.cross_icon = QtGui.QIcon(":/icon_button/resources/icons/cross.png")

        # Добавляем проверки
        self.structure_check = self._create_check_item("Структура приложения")
        self.sql_check = self._create_check_item("Подключение к SQL")
        self.config_check = self._create_check_item("Поля для config")

        self.layout.addWidget(self.checks_container)

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

    def _create_check_item(self, text):
        """Создает элемент проверки с иконкой и текстом."""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Создаем иконку статуса
        status_icon = QtWidgets.QLabel()
        status_icon.setFixedSize(20, 20)
        status_icon.setPixmap(self.cross_icon.pixmap(20, 20))
        layout.addWidget(status_icon)

        # Создаем текст
        label = QtWidgets.QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
            }
        """)
        layout.addWidget(label)

        # Добавляем растягивающийся элемент
        layout.addStretch()

        # Добавляем в контейнер проверок
        self.checks_layout.addWidget(container)

        return {
            'container': container,
            'status_icon': status_icon,
            'label': label
        }

    def update_check_status(self, check_name, status):
        """Обновляет статус проверки.

        Args:
            check_name (str): Имя проверки ('structure', 'sql', 'config')
            status (bool): True для успеха, False для ошибки
        """
        check_map = {
            'structure': self.structure_check,
            'sql': self.sql_check,
            'config': self.config_check
        }

        if check_name in check_map:
            check = check_map[check_name]
            icon = self.check_icon if status else self.cross_icon
            check['status_icon'].setPixmap(icon.pixmap(20, 20))
            check['label'].setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    color: {'#4CAF50' if status else '#666666'};
                }}
            """)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    splash = SplashScreen("John Doe")
    splash.show()
    sys.exit(app.exec_())
