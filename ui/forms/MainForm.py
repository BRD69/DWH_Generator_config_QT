from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from ui.widgets.ActionsConnectWidget import ActionsConnectWidget
from ui.widgets.LoadingWidget import LoadingWidget
from ui.widgets.NotificationWidget import NotificationWidget



class UiMainWindow(QtWidgets.QMainWindow):
    """Главное окно приложения.

    Attributes:
        working_dir (Path): Путь к рабочей директории приложения
        stylesheet (str): Строка со стилями приложения
        icons (dict): Словарь с иконками приложения
    """

    def __init__(self, app): # type: ignore
        """Инициализирует главное окно приложения.

        Args:
            working_dir (Path): Путь к рабочей директории приложения
        """
        super().__init__()
        self.stylesheet = ""
        self.icons = {}
        self.working_dir = app.working_dir
        self.app = app

        self._load_icons()
        self._setup_ui()
        self._load_stylesheet()
        self._setup_toolbars()
        self._setup_toolbars_status()
        self._connect_signals()

    # =============== Настройка стилей ===============
    def _load_stylesheet(self):
        """Загружает и применяет стили для всех виджетов главного окна.

        Загружает стили из файла MainForm.qss и применяет их ко всем основным
        виджетам окна, включая фреймы, кнопки и таблицу.
        """
        with open(self.working_dir / "resources" / "styles" / "MainForm.qss", "r") as f_main_form:
            self.stylesheet = f_main_form.read()

        with open(self.working_dir / "resources" / "styles" / "ButtonToolBar.qss", "r") as f_button_tool_bar:
            self.stylesheet_button_tool_bar = f_button_tool_bar.read()

        with open(self.working_dir / "resources" / "styles" / "ButtonToolBarStatus.qss", "r") as f_button_tool_bar_status:
            self.stylesheet_button_tool_bar_status = f_button_tool_bar_status.read()

        self.setStyleSheet(self.stylesheet)
        self.centralwidget.setStyleSheet(self.stylesheet)
        self.frame_content.setStyleSheet(self.stylesheet)
        self.frame_content_left.setStyleSheet(self.stylesheet)
        self.toolBox_fields.setStyleSheet(self.stylesheet)
        self.frame_content_right.setStyleSheet(self.stylesheet)
        self.frame_control_table.setStyleSheet(self.stylesheet)
        self.btnAdd.setStyleSheet(self.stylesheet)
        self.btnClear.setStyleSheet(self.stylesheet)
        self.table_fields.setStyleSheet(self.stylesheet)

        self.toolBar.setStyleSheet(self.stylesheet_button_tool_bar)
        self.toolBarStatus.setStyleSheet(self.stylesheet_button_tool_bar_status)

    # =============== Настройка иконки ===============
    def _load_icons(self):
        """Загружает иконки для кнопок приложения.

        Загружает следующие иконки:
            - plus: Иконка добавления
            - x: Иконка удаления
            - download: Иконка сохранения
            - upload: Иконка загрузки
            - search: Иконка поиска
            - gear: Иконка настроек
            - git: Иконка git
        """
        self.icons["plus"] = QtGui.QIcon()
        self.icons["plus"].addPixmap(QtGui.QPixmap(":/icon_button/resources/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.icons["x"] = QtGui.QIcon()
        self.icons["x"].addPixmap(QtGui.QPixmap(":/icon_button/resources/icons/x.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.icons["save"] = QtGui.QIcon()
        self.icons["save"].addPixmap(QtGui.QPixmap(":/icon_button/resources/icons/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.icons["upload"] = QtGui.QIcon()
        self.icons["upload"].addPixmap(QtGui.QPixmap(":/icon_button/resources/icons/load.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.icons["search"] = QtGui.QIcon()
        self.icons["search"].addPixmap(QtGui.QPixmap(":/icon_button/resources/icons/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.icons["gear"] = QtGui.QIcon()
        self.icons["gear"].addPixmap(QtGui.QPixmap(":/icon_button/resources/icons/gear.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.icons["git"] = QtGui.QIcon()
        self.icons["git"].addPixmap(QtGui.QPixmap(":/icon_button/resources/icons/git.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.icons["load_table"] = QtGui.QIcon()
        self.icons["load_table"].addPixmap(QtGui.QPixmap(":/icon_button/resources/icons/load_table.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.icons["load_item"] = QtGui.QIcon()
        self.icons["load_item"].addPixmap(QtGui.QPixmap(":/icon_button/resources/icons/load_item.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

    # =============== Настройка интерфейса ===============
    def _setup_ui(self):
        """Создает и настраивает пользовательский интерфейс главного окна.

        Создает основную структуру окна:
            - Центральный виджет с вертикальным layout
            - Левая панель с деревом полей
            - Правая панель с таблицей
            - Нижняя панель с кнопками управления
            - Меню приложения
        """
        self.setObjectName("MainWindow")
        self.resize(1200, 850)

        self.centralwidget = QtWidgets.QWidget(parent=self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")

        self.frame_content = QtWidgets.QFrame(self.centralwidget)
        self.frame_content.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_content.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_content.setObjectName("frame_content")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_content)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.frame_content_left = QtWidgets.QFrame(self.frame_content)
        self.frame_content_left.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_content_left.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_content_left.setObjectName("frame_content_left")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_content_left)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(3)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")

        self.toolBox_fields = QtWidgets.QToolBox(self.frame_content_left)
        self.toolBox_fields.setObjectName("toolBox_fields")

        self.gridLayout.addWidget(self.toolBox_fields, 0, 0, 1, 1)
        self.horizontalLayout.addWidget(self.frame_content_left)
        self.frame_content_right = QtWidgets.QFrame(self.frame_content)
        self.frame_content_right.setBaseSize(QtCore.QSize(1200, 800))

        self.frame_content_right.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_content_right.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_content_right.setObjectName("frame_content_right")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_content_right)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_control_table = QtWidgets.QFrame(self.frame_content_right)

        self.frame_control_table.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_control_table.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_control_table.setObjectName("frame_control_table")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_control_table)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnAdd = QtWidgets.QPushButton(self.frame_control_table)

        self.btnAdd.setIcon(self.icons["plus"])
        self.btnAdd.setObjectName("btnAdd")
        self.horizontalLayout_2.addWidget(self.btnAdd)
        self.btnClear = QtWidgets.QPushButton(self.frame_control_table)

        self.btnClear.setText("")
        self.btnClear.setIcon(self.icons["x"])
        self.btnClear.setObjectName("btnClear")
        self.horizontalLayout_2.addWidget(self.btnClear)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_2.addWidget(self.frame_control_table)

        self.table_fields = QtWidgets.QTableWidget(self.frame_content_right)
        self.table_fields.setAutoFillBackground(False)
        self.table_fields.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_fields.setAlternatingRowColors(True)
        self.table_fields.setObjectName("table_fields")

        self.table_fields.horizontalHeader().setCascadingSectionResizes(False)
        self.table_fields.horizontalHeader().setHighlightSections(False)
        self.table_fields.horizontalHeader().setSortIndicatorShown(False)
        self.table_fields.horizontalHeader().setStretchLastSection(True)
        self.table_fields.verticalHeader().setVisible(True)
        self.table_fields.verticalHeader().setCascadingSectionResizes(True)
        self.table_fields.verticalHeader().setSortIndicatorShown(False)
        self.table_fields.verticalHeader().setStretchLastSection(False)
        self.verticalLayout_2.addWidget(self.table_fields)
        self.verticalLayout_2.setStretch(1, 12)
        self.horizontalLayout.addWidget(self.frame_content_right)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)
        self.verticalLayout.addWidget(self.frame_content)

        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 973, 24))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuParametrs = QtWidgets.QMenu(self.menubar)
        self.menuParametrs.setObjectName("menuParametrs")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        # self.setStatusBar(self.statusbar)

        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setMinimumSize(QtCore.QSize(0, 30))
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.toolBarStatus = QtWidgets.QToolBar(self)
        self.toolBarStatus.setMaximumHeight(25)

        self.toolBarStatus.setObjectName("toolBarStatus")
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolBarStatus)

        self.actionExit = QtWidgets.QAction(self)
        self.actionExit.setObjectName("actionExit")
        self.actionConfig = QtWidgets.QAction(self)
        self.actionConfig.setObjectName("actionConfig")
        self.actionSettings = QtWidgets.QAction(self)
        self.actionSettings.setObjectName("actionSettings")
        self.menuFile.addAction(self.actionExit)
        self.menuParametrs.addAction(self.actionConfig)
        self.menuParametrs.addAction(self.actionSettings)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuParametrs.menuAction())

        self.notification = NotificationWidget(self)
        self.loading = LoadingWidget(self)

        self._retranslateUi()
        self.toolBox_fields.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    # =============== Перевод текстов ===============
    def _retranslateUi(self):
        """Устанавливает текстовые значения для всех элементов интерфейса.

        Задает:
            - Заголовок окна
            - Тексты кнопок
            - Названия пунктов меню
        """
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btnAdd.setText(_translate("MainWindow", "Добавить"))
        self.table_fields.setSortingEnabled(False)
        self.menuFile.setTitle(_translate("MainWindow", "Файл"))
        self.menuParametrs.setTitle(_translate("MainWindow", "Параметры"))
        self.actionExit.setText(_translate("MainWindow", "Выход"))
        self.actionConfig.setText(_translate("MainWindow", "Config"))
        self.actionSettings.setText(_translate("MainWindow", "Настройки"))

    # =============== Настройка панелей инструментов ===============
    def _setup_toolbars(self):
        self.toolBar.setIconSize(QtCore.QSize(15, 15))
        # Создаем выпадающий список (QComboBox)

        self.toolBar.addWidget(QtWidgets.QLabel("Конфигурация:"))
        self.combo_box_configs = QtWidgets.QComboBox()
        self.combo_box_configs.setCurrentIndex(0)
        self.combo_box_configs.setObjectName("combo_box_configs")
        self.combo_box_configs.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.combo_box_configs.setMinimumWidth(120)
        self.toolBar.addWidget(self.combo_box_configs)

        self.toolBar.addSeparator()

        self.action_save = QtWidgets.QAction(self.icons["save"], "Сохранить", self)
        self.toolBar.addAction(self.action_save)

        self.action_load = QtWidgets.QAction(self.icons["upload"], "Загрузить", self)
        self.toolBar.addAction(self.action_load)

        self.action_view = QtWidgets.QAction(self.icons["search"], "Просмотр", self)
        self.toolBar.addAction(self.action_view)

        # self.toolBar.addSeparator()

        # self.toolBar.addWidget(QtWidgets.QLabel("Git"))

        self.action_git = QtWidgets.QAction(self.icons["git"], "Git", self)
        self.toolBar.addAction(self.action_git)

        # self.toolBar.addSeparator()

        self.action_load_table = QtWidgets.QAction(self.icons["load_table"], "Загрузить таблицу", self)
        self.toolBar.addAction(self.action_load_table)

        # self.toolBar.addSeparator()

        self.action_settings = QtWidgets.QAction(self.icons["gear"], "Настройки", self)
        self.toolBar.addAction(self.action_settings)

        self.action_test_notification = QtWidgets.QAction(self.icons["load_table"], "Тестовое уведомление", self)
        self.toolBar.addAction(self.action_test_notification)

        self.toolBar.widgetForAction(self.action_save).setCursor(Qt.PointingHandCursor)
        self.toolBar.widgetForAction(self.action_load).setCursor(Qt.PointingHandCursor)
        self.toolBar.widgetForAction(self.action_view).setCursor(Qt.PointingHandCursor)
        self.toolBar.widgetForAction(self.action_git).setCursor(Qt.PointingHandCursor)
        self.toolBar.widgetForAction(self.action_settings).setCursor(Qt.PointingHandCursor)
        self.toolBar.widgetForAction(self.action_load_table).setCursor(Qt.PointingHandCursor)
    # =============== Настройка панелей инструментов статуса ===============
    def _setup_toolbars_status(self):
        self.toolBarStatus.setIconSize(QtCore.QSize(10, 10))
        self.toolBarStatus.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolBarStatus.setMovable(False)  # Фиксируем панель
        self.toolBarStatus.setFloatable(False)  # Запрещаем перемещение

        self.action_connect_pg = ActionsConnectWidget(name="PostgreSQL")
        self.toolBarStatus.addAction(self.action_connect_pg)

        # self.action_connect_ch = ActionsConnectWidget(name="ClickHouse")
        # self.toolBarStatus.addAction(self.action_connect_ch)

        # Добавляем растягивающий элемент
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.toolBarStatus.addWidget(spacer)

        self.toolBarStatus.addWidget(QtWidgets.QLabel(f"{self.app.user_name}"))
        self.toolBarStatus.addWidget(QtWidgets.QLabel(f" {self.app.version}"))

        # Добавляем отступ слева (пустой QWidget с фиксированной шириной)
        spacer = QtWidgets.QWidget()
        spacer.setFixedWidth(10)  # Отступ 20 пикселей
        self.toolBarStatus.addWidget(spacer)

    # =============== Подключение сигналов ===============
    def _connect_signals(self):
        """Подключает сигналы для всех виджетов."""
        self.btnAdd.clicked.connect(self._event_btn_clicked_add_field_table)
        self.btnClear.clicked.connect(self._event_btn_clicked_clear_fields_table)

        self.action_save.triggered.connect(self._event_btn_clicked_save_fields_table)
        self.action_load.triggered.connect(self._event_btn_clicked_load_fields_table)
        self.action_view.triggered.connect(self._event_btn_clicked_view_fields_table)
        self.action_git.triggered.connect(self._event_btn_clicked_open_git_form)
        self.action_settings.triggered.connect(self._event_btn_clicked_settings_fields)
        self.action_connect_pg.triggered.connect(self._event_btn_clicked_open_connection_pg_form)
        # self.action_connect_ch.triggered.connect(self._connect_ch)

        self.action_test_notification.triggered.connect(self._event_btn_clicked_test_notification)

    # =============== Обработчики событий ===============
    def _event_btn_clicked_add_field_table(self):
        """Обработчик события нажатия на кнопку добавления поля."""
        pass

    def _event_btn_clicked_clear_fields_table(self):
        """Обработчик события нажатия на кнопку очистки полей."""
        pass

    def _event_btn_clicked_save_fields_table(self):
        """Обработчик события нажатия на кнопку сохранения полей."""
        pass

    def _event_btn_clicked_load_fields_table(self):
        """Обработчик события нажатия на кнопку загрузки полей."""
        pass

    def _event_btn_clicked_view_fields_table(self):
        """Обработчик события нажатия на кнопку просмотра полей."""
        pass

    def _event_btn_clicked_open_git_form(self):
        """Обработчик события нажатия на кнопку git."""
        pass

    def _event_btn_clicked_open_connection_pg_form(self):
        """Обработчик события нажатия на кнопку подключения к PostgreSQL."""
        pass

    def _event_btn_clicked_settings_fields(self):
        """Обработчик события нажатия на кнопку настроек."""
        pass

    def _event_btn_clicked_test_notification(self):
        """Обработчик события нажатия на кнопку тестового уведомления."""
        # self.notification.show_notification("Тестовое уведомление", "info")
        self.loading.show_loading("Тестовое уведомление")
        self.loading.update_status("Обработка результатов...", 45)
        # self.loading.hide_loading()


    def load_field_data(self):
        """Загружает данные из файла JSON."""
        pass
