
from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton, QHBoxLayout, QScrollArea, QSizePolicy, QLineEdit,QScrollBar

import Process.Process_Module
import UI.UI_utils
# 进程模块的TAB
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame

### 预留给晗哥的位置
class Label4(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
### 展示当前状态的Label
class currentStatusLabel(QLabel):
    def __init__(self,memory_module):
        super().__init__()
        self.memory_module = memory_module
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateText)
        self.timer.start(100)

        layout = QVBoxLayout()
        self.text_label = QLabel("缺页次数")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label1 = QLabel("访存次数")
        self.text_label1.setAlignment(Qt.AlignCenter)
        self.text_label2 = QLabel("内存使用率")
        self.text_label2.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.text_label1)
        layout.addWidget(self.text_label)
        layout.addWidget(self.text_label2)
        self.setLayout(layout)

    #根据按钮调整算法
    def updateText(self):
        ##获取对应值
        Number_of_missing_pages=self.memory_module.page_fault
        Number_of_calls = self.memory_module.page_access
        Memory_usage = self.memory_module.physical_rate
        self.text_label1.setText(f"缺页次数:{Number_of_missing_pages}")
        self.text_label.setText(f"访存次数: {Number_of_calls}")
        self.text_label2.setText(f"内存使用率:{Memory_usage}")


### 切换调度算法的
class SchedulerLabel(QLabel):
    def __init__(self,memory_module):
        super().__init__()
        self.memory_module = memory_module



        layout = QVBoxLayout()
        self.text_label = QLabel("选择调页算法")
        self.text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.text_label)
        self.button1 = QPushButton("FIFO")
        self.button2 = QPushButton("LRU")
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        self.button1.clicked.connect(lambda: self.setTextFromButton1(self.button1))
        self.button2.clicked.connect(lambda: self.setTextFromButton1(self.button2))
        self.setLayout(layout)


    def setTextFromButton1(self, button):
        #if(self.memory_module.schedule != null):
        #    print(self.memory_module.schedule)
        #else:
        #    print("11111")
        self.text_label.setText(button.text())

class MemoTab(QWidget):
    def __init__(self, memo_module):
        super().__init__()
        self.process_module = memo_module

        layout = QVBoxLayout()

        #第二行
        row2_layout = QHBoxLayout()
        label4 = Label4("晗哥的图的位置")
        row2_layout.addWidget(label4)

        #第三行
        row3_layout = QHBoxLayout()
        label5 = currentStatusLabel(memo_module)
        row3_layout.addWidget(label5)
        UI.UI_utils.addLine(row3_layout, "V")
        label6 = SchedulerLabel("调度算法之类的")
        row3_layout.addWidget(label6)
        UI.UI_utils.addLine(layout, "H")
        layout.addLayout(row2_layout)
        UI.UI_utils.addLine(layout, "H")
        layout.addLayout(row3_layout)
        self.setLayout(layout)
