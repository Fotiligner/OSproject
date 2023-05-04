import sys, os
import random
from PyQt5.Qt import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QIcon, QCursor, QPixmap
import Process_Module_UI

from File_Module import File_Module, Ret_State
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton, QHBoxLayout


# 进程模块的TAB
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame


def addLine(layout,type):
    line = QFrame()
    if(type=="V"):
        line.setFrameShape(QFrame.VLine)
    else:
        line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    layout.addWidget(line)


def addHorizontalLine(layout):
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    layout.addWidget(line)

class Label1(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)

class Label2(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)

class Label3(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)

class Label4(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)

class Label5(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)

class Label6(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)

class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        row1_layout = QHBoxLayout()
        addLine(row1_layout,"V")
        label1 = Label1("当前状态")
        row1_layout.addWidget(label1)
        addLine(row1_layout,"V")
        label2 = Label2("ready队列")
        row1_layout.addWidget(label2)
        addLine(row1_layout,"V")
        label3 = Label3("waiting队列")
        row1_layout.addWidget(label3)
        row2_layout = QHBoxLayout()
        label4 = Label4("甘特图")
        row2_layout.addWidget(label4)
        row3_layout = QHBoxLayout()
        label5 = Label5("创建进程")
        row3_layout.addWidget(label5)
        addLine(row3_layout, "V")
        label6 = Label6("调度算法之类的")
        row3_layout.addWidget(label6)
        layout.addLayout(row1_layout)
        addLine(layout, "H")
        layout.addLayout(row2_layout)
        addLine(layout, "H")
        layout.addLayout(row3_layout)
        self.setLayout(layout)
