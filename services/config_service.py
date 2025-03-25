import json
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from services.crypto_text_service import CryptoTextService
from services.file_structure_service import FileStructureService
from services.logger_service import LoggerService


class ConfigService:
    """Сервис для управления конфигурацией приложения."""

    def __init__(self,
                 working_dir: Path,
                 logger_service: LoggerService,
                 file_service: FileStructureService = None,
                 crypto_service: CryptoTextService = None):
        """
        Инициализация сервиса конфигурации.

        Args:
            working_dir: Рабочая директория приложения
            logger_service: Сервис логирования
        """
        self.config_fields_data = {}
        self.config_pages_data = {}
        self.config_output_data = {}
        self.sql_connect_data = {}
        self.sql_scripts_data = {}

        self.logger_service = logger_service
        self.file_service = file_service
        self.crypto_service = crypto_service

        self.working_dir = working_dir
        self.config_path = file_service.get_config_path()
        self.template_path = file_service.get_template_path()

        self.config_fields_file = file_service.get_config_fields_file()
        self.config_pages_file = file_service.get_config_pages_file()
        self.config_output_file = file_service.get_config_output_file()
        self.sql_connect_file = file_service.get_sql_connect_file()
        self.sql_scripts_file = file_service.get_sql_scripts_file()

        self.init_config()


     # =============== Инициализация ===============
    def init_config(self) -> None:
        """
        Инициализирует конфигурацию приложения.
        """
        self.load_config_fields()
        self.load_config_pages()
        self.load_config_output()
        self.load_sql_connect()
        self.load_sql_scripts()


    # =============== Поля ===============
    def load_config_fields(self) -> None:
        """
        Загружает конфигурацию из файла.

        """
        if not self.config_fields_file.exists():
            self.logger_service.error(f"Файл конфигурации не найден: {self.config_fields_file}")
            self.set_config_fields(data={})
        else:
            with open(file=self.config_fields_file, mode='r', encoding='utf-8') as file:
                self.set_config_fields(data=json.load(file))

    def save_config_fields(self) -> None:
        """
        Сохраняет конфигурацию в файл.
        """
        try:
            with open(self.config_fields_file, 'w', encoding='utf-8') as file:
                json.dump(self.config_fields_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger_service.error(f"Ошибка при сохранении конфигурации: {e}")

    def set_config_fields(self, key: str = None, value: Any = None, data: Dict[str, Any] = None) -> None:
        """
        Устанавливает значение в конфигурацию.
        """
        if data:
            self.config_fields_data = data
        else:
            self.config_fields_data[key] = value

    def get_config_fields(self, key: str = None) -> Any:
        """
        Возвращает значение из конфигурации.
        """
        if key:
            return self.config_fields_data[key]
        else:
            return self.config_fields_data

    # =============== Страницы ===============
    def load_config_pages(self) -> None:
        """
        Загружает конфигурацию из файла.
        """

        if not self.config_pages_file.exists():
            self.logger_service.error(f"Файл конфигурации не найден: {self.config_pages_file}")
            self.set_config_pages(data={})
        else:
            with open(self.config_pages_file, 'r', encoding='utf-8') as file:
                self.set_config_pages(data=json.load(file))

    def save_config_pages(self) -> None:
        """
        Сохраняет конфигурацию в файл.
        """
        try:
            with open(self.config_pages_file, 'w', encoding='utf-8') as file:
                json.dump(self.config_pages_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger_service.error(f"Ошибка при сохранении конфигурации: {e}")

    def set_config_pages(self, key: str = None, value: Any = None, data: Dict[str, Any] = None) -> None:
        """
        Устанавливает значение в конфигурацию.
        """
        if data:
            self.config_pages_data = data
        else:
            self.config_pages_data[key] = value

    def get_config_pages(self, key: str = None) -> Any:
        """
        Возвращает значение из конфигурации.
        """
        if key:
            return self.config_pages_data[key]
        else:
            return self.config_pages_data

    # =============== SQL подключение ===============
    def load_sql_connect(self):
        """
        Загружает конфигурацию из файла.
        """
        sql_connect_file = self.file_service.get_sql_connect_file()

        if not sql_connect_file.exists():
            self.logger_service.error(f"Файл конфигурации не найден: {sql_connect_file}")
            self.set_sql_connect(data={})
        else:
            with open(sql_connect_file, 'r', encoding='utf-8') as file:
                data_file = json.load(file)
                if self.crypto_service is not None:
                    for key, value in data_file.items():
                        if value.get('password'):
                            value['password'] = self.crypto_service.get_crypto_pass(value['password'])
                        self.set_sql_connect(key=key, value=value)
                else:
                    self.set_sql_connect(data=data_file)

    def save_sql_connect(self) -> None:
        """
        Сохраняет конфигурацию в файл.
        """
        try:
            data_file = self.sql_connect_data.copy()
            if self.crypto_service is not None:
                for key, value in data_file.items():
                    if value.get('password'):
                        data_file[key]['password'] = self.crypto_service.set_crypto_pass(value['password'])

            with open(self.sql_connect_file, 'w', encoding='utf-8') as file:
                json.dump(data_file, file, ensure_ascii=False, indent=4)
            self.load_sql_connect()

        except Exception as e:
            self.logger_service.error(f"Ошибка при сохранении конфигурации: {e}")

    def set_sql_connect(self, key: str = None, value: Any = None, data: Dict[str, Any] = None) -> None:
        """
        Устанавливает значение в конфигурацию.
        """
        if data:
            self.sql_connect_data = data
        else:
            self.sql_connect_data[key] = value

    def get_sql_connect(self, key: str = None) -> Any:
        """
        Возвращает значение из конфигурации.
        """
        if key:
            return self.sql_connect_data[key]
        else:
            return self.sql_connect_data

    # =============== SQL скрипты ===============
    def load_sql_scripts(self) -> None:
        """
        Загружает конфигурацию из файла.
        """
        if not self.sql_scripts_file.exists():
            self.logger_service.error(f"Файл конфигурации не найден: {self.sql_scripts_file}")
            self.set_sql_scripts(data={})
        else:
            with open(self.sql_scripts_file, 'r', encoding='utf-8') as file:
                self.set_sql_scripts(data=json.load(file))

    def save_sql_scripts(self) -> None:
        """
        Сохраняет конфигурацию в файл.
        """
        try:
            with open(self.sql_scripts_file, 'w', encoding='utf-8') as file:
                json.dump(self.sql_scripts_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger_service.error(f"Ошибка при сохранении конфигурации: {e}")

    def set_sql_scripts(self, key: str = None, value: str = None, data: Dict[str, Any] = None   ) -> None:
        """
        Устанавливает значение в конфигурацию.
        """
        if data:
            self.sql_scripts_data = data
        else:
            self.sql_scripts_data[key] = value

    def get_sql_scripts(self, key: str = None) -> Any:
        """
        Возвращает значение из конфигурации.
        """
        if key:
            return self.sql_scripts_data[key]
        else:
            return self.sql_scripts_data

    # =============== Вывод ===============
    def load_config_output(self) -> None:
        """
        Загружает конфигурацию из файла.
        """
        if not self.config_output_file.exists():
            self.logger_service.error(f"Файл конфигурации не найден: {self.config_output_file}")
            self.set_config_output(data={})
        else:
            with open(self.config_output_file, 'r', encoding='utf-8') as file:
                self.set_config_output(data=json.load(file))

    def save_config_output(self) -> None:
        """
        Сохраняет конфигурацию в файл.
        """
        try:
            with open(self.config_output_file, 'w', encoding='utf-8') as file:
                json.dump(self.config_output_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger_service.error(f"Ошибка при сохранении конфигурации: {e}")


    def set_config_output(self, key: str = None, value: Any = None, data: Dict[str, Any] = None) -> None:
        """
        Устанавливает значение в конфигурацию.
        """
        if data:
            self.config_output_data = data
        else:
            self.config_output_data[key] = value

    def get_config_output(self, key: str = None) -> Any:
        """
        Возвращает значение из конфигурации.
        """
        if key:
            return self.config_output_data[key]
        else:
            return self.config_output_data

    # =============== Колонки ===============
    def load_columns_table(self) -> Tuple[dict, dict]:
        """
        Загружает конфигурацию из файла.
        """
        columns_table = []
        for value in self.config_fields_data.values():
            if value['type'] == 'table':
                columns_table.extend(value['values'])
        columns_table.append({"key": "action", "name": "", "type": "action", "value": ""})
        return tuple(columns_table)

    def load_config_output(self) -> Dict[str, Any]:
        output_data = {}
        config_fields = self.load_config_fields()
        if config_fields:
            for key, value in config_fields.items():
                if value['type'] == 'text':
                    output_data[key] = ''
                elif value['type'] == 'select':
                    output_data[key] = ''
                elif value['type'] == 'number':
                    output_data[key] = 0
                elif value['type'] == 'boolean':
                    output_data[key] = False
                elif value['type'] == 'array':
                    output_data[key] = ''
                elif value['type'] == 'table':
                    output_data[key] = []
        return output_data
