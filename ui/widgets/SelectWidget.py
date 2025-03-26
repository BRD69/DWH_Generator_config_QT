import os
import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets

from ui.widgets.PopoverWidget import PopoverWidget


class SelectWidget(QtWidgets.QWidget):
    """Виджет для отображения и редактирования поля выбора из списка.

    Attributes:
        working_dir (Path): Путь к рабочей директории приложения
        config (dict): Конфигурация виджета, содержащая:
            - name (str): Название поля
            - options (list): Список вариантов выбора
            - default (str, optional): Значение по умолчанию
            - help_text (str, optional): Текст подсказки
    """

    def __init__(self,
                 parent=None,
                 config: dict = None,
                 key: str = None,
                 app = None,
                 event_on_changed = None): # type: ignore
        """Инициализирует виджет выбора из списка.

        Args:
            parent: Родительский виджет
            working_dir (Path): Путь к рабочей директории приложения
            config (dict): Конфигурация виджета
        """
        super().__init__(parent)
        self.app = app
        self.working_dir = self.app.working_dir
        self.config = config
        self.key = key
        self.event_on_changed = event_on_changed

        self._setup_ui()
        self._load_stylesheet()
        self.load_data()

        # Подключаем сигнал изменения значения
        self.comboBox.currentTextChanged.connect(self._on_value_changed)

    def _load_stylesheet(self):
        """Загружает и применяет стили для виджетов из QSS файла.

        Стили загружаются из файла SelectWidget.qss в директории resources/styles.
        Применяются к кнопке помощи и выпадающему списку.
        """
        style_path = self.app.file_service.get_stylesheet_path("SelectWidget.qss")

        try:
            with open(style_path, "r", encoding='utf-8') as f:
                self.stylesheet = f.read()

            self.btnHelp.setStyleSheet(self.stylesheet)
            self.comboBox.setStyleSheet(self.stylesheet)
        except Exception as e:
            self.logger.error(f"Ошибка загрузки стилей: {e}")
            self.logger.error(f"Путь к файлу стилей: {style_path}")
            self.logger.error(f"Текущая директория: {os.getcwd()}")
            self.logger.error(f"MEIPASS: {getattr(sys, '_MEIPASS', 'Не установлен')}")


    def _setup_ui(self):
        """Создает и настраивает элементы пользовательского интерфейса.

        Создает:
            - Вертикальный layout для всего виджета
            - Горизонтальный layout для заголовка и кнопки помощи
            - Label с названием поля
            - Кнопку помощи
            - Выпадающий список
        """
        # Создаем основной layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")

        # Создаем горизонтальный layout
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)

        # Добавляем label
        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName(f"label_{self.config['name']}")
        self.horizontalLayout.addWidget(self.label)

        # Добавляем кнопку помощи
        self.btnHelp = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.btnHelp.setSizePolicy(sizePolicy)
        self.btnHelp.setMinimumSize(QtCore.QSize(16, 16))
        self.btnHelp.setMaximumSize(QtCore.QSize(16, 16))
        self.btnHelp.setObjectName(f"btnHelp_{self.config['name']}")
        self.btnHelp.setText("?")
        self.btnHelp.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnHelp.clicked.connect(self._show_help)

        self.horizontalLayout.addWidget(self.btnHelp)
        # Добавляем растягивающийся спейсер
        self.horizontalLayout.addStretch()

        # Добавляем горизонтальный layout в основной layout
        self.verticalLayout.addLayout(self.horizontalLayout)

        # Добавляем выпадающий список
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setObjectName(f"comboBox_{self.config['name']}")
        self.verticalLayout.addWidget(self.comboBox)

    def load_data(self):
        """Загружает данные из конфигурации в виджеты.

        Устанавливает:
            - Текст label из config['name']
            - Список опций из config['options']
            - Значение по умолчанию из config['default']
        """
        if self.config and 'name' in self.config:
            self.label.setText(self.config['name'])

        if self.config and 'values' in self.config:
            self.comboBox.clear()
            for value in self.config['values']:
                self.comboBox.addItem(value['name'])

            self.comboBox.setCurrentIndex(0)
            self._on_value_changed(self.comboBox.currentText())

    def get_value(self) -> str:
        """Возвращает текущее выбранное значение.

        Returns:
            str: Текст выбранного элемента
        """
        return self.comboBox.currentText()

    def set_value(self, value: any):
        """Устанавливает выбранное значение.

        Args:
            value (str): Текст элемента для выбора
        """

        if isinstance(value, str):
            index = self.comboBox.findText(value)
            if index >= 0:
                self.comboBox.setCurrentIndex(index)
            else:
                self.comboBox.addItem(value)
                self.comboBox.setCurrentIndex(self.comboBox.count() - 1)
        elif isinstance(value, int):
            self.comboBox.setCurrentIndex(value)
        else:
            self.app.logger_service.error(f"Неверный тип значения для {self.__class__.__name__} - {self.key}")
            raise ValueError(f"Неверный тип значения для {self.__class__.__name__} - {self.key}")

    def _on_value_changed(self, value: str):
        """Обработчик события изменения значения.

        Args:
            value (str): Новое значение в поле ввода
        """
        if self.event_on_changed:
            for val in self.config['values']:
                if val['name'] == value:
                    value = val['value']
            self.event_on_changed(key=self.key, value=value)
        else:
            self.app.logger_service.error(f"event_on_changed не установлен для {self.__class__.__name__} - {self.key}")
            raise ValueError(f"event_on_changed не установлен для {self.__class__.__name__} - {self.key}")


    def _show_help(self):
        """Обработчик события нажатия на кнопку помощи."""
        self.popover = PopoverWidget(parent=self, text=self.config['help'])
        self.popover.move(self.btnHelp.mapToGlobal(self.btnHelp.rect().bottomLeft()))
        self.popover.show()
