import sys, os
import random
from PyQt5.Qt import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QIcon, QCursor, QPixmap
import Process_Module_UI

from File_Module import File_Module, Ret_State
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton

# 进程模块的TAB
class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("完蛋了. 要开始做了")
        layout.addWidget(label)
        self.setLayout(layout)

