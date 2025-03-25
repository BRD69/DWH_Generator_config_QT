from PyQt5 import QtCore, QtGui, QtWidgets


class PageWidget(QtWidgets.QWidget):
    def __init__(self, name: str, parent: QtWidgets.QWidget = None):
        super().__init__()

        self.name = name
        self.parent = parent

        self.setObjectName(name)
