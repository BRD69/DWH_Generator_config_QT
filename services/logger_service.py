import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

class LoggerService:
    """Сервис для управления логированием приложения."""

    def __init__(self, name: str, log_dir: Path):
        """
        Инициализация сервиса логирования.

        Args:
            name: Имя логгера
            log_dir: Директория для хранения логов
        """
        self.name = name
        self.log_dir = log_dir
        self.logger: Optional[logging.Logger] = None
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Настройка логгера с файловым и консольным выводом."""
        try:
            # Создаем директорию для логов если её нет
            if not self.log_dir.exists():
                self.log_dir.mkdir(parents=True, exist_ok=True)

            # Создаем форматтер для логов
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # Настраиваем файловый обработчик с ротацией
            log_file = self.log_dir / f"{self.name}.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)

            # Настраиваем консольный обработчик
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)

            # Получаем логгер и настраиваем его
            self.logger = logging.getLogger(self.name)
            self.logger.setLevel(logging.DEBUG)

            # Очищаем существующие обработчики
            self.logger.handlers.clear()

            # Добавляем обработчики
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        except Exception as e:
            print(f"Ошибка при инициализации логгера: {e}")
            raise

    def get_logger(self) -> logging.Logger:
        """
        Возвращает настроенный логгер.

        Returns:
            logging.Logger: Настроенный логгер
        """
        if not self.logger:
            raise RuntimeError("Логгер не был инициализирован")
        return self.logger

    def debug(self, message: str) -> None:
        """Логирование отладочного сообщения."""
        if self.logger:
            self.logger.debug(message)

    def info(self, message: str) -> None:
        """Логирование информационного сообщения."""
        if self.logger:
            self.logger.info(message)

    def warning(self, message: str) -> None:
        """Логирование предупреждения."""
        if self.logger:
            self.logger.warning(message)

    def error(self, message: str) -> None:
        """Логирование ошибки."""
        if self.logger:
            self.logger.error(message)

    def critical(self, message: str) -> None:
        """Логирование критической ошибки."""
        if self.logger:
            self.logger.critical(message)

    def exception(self, message: str) -> None:
        """Логирование исключения с трейсбеком."""
        if self.logger:
            self.logger.exception(message)

    def set_level(self, level: int) -> None:
        """
        Установка уровня логирования.

        Args:
            level: Уровень логирования (logging.DEBUG, logging.INFO, etc.)
        """
        if self.logger:
            self.logger.setLevel(level)

    def add_file_handler(self, filename: str, level: int = logging.DEBUG) -> None:
        """
        Добавление дополнительного файлового обработчика.

        Args:
            filename: Имя файла для логирования
            level: Уровень логирования для этого обработчика
        """
        if self.logger:
            handler = RotatingFileHandler(
                self.log_dir / filename,
                maxBytes=10*1024*1024,
                backupCount=5,
                encoding='utf-8'
            )
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            handler.setLevel(level)
            self.logger.addHandler(handler)

    def remove_all_handlers(self) -> None:
        """Удаление всех обработчиков логгера."""
        if self.logger:
            self.logger.handlers.clear()

    def __del__(self) -> None:
        """Очистка ресурсов при удалении сервиса."""
        if self.logger:
            self.remove_all_handlers()