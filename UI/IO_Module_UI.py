from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton, QHBoxLayout, QScrollArea, QSizePolicy, QLineEdit, QTableWidget

import IO_Module as IO_Module

from UI.IO_ui import Ui_QWidget

class IO_Tab(Ui_QWidget):
    def __init__(self, io_module):
        super().__init__()
        self.setupUi(self)
        self.io_module = io_module
        self.device_name = []
        self.device_count = []

        self.colcount = 3

        self.table_update()


    def table_update(self):   # 更新三张表中的内容
        # 界面不如弄成横过来的
        print(self.io_module.device_table)
        for k, v in self.io_module.device_table.items():  # 设备名和设备device类
            self.device_name.append(k)
            self.device_count.append(v.device_count)

        self.tableWidget.setRowCount(self.device_count[0])
        self.tableWidget_2.setRowCount(self.device_count[1])
        self.tableWidget_3.setRowCount(self.device_count[2])

        self.tableWidget.setColumnCount(self.colcount)
        self.tableWidget_2.setColumnCount(self.colcount)
        self.tableWidget_3.setColumnCount(self.colcount)

        self.tableWidget.setHorizontalHeaderLabels(['设备名', 'pid', 'IO内容'])
        self.tableWidget_2.setHorizontalHeaderLabels(['设备名', 'pid', 'IO内容'])
        self.tableWidget_3.setHorizontalHeaderLabels(['设备名', 'pid', 'IO内容'])