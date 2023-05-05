import sys, os
from PyQt5.Qt import Qt
from PyQt5.QtGui import QPainter, QIcon, QCursor, QPixmap
import UI.Process_Module_UI as Process_Module_UI
from UI.Main_Module_UI import MainTab

from Controller import Controller

from UI.main_test import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton

if __name__ == '__main__':
    # 启动操作系统主控制程序，包括文件、内存、进程模块代码在内
    os_controller = Controller()

    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.tab = MainTab(os_controller.file_module, os_controller.process_module)   # 所有原件需要在setup前初始化
    ui.tab_2 = Process_Module_UI.ProcessTab()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())