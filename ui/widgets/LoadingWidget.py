from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QProgressBar, QFrame)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPen

class LinearProgress(QWidget):
    """Виджет для отображения линейного индикатора загрузки"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 6)  # Ширина 200px, высота 6px
        self.progress_value = 0

    def set_progress(self, value):
        """Установка значения прогресса"""
        self.progress_value = value
        self.update()

    def paintEvent(self, event):
        """Отрисовка линейного индикатора"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Получаем размеры виджета
        rect = self.rect()
        width = rect.width()
        height = rect.height()

        # Рисуем фон
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#e9ecef"))
        painter.drawRoundedRect(0, 0, width, height, height/2, height/2)

        # Рисуем прогресс
        progress_width = int(width * self.progress_value / 100)
        painter.setBrush(QColor("#007bff"))
        painter.drawRoundedRect(0, 0, progress_width, height, height/2, height/2)

class LoadingWidget(QWidget):
    """Виджет для отображения процесса загрузки"""

    # Добавляем сигнал для отмены
    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

        # Анимация появления/исчезновения
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.setDuration(200)

        # Изначально скрыт
        self.hide()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Устанавливаем фиксированный размер виджета
        self.setFixedSize(300, 200)

        # Основной контейнер
        self.container = QFrame(self)
        self.container.setObjectName("loadingContainer")
        self.container.setFixedSize(280, 180)
        self.container.setStyleSheet("""
            QFrame#loadingContainer {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)

        # Линейный индикатор загрузки
        self.progress = LinearProgress(self)
        container_layout.addWidget(self.progress, alignment=Qt.AlignCenter)

        # Текст статуса
        self.status_label = QLabel(self)
        self.status_label.setWordWrap(True)
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #333333;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(30)
        self.status_label.setMaximumHeight(40)
        container_layout.addWidget(self.status_label)

        # Кнопка отмены
        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setFont(QFont("Segoe UI", 9))
        self.cancel_button.setFixedWidth(120)
        self.cancel_button.setFixedHeight(30)
        self.cancel_button.setStyleSheet("""
            QPushButton#cancelButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px 15px;
                color: #333333;
            }
            QPushButton#cancelButton:hover {
                background-color: #e9ecef;
            }
            QPushButton#cancelButton:pressed {
                background-color: #dee2e6;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel_loading)
        container_layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        layout.addWidget(self.container)

    def show_loading(self, message: str = "Загрузка..."):
        """Показать виджет загрузки

        Args:
            message (str): Текст статуса загрузки
        """
        self.status_label.setText(message)
        self.progress.set_progress(0)

        # Центрируем виджет на родительском окне
        if self.parent():
            parent_rect = self.parent().rect()
            self.move(
                parent_rect.width() // 2 - self.width() // 2,
                parent_rect.height() // 2 - self.height() // 2
            )

        # Показываем с анимацией
        self.show()
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def hide_loading(self):
        """Скрыть виджет загрузки с анимацией"""
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.hide)
        self.animation.start()

    def update_status(self, message: str, value: int = None):
        """Обновить статус загрузки

        Args:
            message (str): Новый текст статуса
            value (int, optional): Значение прогресса (0-100)
        """
        self.status_label.setText(message)
        if value is not None:
            self.progress.set_progress(value)

    def cancel_loading(self):
        """Отмена загрузки"""
        self.hide_loading()
        self.cancelled.emit()  # Эмитим сигнал отмены