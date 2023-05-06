
from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton, QHBoxLayout, QScrollArea, QSizePolicy, QLineEdit

import Process.Process_Module

# 进程模块的TAB
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame

# 用于添加分割线的函数
def addLine(layout,type):
    line = QFrame()
    if(type=="V"):
        line.setFrameShape(QFrame.VLine)
    else:
        line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    layout.addWidget(line)


class currentStatusLabel(QLabel):
    def __init__(self,process_module):
        super().__init__()
        ### 获取进程模块
        self.process_module = process_module

        ## 设置定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateText)
        self.timer.start(100)

        layout = QVBoxLayout()
        ### 上面的文字部分

        self.text_label = QLabel("当前执行进程")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label1 = QLabel("当前时刻")
        self.text_label1.setAlignment(Qt.AlignCenter)
        self.text_label2 = QLabel("当前使用的调度算法")
        self.text_label2.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.text_label1)
        layout.addWidget(self.text_label)
        layout.addWidget(self.text_label2)

        ### 按钮部分
        self.buttonFCFS = QPushButton("FCFS")
        self.button2 = QPushButton("抢占优先级")
        self.button3 = QPushButton("时间片轮转")
        layout.addWidget(self.buttonFCFS)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        self.buttonFCFS.clicked.connect(lambda: self.switchSchedule(self.buttonFCFS))
        self.button2.clicked.connect(lambda: self.switchSchedule(self.button2))
        self.button3.clicked.connect(lambda: self.switchSchedule(self.button3))
        self.setLayout(layout)

    #根据按钮调整算法
    def switchSchedule(self, button):
        if(button.text()=="FCFS"):
            self.process_module.schedule_type="FCFS"
        elif (button.text() == "抢占优先级"):
            self.process_module.schedule_type = "Preempting"
        elif (button.text() == "时间片轮转"):
            self.process_module.schedule_type = "RR"

    def updateText(self):
        # 获取值
        time = Process.Process_Module.current_time
        current_running = self.process_module.current_pid

        # 更新当前StatusLabel的文本属性
        self.text_label1.setText(f"当前时刻:{time}")
        self.text_label.setText(f"当前执行进程: {current_running}")
        self.text_label2.setText(f"当前使用的调度算法:{self.process_module.schedule_type}")


### ready队列的Label
class readyQueueLabel(QLabel):
    def __init__(self,process_module):
        super().__init__()
        self.length = len(process_module.ready_queue)

        layout = QVBoxLayout()
        label = QLabel("ready队列")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # 创建多个按钮并添加到布局中
        for i in range(self.length):
            btn = QPushButton("Button {}".format(i + 1))
            layout.addWidget(btn)

        # 将布局添加到QScrollArea的QWidget中
        widget = QWidget()
        widget.setLayout(layout)

        # 创建一个滚动区域并将QWidget添加到其中
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(widget)

        # 设置滚动区域的大小策略
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # 将QScrollArea设置为当前label的布局
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)
### 等待队列的Label
class waitingQueueLabel(QLabel):
    def __init__(self, text):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("waiting队列")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # 创建多个按钮并添加到布局中
        for i in range(6):
            btn = QPushButton("Button {}".format(i + 1))
            layout.addWidget(btn)

        # 将布局添加到QScrollArea的QWidget中
        widget = QWidget()
        widget.setLayout(layout)

        # 创建一个滚动区域并将QWidget添加到其中
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(widget)

        # 设置滚动区域的大小策略
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # 将QScrollArea设置为当前label的布局
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)
### 预留给甘特图的地方
class Label4(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
### 创建新进程的Laebl
class createProcessLabel(QLabel):
    def __init__(self, process_module):
        super().__init__()
        # 创建一个垂直布局
        layout = QVBoxLayout()

        # 创建三个文本框并添加到布局中
        self.textbox1 = QLineEdit()
        self.textbox1.setPlaceholderText("uid")
        self.textbox2 = QLineEdit()
        self.textbox3 = QLineEdit()
        layout.addWidget(self.textbox1)
        layout.addWidget(self.textbox2)
        layout.addWidget(self.textbox3)
        self.button = QPushButton("创建进程")
        layout.addWidget(self.button)
        self.button.clicked.connect(self.outputTextboxes)
        widget = QWidget()
        widget.setLayout(layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(widget)
        widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        widget.setMaximumSize(300,200)
        self.setLayout(QVBoxLayout())
        self.setFixedSize(300, 200)
        self.layout().addWidget(scroll_area)

    def outputTextboxes(self):
        print(self.textbox1.text())
        print(self.textbox2.text())
        print(self.textbox3.text())
class SchedulerLabel(QLabel):
    def __init__(self, text):
        super().__init__()
        layout = QVBoxLayout()
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.text_label)
        self.button1 = QPushButton("FCFS")
        self.button2 = QPushButton("抢占优先级")
        self.button3 = QPushButton("时间片轮转")
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        self.button1.clicked.connect(lambda: self.setTextFromButton(self.button1))
        self.button2.clicked.connect(lambda: self.setTextFromButton(self.button2))
        self.button3.clicked.connect(lambda: self.setTextFromButton(self.button3))
        self.setLayout(layout)

    def setTextFromButton(self, button):
        self.text_label.setText(button.text())
### 属于进程系统的TAB
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
        label3 = waitingQueueLabel("waiting队列")
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