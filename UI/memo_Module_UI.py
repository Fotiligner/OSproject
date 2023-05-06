
from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton, QHBoxLayout, QScrollArea, QSizePolicy, QLineEdit,QScrollBar

import Process.Process_Module

# 进程模块的TAB
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame


class ProcessTab(QWidget):
    def __init__(self, process_module):
        super().__init__()
        self.process_module = process_module

        layout = QVBoxLayout()
        #第一行
        row1_layout = QHBoxLayout()
        addLine(row1_layout,"V")
        label1 = currentStatusLabel(process_module)
        row1_layout.addWidget(label1)
        addLine(row1_layout,"V")
        label2 = readyQueueLabel(process_module)
        row1_layout.addWidget(label2)
        addLine(row1_layout,"V")
        label3 = waitingQueueLabel(process_module)
        row1_layout.addWidget(label3)

        #第二行
        row2_layout = QHBoxLayout()
        label4 = Label4("甘特图")
        row2_layout.addWidget(label4)

        #第三行
        row3_layout = QHBoxLayout()
        label5 = createProcessLabel(process_module)
        row3_layout.addWidget(label5)
        addLine(row3_layout, "V")
        label6 = SchedulerLabel("调度算法之类的")
        row3_layout.addWidget(label6)
        layout.addLayout(row1_layout)
        addLine(layout, "H")
        layout.addLayout(row2_layout)
        addLine(layout, "H")
        layout.addLayout(row3_layout)
        self.setLayout(layout)
