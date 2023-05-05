from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton, QHBoxLayout, QScrollArea, QSizePolicy, QLineEdit

import IO_Module.IO_Module as IO_Module

class IOTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        #第一行
        row1_layout = QHBoxLayout()
        addLine(row1_layout,"V")
        label1 = currentStatusLabel("当前状态")
        row1_layout.addWidget(label1)
        addLine(row1_layout,"V")
        label2 = readyQueueLabel("ready队列")
        row1_layout.addWidget(label2)
        addLine(row1_layout,"V")
        label3 = waitingQueueLabel("waiting队列")
        row1_layout.addWidget(label3)

        #第二行
        row2_layout = QHBoxLayout()
        label4 = Label4("甘特图")
        row2_layout.addWidget(label4)

        #第三行
        row3_layout = QHBoxLayout()
        label5 = Label5("创建进程")
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