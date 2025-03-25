from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QWidget, QToolBox, QPushButton, QSpacerItem,
                             QSizePolicy)
from ui.widgets.SQLClickHouseWidget import ClickHouseWidget
from ui.widgets.SQLPostgreWidget import PostgreWidget


class SettingsForm(QDialog):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.working_dir = self.app.working_dir

        self.setWindowTitle("Настройки")
        self._setup_ui()
        self._load_styles()


    def _setup_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setObjectName("main_layout")
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Создаем QToolBox
        self.tool_box = QToolBox()
        self.tool_box.setObjectName("toolBox_settings")

        # Создаем страницы
        self.general_page = QWidget()
        self.general_page.setObjectName("general_page")
        self.general_page_layout = QVBoxLayout()
        self.general_page_layout.setContentsMargins(0, 0, 0, 0)
        self.general_page.setLayout(self.general_page_layout)

        self.postgres_page = QWidget()
        self.postgres_page.setObjectName("postgres_page")
        self.postgres_page_layout = QVBoxLayout()
        self.postgres_page_layout.setContentsMargins(0, 0, 0, 0)
        self.postgres_page.setLayout(self.postgres_page_layout)

        self.json_page = QWidget()
        self.json_page.setObjectName("json_page")
        self.json_page_layout = QVBoxLayout()
        self.json_page_layout.setContentsMargins(0, 0, 0, 0)
        self.json_page.setLayout(self.json_page_layout)

        # Добавляем страницы в QToolBox
        self.tool_box.addItem(self.general_page, "Общие")
        self.tool_box.addItem(self.postgres_page, "PostgreSQL")
        self.tool_box.addItem(self.json_page, "JSON Config")

        # Добавляем QToolBox в основной layout
        main_layout.addWidget(self.tool_box)

        # Создаем layout для кнопок
        button_layout = QHBoxLayout()

        # Добавляем растягивающийся спейсер
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Создаем кнопки
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        # Добавляем кнопки в layout
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        # Добавляем layout с кнопками в основной layout
        main_layout.addLayout(button_layout)

        # Устанавливаем layout для формы
        self.setLayout(main_layout)

        # Устанавливаем размеры
        self.resize(800, 600)

        # Добавляем виджеты на страницы
        self._add_widgets_to_pages()



    def _load_styles(self):
        """Загрузка стилей из файла QSS"""
        with open(self.working_dir / "resources" / "styles" / "SettingsForm.qss", "r") as f_settings_form:
            self.stylesheet = f_settings_form.read()

        self.setStyleSheet(self.stylesheet)

    def exec_(self):
        """Переопределяем метод exec_ для модального окна"""
        self.resize(800, 600)
        return super().exec_()

    def _add_widgets_to_pages(self):
        """Добавление виджетов на страницы"""
        # Общие настройки
        self._add_general_widgets()

        # Настройки PostgreSQL
        self._add_postgres_widgets()

        # Настройки JSON
        self._add_json_widgets()

    def _add_general_widgets(self):
        """Добавление виджетов на страницу общих настроек"""
        pass

    def _add_postgres_widgets(self):
        """Добавление виджетов на страницу настроек PostgreSQL"""
        postgre_widget = PostgreWidget(
            parent=self.postgres_page,
            working_dir=self.working_dir,
            app=self.app,
            data_connect=self.app.config_service.get_sql_connect('pg')
        )
        self.postgres_page_layout.addWidget(postgre_widget)
        self.postgres_page_layout.addItem(QSpacerItem(20, 20, vPolicy=QSizePolicy.Expanding))

    def _add_json_widgets(self):
        """Добавление виджетов на страницу настроек JSON"""
        pass
