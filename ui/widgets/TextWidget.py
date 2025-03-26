import os
import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets

from ui.widgets.PopoverWidget import PopoverWidget



class TextWidget(QtWidgets.QWidget):
    """Виджет для отображения и редактирования текстового поля.

    Attributes:
        working_dir (Path): Путь к рабочей директории приложения
        config (dict): Конфигурация виджета, содержащая:
            - name (str): Название поля
            - placeholder (str, optional): Текст-подсказка для поля ввода
    """

    def __init__(self,
                 parent=None,
                 config: dict = None,
                 key: str = None,
                 app = None,
                 event_on_changed = None,
                 event_open_sql_script = None,
                 event_run_sql_script = None): # type: ignore

        """Инициализирует виджет текстового поля.

        Args:
            parent: Родительский виджет
            config (dict): Конфигурация виджета
        """
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.working_dir = self.app.working_dir
        self.config = config
        self.key = key

        self.event_on_changed = event_on_changed
        self.event_open_sql_script = event_open_sql_script
        self.event_run_sql_script = event_run_sql_script
        self.icons = {}

        self._load_icons()
        self._setup_ui()
        self._load_stylesheet()
        self.load_data()

        # Подключаем сигнал изменения текста
        self.lineEdit.textChanged.connect(self._on_text_changed)

    def _load_stylesheet(self):
        """Загружает и применяет стили для виджетов из QSS файла.

        Стили загружаются из файла TextWidget.qss в директории resources/styles.
        Применяются к кнопке помощи и полю ввода.
        """

        style_path = self.app.file_service.get_stylesheet_path("TextWidget.qss")

        try:
            with open(style_path, "r", encoding='utf-8') as f:
                self.stylesheet = f.read()

            self.btnHelp.setStyleSheet(self.stylesheet)
            self.lineEdit.setStyleSheet(self.stylesheet)
        except Exception as e:
            print(f"Ошибка загрузки стилей: {e}")
            print(f"Путь к файлу стилей: {style_path}")
            print(f"Текущая директория: {os.getcwd()}")
            print(f"MEIPASS: {getattr(sys, '_MEIPASS', 'Не установлен')}")

    def _load_icons(self):
        """Загружает иконки для кнопок приложения.

        Загружает следующие иконки:
            - plus: Иконка добавления
            - x: Иконка удаления
            - download: Иконка сохранения"""
        self.icons["load_item"] = QtGui.QIcon()
        self.icons["load_item"].addPixmap(QtGui.QPixmap(":/icon_button/resources/icons/load_item.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.icons["sql_script"] = QtGui.QIcon()
        self.icons["sql_script"].addPixmap(QtGui.QPixmap(":/icon_button/resources/icons/sql_script.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)


    def _setup_ui(self):
        """Создает и настраивает элементы пользовательского интерфейса.

        Создает:
            - Вертикальный layout для всего виджета
            - Горизонтальный layout для заголовка и кнопки помощи
            - Label с названием поля
            - Кнопку помощи
            - Поле ввода текста
        """
        # Создаем основной layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")

        # Создаем горизонтальный сплиттер
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

         # Создаем горизонтальный сплиттер
        self.horizontalLayout_1 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_1.setSpacing(3)

        # Добавляем поле ввода
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setObjectName(f"lineEdit_{self.config['name']}")
        self.horizontalLayout_1.addWidget(self.lineEdit)

        self.horizontalLayout_1.setStretch(0, 12)

        # Добавляем кнопку загрузки
        self.btnSQLScript = QtWidgets.QPushButton(self)
        self.btnSQLScript.setObjectName(f"btnSQLScript_{self.config['name']}")
        self.btnSQLScript.setMaximumSize(QtCore.QSize(25, 25))
        self.btnSQLScript.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnSQLScript.setIcon(self.icons["sql_script"])
        self.btnSQLScript.setIconSize(QtCore.QSize(16, 16))
        self.btnSQLScript.clicked.connect(self._on_sql_script)

        self.horizontalLayout_1.addWidget(self.btnSQLScript)
        self.horizontalLayout_1.addStretch()

        # Добавляем кнопку загрузки
        self.btnLoad = QtWidgets.QPushButton(self)
        self.btnLoad.setObjectName(f"btnLoad_{self.config['name']}")
        self.btnLoad.setMaximumSize(QtCore.QSize(25, 25))
        self.btnLoad.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnLoad.setIcon(self.icons["load_item"])
        self.btnLoad.setIconSize(QtCore.QSize(16, 16))
        self.btnLoad.clicked.connect(self._on_load_data)

        self.horizontalLayout_1.addWidget(self.btnLoad)
        self.horizontalLayout_1.addStretch()

        self.verticalLayout.addLayout(self.horizontalLayout_1)

    def load_data(self):
        """Загружает данные из конфигурации в виджеты.

        Устанавливает:
            - Текст label из config['name']
            - Текст-подсказку из config['placeholder']
        """
        if self.config and 'name' in self.config:
            self.label.setText(self.config['name'])
        if self.config and 'placeholder' in self.config:
            self.lineEdit.setPlaceholderText(self.config['placeholder'])

        if self.config and self.key == 'dag_owner':
            self.set_value(self.app.user_name)

        if self.config and self.key in self.app.sql_scripts.keys():
            self.btnLoad.show()
            self.btnSQLScript.show()
        else:
            self.btnLoad.hide()
            self.btnSQLScript.hide()

        self._on_text_changed(self.get_value())

    def get_value(self) -> str:
        """Возвращает текущее значение из поля ввода.

        Returns:
            str: Текст, введенный пользователем
        """
        return self.lineEdit.text()

    def set_value(self, value: str):
        """Устанавливает значение в поле ввода.

        Args:
            value (str): Текст для установки в поле ввода
        """
        self.lineEdit.setText(str(value))

    def _on_text_changed(self, text: str):
        """Обработчик события изменения текста.

        Args:
            text (str): Новый текст в поле ввода
        """
        if self.event_on_changed:
            self.event_on_changed(key=self.key, value=text)
        else:
            self.app.logger_service.error(f"event_on_changed не установлен для {self.__class__.__name__} - {self.key}")
            raise ValueError(f"event_on_changed не установлен для {self.__class__.__name__} - {self.key}")

        if self.key == 'object_name':
            self.app.file_service.set_file_name_config_save(text)

    def _on_load_data(self):
        self.event_run_sql_script(key=self.key, value=self.get_value())

    def _on_sql_script(self):
        self.event_open_sql_script(key=self.key, value=self.get_value())


    def _show_help(self):
        """Обработчик события нажатия на кнопку помощи."""
        self.popover = PopoverWidget(parent=self, text=self.config['help'])
        self.popover.move(self.btnHelp.mapToGlobal(self.btnHelp.rect().bottomLeft()))
        self.popover.show()
