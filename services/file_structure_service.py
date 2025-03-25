import json
from pathlib import Path
from typing import Dict, Any, Optional
import shutil
from services.logger_service import LoggerService

class FileStructureService:
    """Сервис для управления файловой структурой приложения."""

    def __init__(self, working_dir: Path, logger_service: LoggerService):
        """
        Инициализация сервиса файловой структуры.

        Args:
            working_dir: Рабочая директория приложения
            logger_service: Сервис логирования
        """
        self.working_dir = working_dir
        self.logger_service = logger_service

        # Определение структуры директорий
        self.config_dir = working_dir / "config"
        self.template_dir = working_dir / "template"
        self.save_config_dir = working_dir / "save_config"
        self.logs_dir = working_dir / "logs"

        self.file_name_config_save = "config_save.json"

        # Определение путей к файлам конфигурации
        self.config_fields_path = self.config_dir / "config_fields.json"
        self.config_pages_path = self.config_dir / "config_pages.json"
        self.config_output_path = self.save_config_dir / self.file_name_config_save
        self.sql_connect_path = self.config_dir / "sql_connect.json"
        self.sql_scripts_path = self.config_dir / "sql_scripts.json"

        self.template_fields_path = self.template_dir / "config_fields.json"

        self.init_config()


    def init_config(self) -> None:
        """Инициализирует базовую структуру директорий и файлов."""
        try:
            # Создаем необходимые директории
            self._create_directories()

            # Создаем файлы конфигурации
            self._create_config_files()

            self.logger_service.info("Структура приложения инициализирована успешно")
        except Exception as e:
            self.logger_service.error(f"Ошибка при инициализации структуры: {e}")
            raise

    def _create_directories(self) -> None:
        """Создает необходимые директории."""
        directories = [
            (self.config_dir, "конфигурации"),
            (self.template_dir, "шаблонов"),
            (self.save_config_dir, "сохранения конфигурации"),
            (self.logs_dir, "логов")
        ]

        for directory, description in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                self.logger_service.info(f"Создана директория {description}: {directory}")

    def _create_config_files(self) -> None:
        """Создает файлы конфигурации с значениями по умолчанию."""
        # Конфигурация подключения к БД
        if not self.sql_connect_path.exists():
            default_connect_sql = {
                "pg": {
                    "host": "localhost",
                    "port": "5432",
                    "dbname": "postgres",
                    "user": "postgres",
                    "password": ""
                }
            }
            self.save_json(self.sql_connect_path, default_connect_sql)
            self.logger_service.info(f"Создан файл настроек подключения: {self.sql_connect_path}")

        # SQL скрипты
        if not self.sql_scripts_path.exists():
            default_sql_scripts = {
                "object_name": "",
                "endpoint": ""
            }
            self.save_json(self.sql_scripts_path, default_sql_scripts)
            self.logger_service.info(f"Создан файл SQL скриптов: {self.sql_scripts_path}")

        # Шаблон полей
        if not self.template_fields_path.exists():
            default_template = {
                "fields": {
                    "values": [
                        {"key": "name", "name": "Название", "type": "text", "value": ""},
                        {"key": "description", "name": "Описание", "type": "text", "value": ""},
                        {"key": "type", "name": "Тип", "type": "select", "value": "", "values": ["table", "view"]},
                        {"key": "schema", "name": "Схема", "type": "text", "value": ""},
                        {"key": "active", "name": "Активность", "type": "boolean", "value": True}
                    ]
                }
            }
            self.save_json(self.template_fields_path, default_template)
            self.logger_service.info(f"Создан файл шаблона полей: {self.template_fields_path}")

        # Создаем пустые файлы конфигурации
        for file_path in [self.config_fields_path, self.config_pages_path]:
            if not file_path.exists():
                file_path.touch(exist_ok=True)
                self.logger_service.info(f"Создан файл конфигурации: {file_path}")

    def load_json(self, file_path: Path) -> Dict[str, Any]:
        """
        Загружает данные из JSON файла.

        Args:
            file_path: Путь к файлу

        Returns:
            Dict[str, Any]: Загруженные данные
        """
        try:
            if not file_path.exists():
                return {}

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger_service.error(f"Ошибка при загрузке файла {file_path}: {e}")
            return {}

    def save_json(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """
        Сохраняет данные в JSON файл.

        Args:
            file_path: Путь к файлу
            data: Данные для сохранения

        Returns:
            bool: Успешность операции
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger_service.error(f"Ошибка при сохранении файла {file_path}: {e}")
            return False

    def copy_template_to_config(self) -> bool:
        """
        Копирует шаблон в файл конфигурации.

        Returns:
            bool: Успешность операции
        """
        try:
            if not self.template_fields_path.exists():
                self.logger_service.error("Файл шаблона не найден")
                return False

            shutil.copy2(self.template_fields_path, self.config_fields_path)
            self.logger_service.info("Шаблон скопирован в конфигурацию")
            return True
        except Exception as e:
            self.logger_service.error(f"Ошибка при копировании шаблона: {e}")
            return False

    # =============== Получение путей директорий ===============
    def get_working_dir(self) -> Path:
        """
        Возвращает путь для сохранения конфигурации.
        """
        return self.working_dir

    def get_save_path(self, filename: str) -> Path:
        """
        Возвращает путь для сохранения конфигурации.

        Args:
            filename: Имя файла

        Returns:
            Path: Полный путь для сохранения
        """
        return self.save_config_dir / filename

    def get_log_path(self) -> Path:
        """
        Возвращает путь для сохранения логов.

        Returns:
            Path: Полный путь для сохранения логов
        """
        return self.logs_dir

    def get_config_path(self) -> Path:
        """
        Возвращает путь для сохранения конфигурации.

        Returns:
            Path: Полный путь для сохранения конфигурации
        """
        return self.config_dir

    def get_template_path(self) -> Path:
        """
        Возвращает путь для сохранения конфигурации.

        Returns:
            Path: Полный путь для сохранения конфигурации
        """
        return self.template_dir

    def get_save_config_path(self) -> Path:
        """
        Возвращает путь для сохранения конфигурации.
        """
        return self.save_config_dir

    # =============== Получение путей файлов ===============
    def get_config_fields_file(self) -> Path:
        """
        Возвращает путь для сохранения конфигурации.
        """
        return self.config_fields_path

    def get_config_pages_file(self) -> Path:
        """
        Возвращает путь для сохранения конфигурации.
        """
        return self.config_pages_path

    def get_config_output_file(self) -> Path:
        """
        Возвращает путь для сохранения конфигурации.
        """
        return self.config_output_path

    def get_sql_connect_file(self) -> Path:
        """
        Возвращает путь для сохранения конфигурации.
        """
        return self.sql_connect_path

    def get_sql_scripts_file(self) -> Path:
        """
        Возвращает путь для сохранения конфигурации.
        """
        return self.sql_scripts_path

    # =============== Получение имени файла конфигурации ===============
    def get_file_name_config_save(self) -> str:
        """
        Возвращает имя файла конфигурации.
        """
        return self.file_name_config_save

    def set_file_name_config_save(self, file_name: str) -> None:
        """
        Устанавливает имя файла конфигурации.
        """
        if file_name:
            self.file_name_config_save = f"{file_name}.json"
