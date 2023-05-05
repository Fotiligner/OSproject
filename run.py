import sys, os
from PyQt5.Qt import Qt
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPainter, QIcon, QCursor, QPixmap
from PyQt5.QtCore import QEventLoop, QTimer
import UI.Process_Module_UI as Process_Module_UI
from UI.Main_Module_UI import MainTab, EmittingStr
import UI.IO_ui as IO_UI

from Controller import Controller

from UI.main_test import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton

class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))
        loop = QEventLoop()
        QTimer.singleShot(100, loop.quit)
        loop.exec_()

class Main_Board(QMainWindow, Ui_MainWindow):
    def __init__(self, os_controller):
        super(Main_Board, self).__init__()
        self.tab = MainTab(os_controller.file_module, os_controller.process_module)   # 所有原件需要在setup前初始化
        self.tab_2 = Process_Module_UI.ProcessTab(os_controller.process_module)

        # IO界面初始化
        self.tab_3 = IO_UI.Ui_QWidget()
        self.tab_3.setupUi(self.tab_3)

        self.setupUi(self)
        self.tabWidget.setGeometry(QtCore.QRect(20, 40, 1161, 800))
        self.textBrowser.setVisible(False)

        self.tab.action_cmd.triggered.connect(self.ui_cmd)
        self.tab_visible = False

        # 下面将输出重定向到textBrowser中
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)

    def ui_cmd(self):  # 调整主界面可视化
        if not self.tab_visible:
            self.tab_visible = True
            self.textBrowser.setVisible(True)
            self.tabWidget.setGeometry(QtCore.QRect(20, 40, 1161, 571))
        else:
            self.tab_visible = False
            self.textBrowser.setVisible(False)
            self.tabWidget.setGeometry(QtCore.QRect(20, 40, 1161, 800))


    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()


if __name__ == "__main__":
    os_controller = Controller()
    app = QApplication(sys.argv)
    win = Main_Board(os_controller)
    win.show()
    sys.exit(app.exec_())
