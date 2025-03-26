from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QProgressBar, QFrame)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPen

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

        # Анимация вращения
        self.rotation_angle = 0
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.rotate)
        self.rotation_timer.setInterval(50)

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

        # Круговой индикатор загрузки
        self.progress = QProgressBar(self)
        self.progress.setObjectName("circularProgress")
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedSize(80, 20)  # Фиксированный размер
        self.progress.setStyleSheet("""
            QProgressBar#circularProgress {
                border: none;
                background-color: transparent;
                min-height: 20px;
                max-height: 20px;
            }
        """)
        container_layout.addWidget(self.progress, alignment=Qt.AlignCenter)

        # Текст статуса
        self.status_label = QLabel(self)
        self.status_label.setWordWrap(True)
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #333333;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(30)  # Уменьшаем минимальную высоту
        self.status_label.setMaximumHeight(40)  # Добавляем максимальную высоту
        container_layout.addWidget(self.status_label)

        # Кнопка отмены
        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setFont(QFont("Segoe UI", 9))
        self.cancel_button.setFixedWidth(120)
        self.cancel_button.setFixedHeight(30)  # Фиксированная высота кнопки
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
        self.progress.setValue(0)
        self.rotation_angle = 0

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
        self.rotation_timer.start()

    def hide_loading(self):
        """Скрыть виджет загрузки с анимацией"""
        self.rotation_timer.stop()
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
            self.progress.setValue(value)

    def cancel_loading(self):
        """Отмена загрузки"""
        self.rotation_timer.stop()
        self.hide_loading()
        self.cancelled.emit()  # Эмитим сигнал отмены

    def rotate(self):
        """Анимация вращения"""
        self.rotation_angle = (self.rotation_angle + 5) % 360
        self.progress.update()

    def paintEvent(self, event):
        """Переопределение метода paintEvent для вращения"""
        super().paintEvent(event)
        painter = QPainter(self.progress)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.progress.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 3

        # Фоновый круг
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#e9ecef"))
        painter.drawEllipse(center.x() - radius, center.y() - radius,
                          radius * 2, radius * 2)

        # Вращающийся индикатор
        painter.setPen(QPen(QColor("#007bff"), 3))
        painter.setBrush(Qt.NoBrush)
        start_angle = 90 * 16 - self.rotation_angle * 16
        span_angle = 270 * 16
        painter.drawArc(center.x() - radius, center.y() - radius,
                       radius * 2, radius * 2, start_angle, span_angle)