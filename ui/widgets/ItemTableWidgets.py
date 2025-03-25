from PyQt5 import QtCore, QtGui, QtWidgets


class HeaderItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text: str, widget_type: str, parent=None):
        super().__init__(text)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)
        self.widget_type = widget_type

    def get_resize_mode(self) -> QtWidgets.QHeaderView.ResizeMode:
        """Возвращает режим изменения размера в зависимости от типа виджета"""
        if self.widget_type == "text":
            return QtWidgets.QHeaderView.Stretch
        elif self.widget_type == "select":
            return QtWidgets.QHeaderView.Stretch
        elif self.widget_type == "boolean":
            return QtWidgets.QHeaderView.Fixed
        elif self.widget_type == "number":
            return QtWidgets.QHeaderView.Fixed
        elif self.widget_type == "action":
            return QtWidgets.QHeaderView.Fixed
        return QtWidgets.QHeaderView.Stretch

    def get_column_width(self) -> int:
        """Возвращает ширину колонки в зависимости от типа виджета"""
        if self.widget_type == "select":
            return 150
        elif self.widget_type == "number":
            return 130
        elif self.widget_type == "boolean":
            return 80
        elif self.widget_type == "action":
            return 30
        return 0  # Для текстового поля ширина не фиксирована


class TextItemTableWidget(QtWidgets.QWidget):
    def __init__(self,
                 parent=None,
                 column: dict = None,
                 row: int = None,
                 event_on_changed: callable = None): # type: ignore
        """Инициализирует виджет текстового поля.

        Args:
            parent: Родительский виджет
            column: Словарь с настройками колонки
            row: Номер строки в таблице
            event_on_changed: Функция обратного вызова для обработки изменения текста
        """

        super().__init__(parent)
        self.column = column
        self.row = row
        self.event_on_changed = event_on_changed

        self.key = column['key']
        self.type = column['type']
        self.value = column['value']

        # Создаем layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Создаем текстовое поле
        self.text_edit = QtWidgets.QLineEdit()
        self.text_edit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.text_edit.textChanged.connect(lambda: self.event_on_changed(self.row, self.key, self.get_value()))

        layout.addWidget(self.text_edit)

        # Устанавливаем стили
        self.setStyleSheet("""
            QLineEdit {
                border: none;
                background-color: white;
                height: 100%;
            }
            QLineEdit:hover {
                border: 1px solid #808080;
            }
        """)

    def get_value(self):
        return self.text_edit.text()

    def set_value(self, value):
        self.text_edit.setText(str(value))


class SelectItemTableWidget(QtWidgets.QWidget):
    def __init__(self,
                 parent=None,
                 column: dict = None,
                 row: int = None,
                 event_on_changed: callable = None): # type: ignore
        super().__init__(parent)
        self.column = column
        self.row = row
        self.event_on_changed = event_on_changed

        self.key = column['key']
        self.type = column['type']
        self.value = column['value']

        # Создаем layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Создаем выпадающий список
        self.combo = QtWidgets.QComboBox()
        self.combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        for item in self.value:
            self.combo.addItem(item)

        self.combo.currentTextChanged.connect(lambda: self.event_on_changed(self.row, self.key, self.get_value()))
        layout.addWidget(self.combo)

        # Устанавливаем стили
        self.setStyleSheet("""
            QComboBox {
                border: none;
                padding: 2px;
                background-color: white;
                height: 100%;
            }
            QComboBox:hover {
                border: 1px solid #808080;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(resources/icons/dropdown-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)

    def get_value(self):
        return self.combo.currentText()

    def set_value(self, value):
        index = self.combo.findText(str(value))
        if index >= 0:
            self.combo.setCurrentIndex(index)
        else:
            self.combo.addItem(str(value))
            self.combo.setCurrentIndex(self.combo.count() - 1)


class BooleanItemTableWidget(QtWidgets.QWidget):
    def __init__(self,
                 parent=None,
                 column: dict = None,
                 row: int = None,
                 event_on_changed: callable = None): # type: ignore
        super().__init__(parent)
        self.column = column
        self.row = row
        self.event_on_changed = event_on_changed

        self.key = column['key']
        self.type = column['type']
        self.value = column['value']

        # Создаем layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # Создаем чекбокс
        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.checkbox.stateChanged.connect(lambda: self.event_on_changed(self.row, self.key, self.get_value()))
        layout.addWidget(self.checkbox)

        # Устанавливаем стили
        self.setStyleSheet("""
            QCheckBox {
                spacing: 5px;
                height: 100%;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)

    def get_value(self):
        return self.checkbox.isChecked()

    def set_value(self, value):
        self.checkbox.setChecked(bool(value))


class NumberItemTableWidget(QtWidgets.QWidget):
    def __init__(self,
                 parent=None,
                 column: dict = None,
                 row: int = None,
                 event_on_changed: callable = None): # type: ignore
        super().__init__(parent)
        self.column = column
        self.row = row
        self.event_on_changed = event_on_changed

        self.key = column['key']
        self.type = column['type']
        self.value = column['value']

        # Создаем layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Создаем числовое поле
        self.spinbox = QtWidgets.QSpinBox()
        self.spinbox.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.spinbox.setRange(-999999, 999999)
        self.spinbox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.spinbox.valueChanged.connect(lambda: self.event_on_changed(self.row, self.key, self.get_value()))
        layout.addWidget(self.spinbox)

        # Устанавливаем стили
        self.setStyleSheet("""
            QSpinBox {
                border: none;
                padding: 2px;
                background-color: white;
                height: 100%;
            }
            QSpinBox:hover {
                border: 1px solid #808080;
            }
        """)

    def get_value(self):
        return self.spinbox.value()

    def set_value(self, value):
        self.spinbox.setValue(int(value))


class ActionItemTableWidget(QtWidgets.QWidget):
    def __init__(self,
                 parent=None,
                 column: dict = None,
                 row: int = None,
                 event_on_changed: callable = None): # type: ignore

        super().__init__(parent)
        self.column = column
        self.row = row
        self.event_on_changed = event_on_changed

        self.key = column['key']
        self.type = column['type']
        self.value = column['value']

        # Создаем layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # Создаем кнопку
        self.button = QtWidgets.QPushButton("×")
        self.button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        layout.addWidget(self.button)

        # Устанавливаем стили
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                color: #666666;
                font-size: 14px;
                padding: 0px;
            }
            QPushButton:hover {
                color: #ff0000;
            }
            QPushButton:pressed {
                color: #cc0000;
            }
        """)

        # Подключаем сигнал
        self.button.clicked.connect(self.event_on_changed)


    def get_value(self):
        return None

    def set_value(self, value):
        pass



