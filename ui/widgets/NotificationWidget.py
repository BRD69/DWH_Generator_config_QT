from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QColor, QPalette, QFont

class NotificationWidget(QWidget):
    """Виджет для отображения всплывающих уведомлений"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

        # Таймер для автоматического скрытия
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide_notification)

        # Анимация появления/исчезновения
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(300)  # 300 мс для анимации

        # Изначально скрыт
        self.hide()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Устанавливаем минимальный размер виджета
        self.setMinimumSize(300, 75)  # Минимальная высота 75px
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)  # Растягивается по ширине, адаптируется по высоте

        # Основной контейнер
        self.container = QFrame(self)
        self.container.setObjectName("notificationContainer")
        self.container.setStyleSheet("""
            QFrame#notificationContainer {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(12, 8, 12, 12)  # Уменьшаем верхний отступ до 8
        container_layout.setSpacing(4)

        # Заголовок уведомления
        self.title_label = QLabel(self)
        self.title_label.setWordWrap(True)
        title_font = QFont("Segoe UI", 10)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #333333;")
        container_layout.addWidget(self.title_label)

        # Разделительная линия
        self.separator = QFrame(self)
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setStyleSheet("background-color: #e0e0e0;")
        container_layout.addWidget(self.separator)

        # Текст уведомления
        self.message_label = QLabel(self)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Segoe UI", 10))
        self.message_label.setStyleSheet("color: #333333;")
        self.message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)  # Растягивается по ширине, адаптируется по высоте
        container_layout.addWidget(self.message_label)

        layout.addWidget(self.container)

    def show_notification(self, message: str, status: str = "info", title: str = None):
        """Показать уведомление

        Args:
            message (str): Текст сообщения
            status (str): Статус сообщения ("info", "warning" или "important")
        """
        # Устанавливаем заголовок и текст
        if title:
            self.title_label.setText(title)
        else:
            if status == "info":
                self.title_label.setText("Уведомление")
            elif status == "warning":
                self.title_label.setText("Предупреждение")
            else:  # important
                self.title_label.setText("Важное сообщение")
        self.message_label.setText(message)

        # Настраиваем стиль в зависимости от статуса
        if status == "info":
            self.container.setStyleSheet("""
                QFrame#notificationContainer {
                    background-color: #f0f7ff;
                    border-radius: 8px;
                    border: 1px solid #b3d7ff;
                }
            """)
            self.separator.setStyleSheet("background-color: #b3d7ff;")
        elif status == "warning":
            self.container.setStyleSheet("""
                QFrame#notificationContainer {
                    background-color: #fff7e6;
                    border-radius: 8px;
                    border: 1px solid #ffd700;
                }
            """)
            self.separator.setStyleSheet("background-color: #ffd700;")
        else:  # important
            self.container.setStyleSheet("""
                QFrame#notificationContainer {
                    background-color: #fff0f0;
                    border-radius: 8px;
                    border: 1px solid #ffb3b3;
                }
            """)
            self.separator.setStyleSheet("background-color: #ffb3b3;")

        # Показываем виджет
        self.show()

        # Позиционируем в правом нижнем углу родительского окна
        if self.parent():
            parent_rect = self.parent().rect()
            self.move(
                parent_rect.width() - self.width() - 5,
                parent_rect.height() - self.height() - 5
            )

        # Запускаем таймер для автоматического скрытия
        self.timer.start(4000)  # 4 секунды

    def hide_notification(self):
        """Скрыть уведомление с анимацией"""
        self.timer.stop()

        # Анимация исчезновения
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(self.x(), self.y() + 100))
        self.animation.finished.connect(self.hide)
        self.animation.start()