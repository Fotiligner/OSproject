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

        # 创建一个垂直布局
        layout = QVBoxLayout()

        # 创建第一行水平布局
        row1_layout = QHBoxLayout()
        # 添加竖直分割线
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        row1_layout.addWidget(line)
        # 添加第一个文本标签
        label1 = Label1("当前状态")
        row1_layout.addWidget(label1)
        # 添加竖直分割线
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        row1_layout.addWidget(line)
        # 添加第二个文本标签
        label2 = Label2("ready队列")
        row1_layout.addWidget(label2)
        # 添加竖直分割线
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        row1_layout.addWidget(line)
        # 添加第三个文本标签
        label3 = Label3("waiting队列")
        row1_layout.addWidget(label3)

        # 创建第二行水平布局
        row2_layout = QHBoxLayout()
        # 添加文本标签
        label4 = Label4("甘特图")
        row2_layout.addWidget(label4)

        # 创建第三行水平布局
        row3_layout = QHBoxLayout()
        # 添加第一个文本标签
        label5 = Label5("创建进程")
        row3_layout.addWidget(label5)
        # 添加竖直分割线
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        row3_layout.addWidget(line)
        # 添加第二个文本标签
        label6 = Label6("调度算法之类的")
        row3_layout.addWidget(label6)

        # 将三个水平布局添加到垂直布局中
        layout.addLayout(row1_layout)
        # 添加水平分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        layout.addLayout(row2_layout)
        # 添加水平分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        layout.addLayout(row3_layout)

        # 将布局设置为主窗口的布局
        self.setLayout(layout)
