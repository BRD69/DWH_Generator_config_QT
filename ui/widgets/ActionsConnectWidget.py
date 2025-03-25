from PyQt5 import QtCore, QtGui, QtWidgets


class ActionsConnectWidget(QtWidgets.QAction):
    def __init__(self, parent=None, name: str = "SQL"):
        super().__init__(parent)
        self.setObjectName("action_connect")
        self.setText(name)
        self.setToolTip(name)

        self.set_status_connect_off()

    def set_status_connect_on(self):
        self.setIcon(QtGui.QIcon(":/icon_button/resources/icons/connect_on.png"))


    def set_status_connect_off(self):
        self.setIcon(QtGui.QIcon(":/icon_button/resources/icons/connect_off.png"))


class LabelConnectWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.setObjectName("label_connect")

    def set_status_connect_on(self):
        self.setPixmap(QtGui.QIcon(":/icon_button/resources/icons/connect_on.png").pixmap(16, 16))

    def set_status_connect_off(self):
        self.setPixmap(QtGui.QIcon(":/icon_button/resources/icons/connect_off.png").pixmap(16, 16))




