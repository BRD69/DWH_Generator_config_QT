import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFrame,
    QHBoxLayout,
)
import psycopg2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import json
from pathlib import Path

class ClickHouseWidget(QWidget):
    def __init__(self, parent=None, working_dir=None, data_connect=None, app=None):
        super().__init__(parent)
        self.stylesheet = ""
        self.working_dir = working_dir
        self.data_connect = data_connect
        self.app = app
        self.setObjectName("ch_widget")

        self._setup_ui()
        self._load_stylesheet()

        self.set_data()

    def _load_stylesheet(self):
        """Загружает стили для виджета."""
        with open(self.working_dir / "resources" / "styles" / "SQLWidget.qss", "r") as f_pg_widget:
            self.stylesheet = f_pg_widget.read()

        self.setStyleSheet(self.stylesheet)


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

        # Поля для ввода данных
        self.host_input = QLineEdit(self)
        self.host_input.setObjectName("input_field")
        self.host_input.setPlaceholderText("Хост (например, localhost)")
        fields_layout.addWidget(QLabel("Хост:"))
        fields_layout.addWidget(self.host_input)

        self.port_input = QLineEdit(self)
        self.port_input.setObjectName("input_field")
        self.port_input.setPlaceholderText("Порт (например, 9999)")
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

