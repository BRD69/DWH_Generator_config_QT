import psycopg2
from typing import Dict, Any, Optional, Tuple
import logging
import jinja2

class PostgresService:
    """Сервис для работы с PostgreSQL."""

    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Инициализация сервиса PostgreSQL.

        Args:
            config: Конфигурация подключения к БД
            logger: Логгер для записи событий
        """
        self.config = config
        self.logger = logger
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.cursor = None
        self._status: Tuple[bool, str] = (False, "Не подключено")
        self._is_connected = False

    @property
    def is_connected(self) -> bool:
        """Возвращает статус подключения."""
        return self._is_connected

    @property
    def status(self) -> Tuple[bool, str]:
        """Возвращает текущий статус соединения."""
        return self._status

    def set_config(self, config: Dict[str, Any]) -> None:
        """Устанавливает конфигурацию подключения."""
        self.config = config

    def connect(self) -> Tuple[bool, str]:
        """
        Устанавливает соединение с PostgreSQL.

        Returns:
            Tuple[bool, str]: (успех подключения, текст статуса)
        """
        try:
            self.connection = psycopg2.connect(**self.config)
            self.cursor = self.connection.cursor()
            self._status = (True, "Успешное подключение к PostgreSQL")
            self._is_connected = True
            self.logger.info("Установлено подключение к PostgreSQL")
            return self._status
        except Exception as e:
            error_msg = f"Ошибка подключения к PostgreSQL: {e}"
            self._status = (False, error_msg)
            self._is_connected = False
            self.logger.error(error_msg)
            return self._status

    def execute_query(self, query: str) -> Tuple[bool, Any, str]:
        """
        Выполняет SQL запрос.

        Args:
            query: SQL запрос для выполнения

        Returns:
            Tuple[bool, Any, str]: (успех выполнения, результат, сообщение об ошибке)
        """
        if not self.is_connected:
            return False, None, "Нет активного соединения с базой данных"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            self.connection.commit()
            cursor.close()
            return True, result, ""
        except Exception as e:
            error_msg = f"Ошибка выполнения запроса: {e}"
            self.logger.error(error_msg)
            if self.connection:
                self.connection.rollback()
            return False, None, error_msg

    def execute_script(self, script: str, params: Dict[str, Any] = None) -> Tuple[bool, Any, str]:
        """
        Выполняет SQL скрипт с поддержкой шаблонизации.

        Args:
            script: SQL скрипт для выполнения
            params: Параметры для шаблонизации

        Returns:
            Tuple[bool, Any, str]: (успех выполнения, результат, сообщение об ошибке)
        """
        try:
            # Рендеринг шаблона если есть параметры
            if params:
                template = jinja2.Template(script)
                script = template.render(**params)
                self.logger.debug(f"SQL скрипт после рендеринга: {script}")

            return self.execute_query(script)
        except Exception as e:
            error_msg = f"Ошибка при подготовке или выполнении скрипта: {e}"
            self.logger.error(error_msg)
            return False, None, error_msg

    def fake_connect_pg(self) -> Tuple[bool, str]:
        """Тестирование соединения с базой данных."""
        self._status = (True, "Тестовое подключение к PostgreSQL")
        return self._status

    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            try:
                self.connection.close()
                self._status = (False, "Соединение закрыто")
                self._is_connected = False
                self.logger.info("Соединение с PostgreSQL закрыто")
            except Exception as e:
                self.logger.error(f"Ошибка при закрытии соединения: {e}")
            finally:
                self.connection = None

    def __del__(self):
        """Автоматическое закрытие соединения при удалении объекта."""
        self.close()