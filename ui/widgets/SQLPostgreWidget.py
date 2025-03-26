import os
import sys
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QFrame,
    QTextEdit,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from ui.widgets.ActionsConnectWidget import LabelConnectWidget
from ui.widgets.SQLViewerScript import SQLViewerScript

class PostgreWidget(QWidget):
    def __init__(self, parent=None, working_dir=None, data_connect=None, app=None):
        super().__init__(parent)
        self.stylesheet = ""
        self.working_dir = working_dir
        self.data_connect = data_connect
        self.app = app
        self.status, self.message = self.app.postgres_service.status
        self.setObjectName("pg_widget")

        self._setup_ui()
        self._load_stylesheet()

        self.set_data()

    def _load_stylesheet(self):
        """Загружает стили для виджета."""
        style_path = self.app.file_service.get_stylesheet_path("SQLWidget.qss")

        try:
            with open(style_path, "r", encoding='utf-8') as f:
                self.stylesheet = f.read()

            self.setStyleSheet(self.stylesheet)
        except Exception as e:
            print(f"Ошибка загрузки стилей: {e}")
            print(f"Путь к файлу стилей: {style_path}")
            print(f"Текущая директория: {os.getcwd()}")
            print(f"MEIPASS: {getattr(sys, '_MEIPASS', 'Не установлен')}")


    def _setup_ui(self):
        """Настройка интерфейса."""

        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Создаем контейнер для полей
        fields_container = QFrame()
        fields_container.setObjectName("fields_container")
        fields_layout = QVBoxLayout(fields_container)
        fields_layout.setContentsMargins(10, 10, 10, 10)
        fields_layout.setSpacing(10)

         # Создаем горизонтальный layout для статуса
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(5)

        # Добавляем label "Статус соединения"
        status_label = QLabel("Статус соединения:")
        status_layout.addWidget(status_label)

        # Добавляем label для иконки
        self.status_icon = LabelConnectWidget()
        status_layout.addWidget(self.status_icon)

        # Добавляем кнопку для отображения ошибки
        self.error_btn = QPushButton("Ошибка")
        self.error_btn.setObjectName("error_btn")
        self.error_btn.setCursor(Qt.PointingHandCursor)
        self.error_btn.clicked.connect(self._show_error)
        self.error_btn.hide()  # По умолчанию скрыта
        status_layout.addWidget(self.error_btn)

        # Добавляем растягивающийся спейсер
        status_layout.addStretch()

        # Добавляем layout статуса в основной layout
        fields_layout.addLayout(status_layout)

        # Добавляем линию
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("line")
        fields_layout.addWidget(line)

        # Поля для ввода данных
        self.host_input = QLineEdit(self)
        self.host_input.setObjectName("input_field")
        self.host_input.setPlaceholderText("Хост (например, localhost)")
        fields_layout.addWidget(QLabel("Хост:"))
        fields_layout.addWidget(self.host_input)

        self.port_input = QLineEdit(self)
        self.port_input.setObjectName("input_field")
        self.port_input.setPlaceholderText("Порт (например, 5432)")
        fields_layout.addWidget(QLabel("Порт:"))
        fields_layout.addWidget(self.port_input)

        self.dbname_input = QLineEdit(self)
        self.dbname_input.setObjectName("input_field")
        self.dbname_input.setPlaceholderText("Имя базы данных")
        fields_layout.addWidget(QLabel("Имя базы данных:"))
        fields_layout.addWidget(self.dbname_input)

        self.user_input = QLineEdit(self)
        self.user_input.setObjectName("input_field")
        self.user_input.setPlaceholderText("Пользователь")
        fields_layout.addWidget(QLabel("Пользователь:"))
        fields_layout.addWidget(self.user_input)

        self.password_input = QLineEdit(self)
        self.password_input.setObjectName("input_field")
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        fields_layout.addWidget(QLabel("Пароль:"))
        fields_layout.addWidget(self.password_input)

        main_layout.addWidget(fields_container)

    def set_status(self):
        """Устанавливает статус соединения."""

        if self.status:
            self.status_icon.set_status_connect_on()
            self.error_btn.hide()
        else:
            self.status_icon.set_status_connect_off()
            self.error_btn.show()

    def _show_error(self):
        """Показывает окно с текстом ошибки."""
        QMessageBox.critical(self, "Ошибка подключения", self.message)

    def get_settings(self):
        settings = {
            "host": self.host_input.text(),
            "port": self.port_input.text(),
            "dbname": self.dbname_input.text(),
            "user": self.user_input.text(),
            "password": self.password_input.text(),
        }
        return settings

    def set_data(self):
        # Устанавливаем статус соединения
        self.set_status()

        if self.data_connect:
            if self.data_connect.get('host'):
                self.host_input.setText(self.data_connect['host'])
            if self.data_connect.get('port'):
                self.port_input.setText(self.data_connect['port'])
            if self.data_connect.get('dbname'):
                self.dbname_input.setText(self.data_connect['dbname'])
            if self.data_connect.get('user'):
                self.user_input.setText(self.data_connect['user'])
            if self.data_connect.get('password'):
                self.password_input.setText(self.data_connect['password'])

