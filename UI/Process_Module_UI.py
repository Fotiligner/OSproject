import random
import string
from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton, QHBoxLayout, QScrollArea, QSizePolicy, QLineEdit,QScrollBar,QGridLayout,QMessageBox,QTableWidget,QTableWidgetItem

import Process.Process_Module

# 进程模块的TAB
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
import UI.UI_utils

## 行表示进程, 列表示时间
ganttTable = [[0 for j in range(1)] for i in range(1)]


table = [#       cpu利用率   外设平均利用率    总时间    平均等待时间    平均周转时间   当前算法模式下的CPU工作时间   当前总的等待时间
    ["先到先服务", 0,         0,             0,       0,            0,           0,                      0],
    ["时间片轮转", 0,         0,             0,       0,            0,           0,                      0],
    ["抢占式优先级",0, 0, 0, 0, 0, 0, 0],
]


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

        # 更新当前StatusLabel的文本属性
        self.text_label1.setText(f"当前时刻:{time}")
        if(self.process_module.running_pid != -1):
            self.text_label.setText(f"当前执行进程: {self.process_module.running_pid}")
        else:
            self.text_label.setText(f"当前执行进程: {0} (init进程)")
        if(self.process_module.schedule_type == "RR"):
            self.text_label2.setText(f"当前使用的调度算法:{self.process_module.schedule_type}当前时间片大小:{self.process_module.time_slot}")
        else:
            self.text_label2.setText(f"当前使用的调度算法:{self.process_module.schedule_type}")

        # 更新执行列表
        self.updateTable()
    def updateTable(self):
        try:
            time = Process.Process_Module.current_time
            current_running = self.process_module.running_pid
            if(current_running==-1):
                current_running=0
            if(len(ganttTable)<current_running+1):
                new_row = [0] * len(ganttTable[0])
                ganttTable.append(new_row)
            if(len(ganttTable[0])<=time):
                ganttTable[current_running].append(1)
                for i in range(len(ganttTable)):
                    if i != current_running:
                        ganttTable[i].append(0)

                #对于table的状态更新
                if(self.process_module.schedule_type=="FCFS"):
                    table[0][3]+=1
                    if(self.process_module.running_pid != -1):
                        table[0][6] += 1
                    table[0][1]=table[0][6] * 100 /table[0][3]  #计算CPU利用率
                    table[0][7]+=len(self.process_module.ready_queue)
                    table[0][4] = table[0][7] / len(ganttTable)

                elif(self.process_module.schedule_type=="RR"):
                    table[1][3] += 1
                    if(self.process_module.running_pid != -1):
                        table[1][6] += 1
                    table[1][1]=table[1][6] * 100 /table[1][3]  #计算CPU利用率
                    table[1][7]+=len(self.process_module.ready_queue)
                    table[1][4] = table[1][7] / len(ganttTable)

                elif(self.process_module.schedule_type=="Preempting"):
                    table[2][3] += 1
                    if(self.process_module.running_pid != -1):
                        table[2][6] += 1
                    table[2][1]=table[2][6] * 100 /table[2][3]  #计算CPU利用率
                    table[2][7]+=len(self.process_module.ready_queue)
                    table[2][4] = table[2][7] / len(ganttTable)



        except Exception as ex:
            print("出现如下异常%s" % ex)


### ready队列的Label
class readyQueueLabel(QLabel):
    def __init__(self, process_module):
        super().__init__()
        self.process_module = process_module
        self.layout = QVBoxLayout()

        label = QLabel("ready队列")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_slots)
        self.timer.start(1000)
        self.setLayout(self.layout)

    def update_slots(self):
        for i in range(self.layout.count() - 1, -1, -1):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setParent(None)
        ready_queue = self.process_module.ready_queue
        num_buttons = len(ready_queue)
        for i in range(num_buttons):
            btn = QPushButton("进程 {}".format(ready_queue[i]))
            btn.clicked.connect(lambda _, pid=ready_queue[i]: self.confirm_slot(pid))
            self.layout.addWidget(btn)

    def confirm_slot(self, pid):
        try:
            reply = QMessageBox.question(self, '提示', f'是否杀死进程 {pid}？',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                # 执行 kill 进程的操作
                self.process_module.kill_process(pid)

                # 发送一个事件
                event = QEvent(QEvent.User)
                QApplication.postEvent(self, event)
            else:
                # 取消操作
                pass

        except Exception as ex:
            print("出现如下异常%s" % ex)
### 等待队列的Label
class waitingQueueLabel(QLabel):
    def __init__(self, process_module):
        super().__init__()
        self.process_module = process_module
        self.layout = QVBoxLayout()

        label = QLabel("waiting队列")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_slots)
        self.timer.start(1000)
        self.setLayout(self.layout)

    def update_slots(self):
        for i in range(self.layout.count() - 1, -1, -1):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setParent(None)

        waiting_queue = self.process_module.waiting_queue
        num_buttons = len(waiting_queue)


        for i in range(num_buttons):
            btn = QPushButton("进程 {}".format(waiting_queue[i]))
            self.layout.addWidget(btn)
### 甘特图的Label
class ganttLabel(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        scrollArea = QScrollArea(self)
        scrollArea.setWidgetResizable(True)
        scrollArea.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        scrollArea.setMinimumSize(1127, 250)
        scrollArea.setMaximumSize(1127, 250)
        self.grid = QGridLayout()
        gridWidget = QWidget()
        gridWidget.setLayout(self.grid)
        scrollArea.setWidget(gridWidget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGrid)
        self.timer.start(1000)

        for i in range(len(ganttTable)):
            for j in range(len(ganttTable[0])):
                cell = QLabel()
                if ganttTable[i][j] == 0:
                    cell.setStyleSheet("background-color: white")
                else:
                    cell.setStyleSheet("background-color: gray")
                self.grid.addWidget(cell, i + 1, j + 1)
                self.grid.setRowMinimumHeight(i + 1, 50)
                self.grid.setColumnMinimumWidth(j + 1, 50)

                if i == 0:
                    label = QLabel(str(j))
                    label.setAlignment(Qt.AlignCenter)
                    self.grid.addWidget(label, 0, j + 1)

                if j == 0:
                    label = QLabel(str(i))
                    label.setAlignment(Qt.AlignCenter)
                    self.grid.addWidget(label, i + 1, 0)

        self.setFixedSize(1200, 250)

    def updateGrid(self):
        # 清空现有网格内容

        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)

            if item.widget():
                item.widget().deleteLater()
            self.grid.removeItem(item)





        for i in range(len(ganttTable)):
            for j in range(len(ganttTable[0])):
                cell = QLabel()
                if ganttTable[i][j] == 0:
                    cell.setStyleSheet("background-color: white")
                else:
                    cell.setStyleSheet("background-color: gray")
                self.grid.addWidget(cell, i + 1, j + 1)

                if i == 0:
                    label = QLabel(str(j))
                    label.setAlignment(Qt.AlignCenter)
                    self.grid.addWidget(label, 0, j + 1)

        for j in range(len(ganttTable) + 1):
            if j == 0:
                continue
            label = QLabel(str(j - 1))
            label.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(label, j, 0)
        scrollArea = self.findChild(QScrollArea)
        scrollArea.horizontalScrollBar().setValue(scrollArea.horizontalScrollBar().maximum())
### 显示当前进程状态的Label
class createProcessLabel(QLabel):
    def __init__(self, process_module):
        super().__init__()
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

        self.setLayout(layout)
    def updateText(self):
        # 获取值
        try:
            if(self.process_module.running_pid!=0):
                PCB = self.process_module.pcb_pool[self.process_module.loc_pid_inPool(self.process_module.running_pid)]
                # 更新当前StatusLabel的文本属性
                self.text_label1.setText(f"当前pc:{PCB.pc}")
                self.text_label.setText(f"当前进程pid: {PCB.pid}")
                self.text_label2.setText(f"当前进程启动时间:{PCB.start_time}")
            else:
                self.text_label1.setText(f"初始进程")
                self.text_label.setText(f"初始进程")
                self.text_label2.setText(f"初始进程")
        except Exception as ex:
            self.text_label1.setText(f"初始进程")
            self.text_label.setText(f"初始进程")
            self.text_label2.setText(f"初始进程")

class SchedulerLabel(QLabel):
    def __init__(self, text):
        super().__init__()
        self.table = QTableWidget(3, 6)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = QTableWidgetItem(str(table[row][col]))
                self.table.setItem(row, col, item)

        # 设置表头
        header_list = ["算法名称", "CPU平均利用率", "外设平均利用率", "总时间",
                       "平均等待时间", "平均周转时间"]
        for i, header in enumerate(header_list):
            item = QTableWidgetItem(header)
            self.table.setHorizontalHeaderItem(i, item)

        self.setFixedSize(800, 250)

        # 设置定时器，每隔一秒刷新表格内容
        timer = QTimer(self)
        timer.timeout.connect(self.update_table)
        timer.start(1000)

    def update_table(self):
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = QTableWidgetItem(str(table[row][col]))
                self.table.setItem(row, col, item)

### 属于进程系统的TAB
class ProcessTab(QWidget):
    def __init__(self, process_module):
        super().__init__()
        self.process_module = process_module

        layout = QVBoxLayout()
        #第一行
        row1_layout = QHBoxLayout()
        UI.UI_utils.addLine(row1_layout,"V")
        label1 = currentStatusLabel(process_module)
        row1_layout.addWidget(label1)
        UI.UI_utils.addLine(row1_layout,"V")
        label2 = readyQueueLabel(process_module)
        row1_layout.addWidget(label2)
        UI.UI_utils.addLine(row1_layout,"V")
        label3 = waitingQueueLabel(process_module)
        row1_layout.addWidget(label3)

        #第二行
        row2_layout = QHBoxLayout()
        label4 = ganttLabel("甘特图")
        row2_layout.addWidget(label4)

        #第三行
        row3_layout = QHBoxLayout()
        label5 = createProcessLabel(process_module)
        row3_layout.addWidget(label5)
        UI.UI_utils.addLine(row3_layout, "V")
        label6 = SchedulerLabel("调度算法之类的")
        row3_layout.addWidget(label6)
        layout.addLayout(row1_layout)
        UI.UI_utils.addLine(layout, "H")
        layout.addLayout(row2_layout)
        UI.UI_utils.addLine(layout, "H")
        layout.addLayout(row3_layout)
        self.setLayout(layout)
