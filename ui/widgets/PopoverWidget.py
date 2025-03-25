from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QPainter, QPainterPath

class PopoverWidget(QWidget):
    def __init__(self, parent=None, text: str = "Это кастомный Popover!"):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Создаем основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Создаем контейнер с фоном
        container = QFrame(self)
        container.setObjectName("popoverContainer")
        container.setStyleSheet("""
            QFrame#popoverContainer {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 5px;
            }
        """)

        # Создаем layout для контейнера
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)

        # Добавляем текст
        label = QLabel(text, container)
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 10))
        label.setStyleSheet("""
            QLabel {
                color: #333333;
            }
        """)
        container_layout.addWidget(label)

        # Добавляем контейнер в основной layout
        layout.addWidget(container)

        # Устанавливаем стили
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

        # Настройка анимации
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(200)

        # Настройка размера
        self.setMinimumWidth(200)
        self.setMaximumWidth(400)

        # Флаг для отслеживания состояния анимации
        self.is_animating = False

    def show(self):
        """Переопределяем метод show для добавления анимации появления"""
        if not self.is_animating:
            self.is_animating = True
            # Сохраняем начальную позицию
            start_pos = self.pos()
            # Устанавливаем начальную позицию выше на 20 пикселей
            self.move(start_pos.x(), start_pos.y() - 20)
            # Настраиваем анимацию
            self.animation.setStartValue(self.pos())
            self.animation.setEndValue(start_pos)
            self.animation.finished.connect(lambda: setattr(self, 'is_animating', False))
            self.animation.start()

        super().show()

    def paintEvent(self, event):
        """Переопределяем метод paintEvent для добавления тени"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Создаем путь для отрисовки тени
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 8, 8)

        # Рисуем тень
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawPath(path.translated(2, 2))

        # Рисуем основной фон
        painter.setBrush(QColor(255, 255, 255))
        painter.drawPath(path)

        super().paintEvent(event)

    def resizeEvent(self, event):
        """Переопределяем метод resizeEvent для обновления формы"""
        super().resizeEvent(event)
        self.update()



