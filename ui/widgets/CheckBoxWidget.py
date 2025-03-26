import os
import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets

from ui.widgets.PopoverWidget import PopoverWidget


class CheckBoxWidget(QtWidgets.QWidget):
    """Виджет для отображения и редактирования логического поля (флажка).

    Attributes:
        working_dir (Path): Путь к рабочей директории приложения
        config (dict): Конфигурация виджета, содержащая:
            - name (str): Название поля
            - default (bool, optional): Значение по умолчанию (по умолчанию: False)
            - help_text (str, optional): Текст подсказки
    """

    def __init__(self,
                 parent=None,
                 config: dict = None,
                 key: str = None,
                 app = None,
                 event_on_changed = None): # type: ignore
        """Инициализирует виджет флажка.

        Args:
            parent: Родительский виджет
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
        self.checkBox.stateChanged.connect(self._on_value_changed)

    def _load_stylesheet(self):
        """Загружает и применяет стили для виджетов из QSS файла.

        Стили загружаются из файла CheckBoxWidget.qss в директории resources/styles.
        Применяются к кнопке помощи и флажку.
        """
        style_path = self.app.file_service.get_stylesheet_path("CheckBoxWidget.qss")

        try:
            with open(style_path, "r", encoding='utf-8') as f:
                self.stylesheet = f.read()

            self.btnHelp.setStyleSheet(self.stylesheet)
            self.checkBox.setStyleSheet(self.stylesheet)
        except Exception as e:
            print(f"Ошибка загрузки стилей: {e}")
            print(f"Путь к файлу стилей: {style_path}")
            print(f"Текущая директория: {os.getcwd()}")
            print(f"MEIPASS: {getattr(sys, '_MEIPASS', 'Не установлен')}")


    def _setup_ui(self):
        """Создает и настраивает элементы пользовательского интерфейса.

        Создает:
            - Вертикальный layout для всего виджета
            - Горизонтальный layout для флажка и кнопки помощи
            - Флажок с текстом
            - Кнопку помощи
        """
        # Создаем основной layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")

        # Создаем горизонтальный layout
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)

        # Добавляем флажок
        self.checkBox = QtWidgets.QCheckBox(self)
        self.checkBox.setObjectName(f"checkBox_{self.config['name']}")
        self.horizontalLayout.addWidget(self.checkBox)

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

    def load_data(self):
        """Загружает данные из конфигурации в виджеты.

        Устанавливает:
            - Текст флажка из config['name']
        """
        if self.config and 'name' in self.config:
            self.checkBox.setText(self.config['name'])

        self._on_value_changed(self.get_value())

    def get_value(self) -> bool:
        """Возвращает текущее состояние флажка.

        Returns:
            bool: True если флажок установлен, False в противном случае
        """
        return self.checkBox.isChecked()

    def set_value(self, value: bool):
        """Устанавливает состояние флажка.

        Args:
            value (bool): True для установки флажка, False для снятия
        """
        self.checkBox.setChecked(bool(value))

    def _on_value_changed(self, value: int):
        """Обработчик события изменения значения.

        Args:
            value (bool): Новое значение в поле ввода
        """
        if self.event_on_changed:
            if value == 2:
                value = 1
            elif value == 0:
                value = 0
            self.event_on_changed(key=self.key, value=value)
        else:
            self.app.logger_service.error(f"event_on_changed не установлен для {self.__class__.__name__} - {self.key}")
            raise ValueError(f"event_on_changed не установлен для {self.__class__.__name__} - {self.key}")


    def _show_help(self):
        """Обработчик события нажатия на кнопку помощи."""
        self.popover = PopoverWidget(parent=self, text=self.config['help'])
        self.popover.move(self.btnHelp.mapToGlobal(self.btnHelp.rect().bottomLeft()))
        self.popover.show()
