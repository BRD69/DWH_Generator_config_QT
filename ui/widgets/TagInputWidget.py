import os
import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSize

from ui.widgets.PopoverWidget import PopoverWidget


class Tag(QtWidgets.QWidget):
    """Виджет тега с текстом и кнопкой удаления.

    Attributes:
        text (str): Текст тега
        label (QLabel): Метка с текстом тега
        btnRemove (QPushButton): Кнопка удаления тега
    """

    def __init__(self, text: str, parent=None):
        """Инициализирует виджет тега.

        Args:
            text (str): Текст тега
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.text = text
        self._setup_ui()

    def _setup_ui(self):
        """Создает и настраивает элементы пользовательского интерфейса тега.

        Создает:
            - Горизонтальный layout
            - Метку с текстом
            - Кнопку удаления
        """
        # Создаем layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 4, 2)
        layout.setSpacing(4)

        # Добавляем метку
        self.label = QtWidgets.QLabel(self.text)
        self.label.setStyleSheet("background: transparent; padding: 0px;")

        # Добавляем кнопку удаления
        self.btnRemove = QtWidgets.QPushButton("×")
        self.btnRemove.setFixedSize(QSize(14, 14))
        self.btnRemove.clicked.connect(self.remove_self)

        layout.addWidget(self.label)
        layout.addWidget(self.btnRemove)

        # Устанавливаем фиксированную высоту для всего тега
        self.setFixedHeight(22)

    def remove_self(self):
        """Удаляет тег из родительского поля."""
        # Ищем родительский контейнер тегов
        parent = self.parent()
        while parent and not hasattr(parent, 'remove_tag'):
            parent = parent.parent()

        if parent and hasattr(parent, 'remove_tag'):
            parent.remove_tag(self)
            return True
        return False


class TagInputWidget(QtWidgets.QWidget):
    """Виджет для ввода и отображения списка тегов.

    Attributes:
        config (dict): Конфигурация виджета, содержащая:
            - name (str): Название поля
            - placeholder (str, optional): Текст-подсказка для поля ввода
            - default (list, optional): Список тегов по умолчанию
            - help_text (str, optional): Текст подсказки
    """

    def __init__(self,
                 parent=None,
                 app = None,
                 config: dict = None,
                 key: str = None,
                 event_on_changed = None): # type: ignore
        """Инициализирует виджет ввода тегов.

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

    def _load_stylesheet(self):
        """Загружает и применяет стили для виджетов из QSS файла.

        Стили загружаются из файла TagInputWidget.qss в директории resources/styles.
        Применяются к кнопке помощи и полю ввода тегов.
        """
        style_path = self.app.file_service.get_stylesheet_path("TagInputWidget.qss")
        try:
            with open(style_path, "r", encoding='utf-8') as f:
                self.stylesheet = f.read()
            self.btnHelp.setStyleSheet(self.stylesheet)
            self.frame.setStyleSheet(self.stylesheet)
        except Exception as e:
            print(f"Ошибка загрузки стилей: {e}")
            print(f"Путь к файлу стилей: {style_path}")
            print(f"Текущая директория: {os.getcwd()}")
            print(f"MEIPASS: {getattr(sys, '_MEIPASS', 'Не установлен')}")


    def _setup_ui(self):
        """Создает и настраивает элементы пользовательского интерфейса.

        Создает:
            - Вертикальный layout для всего виджета
            - Горизонтальный layout для заголовка и кнопки помощи
            - Label с названием поля
            - Кнопку помощи
            - Фрейм для тегов с полем ввода
        """
        # Создаем основной layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")

        # Создаем горизонтальный layout для заголовка
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
        self.horizontalLayout.addStretch()

        # Добавляем заголовок в основной layout
        self.verticalLayout.addLayout(self.horizontalLayout)

        # Создаем фрейм для тегов и поля ввода
        self.frame = QtWidgets.QFrame(self)
        self.frame.setObjectName(f"frame_{self.config['name']}")
        self.frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # Создаем layout для фрейма
        self.frameLayout = QtWidgets.QVBoxLayout(self.frame)
        self.frameLayout.setContentsMargins(5, 5, 5, 5)
        self.frameLayout.setSpacing(5)

        # Создаем контейнер для тегов
        self.tagsContainer = QtWidgets.QWidget(self.frame)
        self.tagsContainer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.tagsContainer.setMinimumHeight(30)

        # Создаем FlowLayout для тегов
        self.tagsLayout = FlowLayout(self.tagsContainer)
        self.tagsLayout.setSpacing(4)
        self.tagsLayout.setContentsMargins(0, 5, 5, 0)

        # Добавляем контейнер тегов в layout фрейма
        self.frameLayout.addWidget(self.tagsContainer)

        # Добавляем поле ввода
        self.inputField = QtWidgets.QLineEdit(self.frame)
        self.inputField.setObjectName(f"input_{self.config['name']}")
        self.inputField.returnPressed.connect(self.add_tag)
        self.frameLayout.addWidget(self.inputField)

        # Добавляем фрейм в основной layout
        self.verticalLayout.addWidget(self.frame)

        # Настраиваем размеры
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.frame.setMinimumHeight(40)

    def load_data(self):
        """Загружает данные из конфигурации в виджеты.

        Устанавливает:
            - Текст label из config['name']
            - Текст-подсказку из config['placeholder']
            - Теги по умолчанию из config['default']
        """
        if self.config and 'name' in self.config:
            self.label.setText(self.config['name'])

        if self.config and 'placeholder' in self.config:
            self.inputField.setPlaceholderText(self.config['placeholder'])
        else:
            self.inputField.setPlaceholderText("Введите и нажмите Enter...")

        if self.config and 'default' in self.config:
            for tag_text in self.config['default']:
                self.add_tag(tag_text)

        self._on_change_tags()

    def add_tag(self, text: str = None):
        """Добавляет новый тег в поле ввода.

        Args:
            text (str, optional): Текст тега. Если не указан, берется из поля ввода.
        """
        if text is None:
            text = self.inputField.text().strip()
            self.inputField.clear()

        if text:
            # Создаем тег с правильным родителем
            tag = Tag(text, parent=self)
            self.tagsLayout.addWidget(tag)
            self.adjust_height()
            self._on_change_tags()

    def remove_tag(self, tag: Tag):
        """Удаляет тег из списка.

        Args:
            tag (Tag): Виджет тега для удаления
        """
        # Находим индекс тега в layout
        for i in range(self.tagsLayout.count()):
            item = self.tagsLayout.itemAt(i)
            if item and item.widget() == tag:
                # Удаляем из layout
                item = self.tagsLayout.takeAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.hide()
                        widget.setParent(None)
                        widget.deleteLater()
                break

        # Обновляем layout
        self.tagsLayout.invalidate()
        self.update()
        self._on_change_tags()


    def _recalculate_layout(self):
        """Пересчитывает layout после изменений."""
        # Получаем текущие размеры
        width = self.tagsContainer.width()
        if width <= 0:
            return

        # Пересчитываем высоту контейнера
        height = self.tagsLayout.heightForWidth(width)
        if height > 0:
            self.tagsContainer.setMinimumHeight(max(height + 5, 30))

        # Пересчитываем высоту фрейма
        input_height = self.inputField.sizeHint().height()
        frame_height = height + input_height + 20
        self.frame.setMinimumHeight(max(frame_height, 70))

        # Обновляем геометрию
        self.tagsLayout.invalidate()
        self.tagsContainer.updateGeometry()
        self.frame.updateGeometry()

    def adjust_height(self):
        """Пересчитывает высоту фрейма в зависимости от количества тегов.

        Вычисляет необходимую высоту контейнера тегов на основе его содержимого
        и устанавливает соответствующую высоту для фрейма.
        """
        # Получаем текущую ширину контейнера
        width = self.tagsContainer.width()

        # Если нет тегов, устанавливаем минимальную высоту
        if self.tagsLayout.count() == 0:
            self.tagsContainer.setMinimumHeight(30)
            self.frame.setMinimumHeight(70)
            return

        # Вычисляем необходимую высоту для текущей ширины
        if width > 0:
            # Вычисляем высоту контента
            height = self.tagsLayout.heightForWidth(width)
            self.tagsContainer.setMinimumHeight(max(height + 5, 30))

            # Учитываем высоту поля ввода и отступы
            frame_height = height + self.inputField.height() + 20
            self.frame.setMinimumHeight(max(frame_height, 70))

            # Принудительно обновляем размеры
            self.tagsContainer.updateGeometry()
            self.frame.updateGeometry()
            self.update()

    def get_value(self) -> list:
        """Возвращает список текущих тегов.

        Returns:
            list: Список текстов тегов
        """
        tags = []
        for i in range(self.tagsLayout.count()):
            widget = self.tagsLayout.itemAt(i).widget()
            if isinstance(widget, Tag):
                tags.append(widget.text)
        return tags

    def set_value(self, values: list):
        """Устанавливает список тегов.

        Args:
            values (list): Список текстов тегов
        """
        # Очищаем текущие теги
        while self.tagsLayout.count():
            widget = self.tagsLayout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        # Добавляем новые теги
        for value in values:
            self.add_tag(str(value))

    def _on_change_tags(self):
        """Обработчик события изменения тегов.

        """
        if self.event_on_changed:
            self.event_on_changed(key=self.key, value=self.get_value())
        else:
            self.app.logger_service.error(f"event_on_changed не установлен для {self.__class__.__name__} - {self.key}")
            raise ValueError(f"event_on_changed не установлен для {self.__class__.__name__} - {self.key}")

    def _show_help(self):
        """Обработчик события нажатия на кнопку помощи."""
        self.popover = PopoverWidget(parent=self, text=self.config['help'])
        self.popover.move(self.btnHelp.mapToGlobal(self.btnHelp.rect().bottomLeft()))
        self.popover.show()


class FlowLayout(QtWidgets.QLayout):
    """Layout для размещения тегов в несколько строк с автоматическим переносом.

    Размещает элементы слева направо и сверху вниз, автоматически переносит на новую строку,
    когда элементы не помещаются по ширине. Учитывает минимальные размеры элементов и отступы.
    """

    def __init__(self, parent=None):
        """Инициализирует layout.

        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.itemList = []
        self.spacing_ = 0

    def addItem(self, item):
        """Добавляет элемент в layout."""
        self.itemList.append(item)
        self.invalidate()

    def count(self):
        """Возвращает количество элементов в layout."""
        return len(self.itemList)

    def itemAt(self, index):
        """Возвращает элемент по индексу."""
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        """Удаляет и возвращает элемент по индексу."""
        if 0 <= index < len(self.itemList):
            item = self.itemList.pop(index)
            self.invalidate()
            return item
        return None

    def setSpacing(self, spacing):
        """Устанавливает отступы между элементами."""
        self.spacing_ = spacing
        self.invalidate()

    def spacing(self):
        """Возвращает текущие отступы между элементами."""
        return self.spacing_

    def expandingDirections(self):
        """Возвращает направления, в которых layout может расширяться."""
        return Qt.Orientations()

    def hasHeightForWidth(self):
        """Указывает, что высота зависит от ширины."""
        return True

    def heightForWidth(self, width):
        """Вычисляет необходимую высоту для заданной ширины."""
        height = self._doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        """Устанавливает геометрию layout и всех его элементов."""
        super().setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self):
        """Возвращает рекомендуемый размер layout."""
        return self.minimumSize()

    def minimumSize(self):
        """Вычисляет минимальный размер layout."""
        size = QtCore.QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins()
        size += QtCore.QSize(margin.left() + margin.right(), margin.top() + margin.bottom())
        return size

    def invalidate(self):
        """Инвалидирует layout и уведомляет родительские виджеты."""
        super().invalidate()
        self.update()
        if self.parent():
            self.parent().updateGeometry()

    def _doLayout(self, rect, testOnly):
        """Выполняет расположение элементов в layout.

        Args:
            rect: Прямоугольник, в котором нужно расположить элементы
            testOnly: Если True, только вычисляет высоту, не перемещая элементы

        Returns:
            int: Необходимая высота для размещения всех элементов
        """
        margin = self.contentsMargins()
        x = rect.x() + margin.left()
        y = rect.y() + margin.top()
        lineHeight = 0
        spacing = self.spacing_
        maxWidth = rect.width() - margin.left() - margin.right()

        for item in self.itemList:
            itemSize = item.sizeHint()
            nextX = x + itemSize.width()

            if x > rect.x() + margin.left() and nextX > rect.x() + maxWidth:
                x = rect.x() + margin.left()
                y = y + lineHeight + spacing
                nextX = x + itemSize.width()
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), itemSize))

            x = nextX + spacing
            lineHeight = max(lineHeight, itemSize.height())

        return y + lineHeight - rect.y() + margin.bottom()


# === Запуск приложения ===
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = TagInputWidget()
    window.show()
    sys.exit(app.exec_())