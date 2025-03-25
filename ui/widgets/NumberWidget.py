from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets

from ui.widgets.PopoverWidget import PopoverWidget



class NumberWidget(QtWidgets.QWidget):
    """Виджет для отображения и редактирования числового поля.

    Attributes:
        working_dir (Path): Путь к рабочей директории приложения
        config (dict): Конфигурация виджета, содержащая:
            - name (str): Название поля
            - min (int, optional): Минимальное значение (по умолчанию: -999999)
            - max (int, optional): Максимальное значение (по умолчанию: 999999)
            - default (int, optional): Значение по умолчанию (по умолчанию: 0)
    """

    def __init__(self,
                 parent=None,
                 config: dict = None,
                 key: str = None,
                 app = None,
                 event_on_changed = None): # type: ignore
        """Инициализирует виджет числового поля.

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

        # Подключаем сигнал изменения текста
        self.spinBox.valueChanged.connect(self._on_value_changed)

    def _load_stylesheet(self):
        """Загружает и применяет стили для виджетов из QSS файла.

        Стили загружаются из файла NumberWidget.qss в директории resources/styles.
        Применяются к кнопке помощи и полю ввода числа.
        """
        with open(self.working_dir / "resources" / "styles" / "NumberWidget.qss", "r") as f:
            self.stylesheet = f.read()

        self.btnHelp.setStyleSheet(self.stylesheet)
        self.spinBox.setStyleSheet(self.stylesheet)

    def _setup_ui(self):
        """Создает и настраивает элементы пользовательского интерфейса.

        Создает:
            - Вертикальный layout для всего виджета
            - Горизонтальный layout для заголовка и кнопки помощи
            - Label с названием поля
            - Кнопку помощи
            - Поле ввода числа
            - Разделительную линию
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

        # Добавляем поле ввода числа
        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBox.setObjectName(f"spinBox_{self.config['name']}")
        self.spinBox.setRange(
            self.config.get('min', -999999),
            self.config.get('max', 999999)
        )
        self.spinBox.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.verticalLayout.addWidget(self.spinBox)

    def load_data(self):
        """Загружает данные из конфигурации в виджеты.

        Устанавливает:
            - Текст label из config['name']
            - Значение по умолчанию из config['default']
            - Диапазон значений из config['min'] и config['max']
        """
        if self.config and 'name' in self.config:
            self.label.setText(self.config['name'])
        if self.config and 'default' in self.config:
            self.spinBox.setValue(self.config['default'])

        self._on_value_changed(self.get_value())

    def get_value(self) -> int:
        """Возвращает текущее значение из поля ввода.

        Returns:
            int: Число, введенное пользователем
        """
        return self.spinBox.value()

    def set_value(self, value: int):
        """Устанавливает значение в поле ввода.

        Args:
            value (int): Число для установки в поле ввода
        """
        if type(value) == str:
            value = int(value)
        else:
            value = value
        self.spinBox.setValue(value)

    def _on_value_changed(self, value: int):
        """Обработчик события изменения значения.

        Args:
            value (int): Новое значение в поле ввода
        """
        if self.event_on_changed:
            self.event_on_changed(key=self.key, value=value)
        else:
            self.app.logger_service.error(f"event_on_changed не установлен для {self.__class__.__name__} - {self.key}")
            raise ValueError(f"event_on_changed не установлен для {self.__class__.__name__} - {self.key}")

    def _show_help(self):
        """Обработчик события нажатия на кнопку помощи."""
        self.popover = PopoverWidget(parent=self, text=self.config['help'])
        self.popover.move(self.btnHelp.mapToGlobal(self.btnHelp.rect().bottomLeft()))
        self.popover.show()
