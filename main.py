import json
import os
import sys
import getpass
import jinja2
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from services.config_service import ConfigService
from services.crypto_text_service import CryptoTextService
from settings import NAME_APP, AUTHOR_APP, DESCRIPTION_APP, LICENSE_APP, COPYRIGHT_APP, get_version_info
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QThread, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

from ui.forms.ContentForm import ContentForm
# from ui.forms.GitForm import GitForm
from ui.forms.MainForm import UiMainWindow
from ui.forms.SettingsForm import SettingsForm
from ui.widgets.CheckBoxWidget import CheckBoxWidget
from ui.widgets.ItemTableWidgets import ActionItemTableWidget, BooleanItemTableWidget, HeaderItem, NumberItemTableWidget, SelectItemTableWidget, TextItemTableWidget
from ui.widgets.LoadingWidget import LoadingWidget
from ui.widgets.NumberWidget import NumberWidget
from ui.widgets.SQLClickHouseWidget import ClickHouseWidget
from ui.widgets.SQLPostgreWidget import PostgreWidget
from ui.widgets.PageWidget import PageWidget
from ui.widgets.SQLViewerScript import SQLViewerScript
from ui.widgets.SelectWidget import SelectWidget
from ui.widgets.TagInputWidget import TagInputWidget
from ui.widgets.TextWidget import TextWidget
from ui.widgets.ViewJSONWidget import ViewJSONWidget
from ui.widgets.ViewTextWidget import ViewTextWidget
from ui.widgets.SplashScreen import SplashScreen
from services.postgres_service import PostgresService
from services.logger_service import LoggerService
from services.file_structure_service import FileStructureService


# Определение пути приложения в исполняемом файле Python, сгенерированном PyInstaller
if getattr(sys, 'frozen', False):
    # Если приложение запущено как exe
    Current_Path = os.path.dirname(sys.executable)
else:
    # Если приложение запущено как скрипт Python
    Current_Path = str(os.path.dirname(__file__))


class ApplicationSignals(QObject):
    """Класс для управления сигналами приложения."""

    # Сигналы для работы с конфигурацией
    config_loaded = pyqtSignal(dict)  # Сигнал успешной загрузки конфигурации
    config_saved = pyqtSignal()  # Сигнал успешного сохранения конфигурации
    config_error = pyqtSignal(str)  # Сигнал ошибки при работе с конфигурацией

    # Сигналы для работы с PostgreSQL
    postgres_connected = pyqtSignal(bool, str)  # Сигнал успешного подключения к PostgreSQL
    postgres_disconnected = pyqtSignal()  # Сигнал отключения от PostgreSQL
    postgres_error = pyqtSignal(str)  # Сигнал ошибки при работе с PostgreSQL

    # Сигналы для работы с файлами
    file_saved = pyqtSignal(str)  # Сигнал успешного сохранения файла
    file_loaded = pyqtSignal(str)  # Сигнал успешной загрузки файла
    file_error = pyqtSignal(str)  # Сигнал ошибки при работе с файлами

    # Сигналы для работы с Git
    git_updated = pyqtSignal()  # Сигнал успешного обновления Git
    git_error = pyqtSignal(str)  # Сигнал ошибки при работе с Git

    # Сигналы для работы с уведомлениями
    notification = pyqtSignal(str, str)  # Сигнал для отображения уведомления (тип, сообщение)

    # Сигналы для работы с загрузкой
    loading_started = pyqtSignal(str)  # Сигнал начала загрузки
    loading_finished = pyqtSignal()  # Сигнал окончания загрузки
    loading_error = pyqtSignal(str)  # Сигнал ошибки при загрузке

    # Сигналы для работы с формой
    form_loaded = pyqtSignal()  # Сигнал успешной загрузки формы
    form_error = pyqtSignal(str)  # Сигнал ошибки при загрузке формы

    # Сигналы для работы с таблицей
    table_loaded = pyqtSignal()  # Сигнал успешной загрузки таблицы
    table_error = pyqtSignal(str)  # Сигнал ошибки при загрузке таблицы

    # Сигналы для работы с настройками
    settings_loaded = pyqtSignal()  # Сигнал успешной загрузки настроек
    settings_saved = pyqtSignal()  # Сигнал успешного сохранения настроек
    settings_error = pyqtSignal(str)  # Сигнал ошибки при работе с настройками

    # Сигналы для работы с логами
    log_loaded = pyqtSignal()  # Сигнал успешной загрузки логов
    log_error = pyqtSignal(str)  # Сигнал ошибки при работе с логами

    # Сигналы для работы с криптографией
    crypto_encrypted = pyqtSignal()  # Сигнал успешного шифрования
    crypto_decrypted = pyqtSignal()  # Сигнал успешного дешифрования
    crypto_error = pyqtSignal(str)  # Сигнал ошибки при работе с криптографией

    # Сигналы для работы с файловой структурой
    structure_loaded = pyqtSignal()  # Сигнал успешной загрузки структуры
    structure_error = pyqtSignal(str)  # Сигнал ошибки при работе со структурой

    # Сигналы для работы с версией
    version_loaded = pyqtSignal()  # Сигнал успешной загрузки версии
    version_error = pyqtSignal(str)  # Сигнал ошибки при работе с версией

    # Сигналы для работы с пользователем
    user_loaded = pyqtSignal()  # Сигнал успешной загрузки пользователя
    user_error = pyqtSignal(str)  # Сигнал ошибки при работе с пользователем

    # Сигналы для работы с приложением
    app_started = pyqtSignal()  # Сигнал успешного запуска приложения
    app_error = pyqtSignal(str)  # Сигнал ошибки при запуске приложения

    # Сигналы для работы с splash screen
    splash_finished = pyqtSignal()  # Сигнал окончания отображения splash screen


class Application(QApplication):
    signal_postgres_connection_changed = pyqtSignal(bool, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Параметры приложения
        self.user_name = getpass.getuser()
        self.name = NAME_APP
        self.version_info = get_version_info()
        self.version = self.version_info['version']
        self.author = AUTHOR_APP
        self.description = DESCRIPTION_APP
        self.license = LICENSE_APP
        self.copyright = COPYRIGHT_APP

        # Инициализация базовых путей
        self.working_dir = Path(Current_Path)
        self.setWindowIcon(QtGui.QIcon("icon512.ico"))

        # Инициализация сигналов
        self.signals = ApplicationSignals()

        # Инициализация логгера
        log_dir = self.working_dir / "logs"
        self.logger_service = LoggerService("DWH_Generator", log_dir)
        self.logger = self.logger_service.get_logger()
        self.logger_service.info("Запуск приложения")

        # Инициализация сервисов
        self.crypto_service = CryptoTextService(
            logger_service=self.logger_service
            )

        self.file_service = FileStructureService(
            working_dir=self.working_dir,
            logger_service=self.logger_service
            )

        # Инициализация конфигурации
        self.config_service = ConfigService(
            working_dir=self.working_dir,
            logger_service=self.logger_service,
            file_service=self.file_service,
            crypto_service=self.crypto_service
            )

        # Загружаем конфигурацию
        self.config_fields = self.config_service.get_config_fields()
        self.config_pages = self.config_service.get_config_pages()
        self.config_output = self.config_service.get_config_output()
        self.sql_connect = self.config_service.get_sql_connect()
        self.sql_scripts = self.config_service.get_sql_scripts()
        self.columns_table = self.config_service.load_columns_table()

        # Инициализация PostgreSQL сервиса
        self.postgres_service = PostgresService(
            config=self.sql_connect['pg'],
            logger=self.logger
        )
        self.postgres_service.connect()

        # Устанавливаем статус соединения
        # self.postgres_service.fake_connect_pg()


        self.status_connect_sql_pg = self.postgres_service.status[0]
        self.status_connect_sql_pg_text = self.postgres_service.status[1]


        # Инициализируем сигналы
        self.signals.postgres_connected.emit(self.postgres_service.status[0], self.postgres_service.status[1])
        self.load_file_data = None
        self.logger_service.info("Загружена конфигурация приложения")


    # =============== Сигналы ===============
    def init_signal(self):
        """Устанавливает сигналы для приложения."""
        self.signals.postgres_connected.emit(self.postgres_service.status[0], self.postgres_service.status[1])


    def save_data(self, path: Path):
        """Сохраняет данные в JSON файл."""
        with open(path, mode="w", encoding="utf-8") as f:
            json.dump(self.config_output, f, indent=4, ensure_ascii=False)


    # =============== Подключение к базам данных ===============
    def set_connect_sql_pg(self):
        """Устанавливает подключение к PostgreSQL."""
        if self.postgres_service:
            self.status_connect_sql_pg, self.status_connect_sql_pg_text = \
                self.postgres_service.connect()

    # =============== Для тестирования ===============
    def _testing_connect_pg(self):
        """Тест подключения к PostgreSQL."""
        self.status_connect_sql_pg = True
        self.status_connect_sql_pg_text = "Успешное подключение к PostgreSQL"

        # self.status_connect_sql_pg = False
        # self.status_connect_sql_pg_text = "Ошибка подключения к PostgreSQL"

    def __del__(self):
        """Закрытие соединений при завершении работы приложения."""
        if self.postgres_service:
            self.postgres_service.close()
            self.logger_service.info("Приложение завершило работу")


class SQLWorker(QThread):
    """Рабочий поток для выполнения SQL-запроса"""
    finished = pyqtSignal(list)  # Сигнал с результатами
    error = pyqtSignal(str)      # Сигнал с ошибкой
    progress = pyqtSignal(int)   # Сигнал с прогрессом

    def __init__(self, app, script):
        super().__init__()
        self.app = app
        self.script = script
        self.sql_service = app.postgres_service

    def run(self):
        try:
            # Выполняем SQL-запрос
            status, results, error_message = self.sql_service.execute_script(script=self.script)
            if status:
                self.finished.emit(results)
            else:
                self.error.emit(error_message)
        except Exception as e:
            self.error.emit(str(e))

    def _update_progress(self, value):
        """Обновление прогресса"""
        self.progress.emit(value)


class MainWindow(UiMainWindow):
    def __init__(self, app, *args, **kwargs):
        _logo = QtGui.QIcon()
        _logo.addPixmap(QtGui.QPixmap("icon512.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        super().__init__(app=app)

        # Параметры приложения
        self.app = app
        self.logger = app.logger
        self.save_path = app.file_service.get_save_config_path()
        self.values_fields = []
        self.list_widget_fields = {}

        # Устанавливаем заголовок окна
        self.setWindowTitle(app.name)

        # Инициализируем комбобокс с конфигурациями
        self._init_combo_box_configs()

        # Загружаем страницы
        self.load_page()

        # Загружаем поля
        self.load_page_fields(config=self.app.config_fields)

        # Загружаем колонки
        self.load_columns(columns=self.app.columns_table)

        #  Подключаем сигналы
        self.app.signals.postgres_connected.connect(self._on_signal_status_connect_sql)

        # Инициализируем сигналы
        self.app.init_signal()

        # Разработка
        self._init_development()

    # =============== Инициализация и загрузка данных ===============
    def _init_development(self):
        self.combo_box_configs.setCurrentIndex(0)
        self.action_git.setVisible(False)
        self.action_load_table.setVisible(False)
        self.action_settings.setVisible(False)
        self.action_test_notification.setVisible(True)

    def _init_combo_box_configs(self):
        """Инициализирует комбобокс с конфигурациями."""
        configs = ['REST']
        for config in configs:
            self.combo_box_configs.addItem(config)

    def load_page(self):
        """Загружает страницы в toolbox."""
        if not self.app.config_pages:
            self.logger.error("Не удалось загрузить страницы!")
            self.notification.show_notification("Не удалось загрузить страницы!", "error", "Ошибка загрузки страниц")
            self.pages = []
            return

        pages_list = []
        for page in self.app.config_pages['pages']:
            pages_list.append({"page": PageWidget(name=page['name']), "title": page['title'], "fields": page['fields'], "name": page['name']})

        self.pages = pages_list
        for page in self.pages:
            self.toolBox_fields.addItem(page["page"], page["title"])
            self.toolBox_fields.setItemText(self.toolBox_fields.indexOf(page['page']), f"{page['title']} ({len(page['fields'])})")


    def load_page_fields(self, config: dict):
        """Загружает поля на страницы в соответствии с конфигурацией."""
        if not self.pages:
            self.logger.error("Не удалось загрузить страницы!")
            self.notification.show_notification("Не удалось загрузить страницы!", "error", "Ошибка загрузки страниц")
            return

        for page in self.pages:
            page_widget = page["page"]
            if page_widget.layout():
                old_layout = page_widget.layout()
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                QtWidgets.QWidget().setLayout(old_layout)

            page_layout = QtWidgets.QVBoxLayout(page_widget)
            page_layout.setContentsMargins(10, 10, 10, 10)
            page_layout.setSpacing(10)
            page_layout.setObjectName(f"page_layout_{page['name']}")

            fields = page["fields"]
            for field in fields:
                if config.get(field):
                    field_config = config[field]
                    field_type = field_config.get('type', 'text')

                    if field_type == 'text':
                        widget = TextWidget(
                            parent=page_widget,
                            app=self.app,
                            config=field_config,
                            key=field,
                            event_on_changed=self.app.config_service.set_config_output,
                            event_open_sql_script=self._event_btn_clicked_open_sql_script,
                            event_run_sql_script=self._event_btn_clicked_run_sql_script
                            )
                    elif field_type == 'select':
                        widget = SelectWidget(
                            parent=page_widget,
                            app=self.app,
                            config=field_config,
                            key=field,
                            event_on_changed=self.app.config_service.set_config_output,
                            )
                    elif field_type == 'boolean':
                        widget = CheckBoxWidget(
                            parent=page_widget,
                            app=self.app,
                            config=field_config,
                            key=field,
                            event_on_changed=self.app.config_service.set_config_output,
                            )
                    elif field_type == 'number':
                        widget = NumberWidget(
                            parent=page_widget,
                            app=self.app,
                            config=field_config,
                            key=field,
                            event_on_changed=self.app.config_service.set_config_output,
                            )
                    elif field_type == 'array':
                        widget = TagInputWidget(
                            parent=page_widget,
                            app=self.app,
                            config=field_config,
                            key=field,
                            event_on_changed=self.app.config_service.set_config_output,
                            )
                    else:
                        continue

                    self.list_widget_fields[field] = widget

                    page_layout.addWidget(widget)
                    line = QtWidgets.QFrame(page_widget)
                    line.setFrameShape(QtWidgets.QFrame.HLine)
                    line.setFrameShadow(QtWidgets.QFrame.Sunken)
                    line.setObjectName("line")
                    page_layout.addWidget(line)
            page_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

    def load_columns(self, columns):
        """Загружает колонки в таблицу."""
        if not columns:
            self.logger.error("Не удалось загрузить колонки!")
            self.notification.show_notification("Не удалось загрузить колонки!", "error", "Ошибка загрузки колонки")
            return

        self.table_fields.setColumnCount(0)
        self.table_fields.setColumnCount(len(columns))
        self.table_fields.horizontalHeader().setStretchLastSection(False)

        list_mode_resize = []
        for col, column in enumerate(columns):
            header_item = HeaderItem(column["name"], column["type"])
            self.table_fields.setHorizontalHeaderItem(col, header_item)
            width = header_item.get_column_width()
            if width > 0:
                self.table_fields.setColumnWidth(col, width)
            list_mode_resize.append(header_item.get_resize_mode())

        header = self.table_fields.horizontalHeader()
        for col, mode in enumerate(list_mode_resize):
            header.setSectionResizeMode(col, mode)

    # =============== Обработчик событий таблицы ===============
    def _editing_values_fields(self, row, key, value):
        """Обновляет значения полей в таблице."""
        self.values_fields[row][key] = value

    def _event_text_changed(self, row, key, value):
        """Обработчик изменения текстового поля."""
        self._editing_values_fields(row=row, key=key, value=value)
        self.app.config_service.set_config_output(key='fields', value=self.values_fields)

    def _event_select_сhanged(self, row, key, value):
        """Обработчик изменения поля выбора."""
        self._editing_values_fields(row=row, key=key, value=value)
        self.app.config_service.set_config_output(key='fields', value=self.values_fields)

    def _event_boolean_changed(self, row, key, value):
        """Обработчик изменения булевого поля."""
        self._editing_values_fields(row=row, key=key, value=value)
        self.app.config_service.set_config_output(key='fields', value=self.values_fields)

    def _event_number_changed(self, row, key, value):
        """Обработчик изменения числового поля."""
        self._editing_values_fields(row=row, key=key, value=value)
        self.app.config_service.set_config_output(key='fields', value=self.values_fields)

    # =============== Обработчик событий кнопок таблицы ===============
    def _event_btn_clicked_add_field_table(self, data_value: dict = None):
        """Обработчик добавления поля."""
        row = self.table_fields.rowCount()
        self.table_fields.insertRow(row)
        dict_fields = {}
        dict_fields_widget = {}
        for col, column in enumerate(self.app.columns_table):
            if column['key'] == 'action':
                widget = ActionItemTableWidget(column=column, row=row, event_on_changed=self._event_btn_clicked_delete_row)
            elif column['type'] == 'text':
                widget = TextItemTableWidget(column=column, row=row, event_on_changed=self._event_text_changed)
                dict_fields[column['key']] = ""
                dict_fields_widget[column['key']] = widget
            elif column['type'] == 'select':
                widget = SelectItemTableWidget(column=column, row=row, event_on_changed=self._event_select_сhanged)
                dict_fields[column['key']] = ""
                dict_fields_widget[column['key']] = widget
            elif column['type'] == 'number':
                widget = NumberItemTableWidget(column=column, row=row, event_on_changed=self._event_number_changed)
                dict_fields[column['key']] = ""
                dict_fields_widget[column['key']] = widget
            elif column['type'] == 'boolean':
                widget = BooleanItemTableWidget(column=column, row=row, event_on_changed=self._event_boolean_changed)
                dict_fields[column['key']] = ""
                dict_fields_widget[column['key']] = widget
            else:
                continue

            self.table_fields.setCellWidget(row, col, widget)

        self.values_fields.append(dict_fields)

        if data_value:
            for key, value in data_value.items():
                if key in dict_fields_widget:
                    dict_fields_widget[key].set_value(value)

    def _event_btn_clicked_clear_fields_table(self):
        """Очистить таблицу"""
        # Создаем диалоговое окно подтверждения
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Очистить таблицу?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        # Если пользователь нажал "Да"
        if reply == QMessageBox.Yes:
            # Очищаем таблицу
            self.table_fields.setRowCount(0)
            self.values_fields = []
            self.app.config_service.set_config_output(key='fields', value=self.values_fields)

    def _event_btn_clicked_delete_row(self, row):
        """Обработчик удаления строки."""
        self.table_fields.removeRow(row)
        self.values_fields.pop(row)
        self.app.config_service.set_config_output(key='fields', value=self.values_fields)

    # =============== Обработчик событий кнопок формы ===============
    def _event_btn_clicked_save_fields_table(self):
        """Обработчик сохранения полей."""
        default_dir = self.app.file_service.get_save_config_path() / self.app.file_service.get_file_name_config_save()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить JSON файл",
            default_dir.as_posix(),
            "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.app.save_data(path=Path(file_path))
                self.notification.show_notification(f"Файл: {file_path} сохранен!", "info", "Сохранение файла")
            except Exception as e:
                self.notification.show_notification(f"Не удалось сохранить файл: {e}", "error", "Ошибка сохранения файла")

    def _event_btn_clicked_load_fields_table(self):
        """Обработчик загрузки полей."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Сохранить JSON файл",
            "JSON Files (*.json)"
        )
        if file_path:
            with open(file_path, mode="r", encoding="utf-8") as f:
                self.app.load_file_data= json.load(f)

            self.load_field_data()

    def _event_btn_clicked_view_fields_table(self):
        """Обработчик просмотра полей."""
        if not self.app.config_output:
            self.notification.show_notification("Не удалось загрузить поля!", "error", "Ошибка загрузки полей")
            return

        content_layout = ViewJSONWidget(text=json.dumps(self.app.config_output, indent=4, ensure_ascii=False), working_dir=self.working_dir, app=self.app)

        # Создаем кнопку для копирования в буфер обмена
        copy_button = QtWidgets.QPushButton("Копировать")
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(json.dumps(self.app.config_output, indent=4, ensure_ascii=False)))

        # Добавляем кнопку в контент
        save_button = QtWidgets.QPushButton("Сохранить")
        save_button.clicked.connect(self._event_btn_clicked_save_fields_table)

        view_message_box = ContentForm(
            title="JSON Config",
            content=content_layout,
            ok_callback=None,
            custom_buttons=[
                save_button,
                copy_button,
            ],
            app=self.app
        )
        view_message_box.exec_()

    def _event_btn_clicked_open_git_form(self):
        """Обработчик git операций."""
        pass
        # git_form = GitForm(parent=self)
        # git_form.show()

    def _event_btn_clicked_settings_fields(self):
        """Обработчик настроек."""
        form_settings = SettingsForm(parent=self, app=self.app)
        form_settings.exec_()

    def _event_btn_clicked_open_connection_pg_form(self):
        """Обработчик подключения к PostgreSQL."""
        content_layout = PostgreWidget(
            working_dir=self.app.file_service.get_working_dir(),
            data_connect=self.app.config_service.get_sql_connect()['pg'],
            app=self.app)

        test_button = QtWidgets.QPushButton("Тест")
        test_button.clicked.connect(self._event_btn_clicked_test_connect)

        try:
            # Создание формы
            form = ContentForm(
                title="Настройки подключения к PostgreSQL",
            content=content_layout,
            ok_callback=lambda: self._callback_btn_ok_save_settings_pg(data=content_layout.get_settings(), form=form),
            stretch_content=True,
            custom_buttons=[
                test_button,
            ],
            app=self.app
            )
            form.exec_()
        except Exception as e:
            self.logger.error(f"Ошибка при создании формы: {e}")
            self.notification.show_notification(f"Ошибка при создании формы: {e}", "error", "Ошибка создания формы")

    def _event_btn_clicked_test_connect(self):
        """Тест подключения к PostgreSQL."""
        self.app.postgres_service.connect()
        status, message = self.app.postgres_service.status
        self.app.signals.postgres_connection_changed.emit(status, message)

        if status:
            self.notification.show_notification("Подключение к PostgreSQL установлено!", "info")
        else:
            self.notification.show_notification(f"Не удалось установить подключение к PostgreSQL! {message}", "error", "Ошибка подключения к PostgreSQL")

    def _event_btn_clicked_open_sql_script(self, key: str, value: str):
        """Обработчик открытия скрипта SQL."""
        content_layout = SQLViewerScript(
            parent=self,
            app=self.app,
            event_render_sql_script=self._event_btn_clicked_render_sql_script,
            event_run_sql_script=self._event_btn_clicked_run_sql_script
            )
        content_layout.set_text(text=self.app.sql_scripts[key], key=key, value=value)

        try:
            form = ContentForm(
                title="Скрипт SQL",
                content=content_layout,
                app=self.app,
                ok_callback=lambda: self._event_btn_clicked_save_sql_script(key=key, content=content_layout.get_text(), form=form),
            )
            form.exec_()
        except Exception as e:
            self.logger.error(f"Ошибка при создании формы: {e}")
            self.notification.show_notification(f"Ошибка при создании формы: {e}", "error", "Ошибка создания формы")

    def _event_btn_clicked_render_sql_script(self, key: str, value: str, sql_script = None):
        """Обработчик рендеринга скрипта SQL."""
        if sql_script is None:
            sql_script = self.app.sql_scripts[key]

        try:
            sql_script = jinja2.Template(sql_script).render(value=value)
        except Exception as e:
            return f"Не удалось рендерить скрипт SQL: {e}"

        return sql_script

    def _event_btn_clicked_save_sql_script(self, key: str, content: str, form: ContentForm):
        """Обработчик сохранения скрипта SQL."""
        self.app.config_service.set_sql_scripts(key=key, value=content)
        self.app.config_service.save_sql_scripts()
        form.close()

    def _event_btn_clicked_run_sql_script(self, key: str = None, value: str = None, sql_script = None):
        """Обработчик запуска скрипта SQL."""
        if not self.app.postgres_service or not self.app.postgres_service.is_connected:
            self.logger.error("Попытка выполнить SQL скрипт без подключения к PostgreSQL")
            self.notification.show_notification("Не удалось установить подключение к PostgreSQL!", "error", "Ошибка подключения к PostgreSQL")
            return

        # Создаем и показываем виджет загрузки
        self.loading_widget = LoadingWidget(self)
        self.loading_widget.show_loading("Выполнение SQL скрипта...")
        # Подключаем сигнал отмены
        self.loading_widget.cancelled.connect(self._cancel_sql_execution)

        try:
            # Получаем SQL-скрипт
            if sql_script is None:
                script = self.app.sql_scripts.get(key, "")
                if not script:
                    raise ValueError(f"SQL скрипт с ключом {key} не найден")
            else:
                script = sql_script

            # Создаем и настраиваем рабочий поток
            self.sql_worker = SQLWorker(app=self.app, script=script)
            self.sql_worker.finished.connect(self._on_sql_finished)
            self.sql_worker.error.connect(self._on_sql_error)
            self.sql_worker.progress.connect(self._on_sql_progress)
            self.sql_worker.start()

        except Exception as e:
            error_msg = f"Ошибка при выполнении SQL скрипта: {e}"
            self.logger.error(error_msg)
            self.notification.show_notification(error_msg, "error")
            self.loading_widget.hide_loading()

    def _on_sql_finished(self, results):
        """Обработка успешного завершения выполнения SQL-запроса"""
        try:
            self.logger.info("SQL скрипт выполнен успешно")
            self.loading_widget.update_status("Обработка результатов...")
            total_rows = len(results)

            # Очищаем таблицу перед загрузкой новых данных
            self.table_fields.setRowCount(0)
            self.values_fields = []

            # Загружаем данные с отображением прогресса
            for i, values in enumerate(results):
                progress = int((i + 1) / total_rows * 100)
                keys = self.app.config_service.get_config_tables_keys()
                fields = dict(zip(keys, values))
                self._event_btn_clicked_add_field_table(data_value=fields)
                self.loading_widget.update_status(f"Обработка результатов... {progress}%", progress)

            # Завершаем загрузку
            self.loading_widget.hide_loading()
            self.notification.show_notification(
                f"Загрузка данных завершена! Данных в таблице: {total_rows} строк",
                "info"
            )

        except Exception as e:
            error_msg = f"Ошибка при обработке результатов: {e}"
            self.logger.error(error_msg)
            self.notification.show_notification(error_msg, "error")
            self.loading_widget.hide_loading()

    def _on_sql_error(self, error_message):
        """Обработка ошибки выполнения SQL-запроса"""
        self.logger.error(f"Ошибка выполнения SQL скрипта: {error_message}")
        self.notification.show_notification(
            f"Ошибка выполнения SQL скрипта: {error_message}",
            "error"
        )
        self.loading_widget.hide_loading()

    def _on_sql_progress(self, value):
        """Обработка обновления прогресса"""
        self.loading_widget.update_status(f"Выполнение SQL скрипта... {value}%", value)

    def _cancel_sql_execution(self):
        """Обработка отмены выполнения SQL-запроса"""
        if hasattr(self, 'sql_worker') and self.sql_worker.isRunning():
            self.sql_worker.terminate()  # Останавливаем поток
            self.sql_worker.wait()      # Ждем завершения потока
        self.loading_widget.hide_loading()
        self.notification.show_notification(
            "Выполнение SQL скрипта отменено пользователем",
            "warning"
        )

    # =============== Обработчик сигналов ===============
    def _on_signal_status_connect_sql(self, status: bool, message: str):
        """Обработчик сигнала статуса соединения."""
        if status:
            self.action_connect_pg.set_status_connect_on()
        else:
            self.action_connect_pg.set_status_connect_off()

    def _callback_btn_ok_save_settings_pg(self, data: dict, form: ContentForm):
        """Обработчик сохранения настроек подключения к PostgreSQL."""
        self.app.config_service.set_sql_connect(key='pg', value=data)
        self.app.config_service.save_sql_connect()
        form.close()

    # =============== Обработчик тестовой загрузки ===============
    def _update_progress(self):
        """Обновление прогресса загрузки"""
        self.progress_value += 1
        if self.progress_value <= 100:
            self.loading_widget.update_status(f"Загрузка тестовых данных... {self.progress_value}%", self.progress_value)
        else:
            self._finish_loading()

    def _cancel_loading(self):
        """Обработка отмены загрузки"""
        self.progress_timer.stop()
        self.loading_widget.hide_loading()
        # Показываем уведомление об отмене
        self.notification.show_notification(
            "Отменено",
            "Загрузка данных отменена пользователем",
            "warning"
        )

    def _finish_loading(self):
        """Завершение загрузки"""
        self.progress_timer.stop()
        self.loading_widget.hide_loading()
        # Показываем уведомление об успешной загрузке
        self.notification.show_notification(
            message="Тестовые данные загружены",
            status="info",
            title="Успешно"
        )


    # =============== Вспомогательные методы ===============
    def load_field_data(self):
        """Загружает данные из файла JSON."""
        for key, value in self.app.load_file_data.items():
            if key == 'fields':
                self.table_fields.setRowCount(0)
                for field in value:
                    self._event_btn_clicked_add_field_table(data_value=field)
            else:
                if key in self.list_widget_fields:
                    self.list_widget_fields[key].set_value(value)


def main():
    """Точка входа в приложение."""
    try:
        # Создаем приложение
        app = Application(sys.argv)

        # Получаем имя пользователя
        user_name = getpass.getuser()

        # Создаем и показываем splash screen
        splash = SplashScreen(user_name)
        splash.show()

        # Центрируем splash screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - splash.width()) // 2
        y = (screen.height() - splash.height()) // 2
        splash.move(x, y)

        # Создаем главное окно
        main_window = MainWindow(app=app)

        # Создаем таймер для минимального времени показа splash screen
        min_display_timer = QTimer()
        min_display_timer.setSingleShot(True)
        min_display_timer.start(2000)  # Минимум 2 секунды

        # Создаем таймер для проверки готовности приложения
        check_ready_timer = QTimer()
        check_ready_timer.timeout.connect(lambda: _check_app_ready(splash, main_window, min_display_timer, check_ready_timer, app))
        check_ready_timer.start(100)  # Проверяем каждые 100мс

        # Запускаем приложение
        sys.exit(app.exec_())

    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        sys.exit(1)


def _check_app_ready(splash, main_window, min_display_timer, check_ready_timer, app):
    """Проверяет готовность приложения к показу."""
    # Проверяем, прошло ли минимальное время показа
    if not min_display_timer.isActive():
        # Проверяем, загружены ли все необходимые данные
        if (app.config_fields and
            app.config_pages and
            app.config_output):

            # Останавливаем таймер проверки
            check_ready_timer.stop()

            # Закрываем splash screen
            splash.close()

            # Показываем главное окно
            main_window.show()


import resource # type: ignore

if __name__ == "__main__":
    main()