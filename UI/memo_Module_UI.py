
from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget, QMenu, QAction, QInputDialog, QGraphicsPixmapItem, QTextEdit, \
    QPushButton, QHBoxLayout, QScrollArea, QSizePolicy, QLineEdit,QScrollBar
import Process.Process_Module
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget, QAbstractItemView, \
    QTableWidgetItem, QPushButton, QScrollArea
import UI.UI_utils
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtGui import QIcon, QPainter, QBrush, QPixmap, QStandardItemModel, QStandardItem, QColor, QFont

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

    #更新文本
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

    #切换的事件
    def setTextFromButton1(self, button):
        if(button.text()=="FIFO"):
            self.memory_module.change_FIFO()
        else:
            self.memory_module.change_LRU()
        self.text_label.setText(f"当前调页算法:{self.memory_module.schedule}")


#内存模块的TAB
class MemoTab(QWidget):
    def __init__(self, memo_module):
        super().__init__()
        self.memo_module = memo_module
        layout = QVBoxLayout()
        #第一行
        row2_layout = QHBoxLayout()
        label = Label4("内存显示图")
        self.tableWidget = QTableWidget()
        self.tableWidget.setFixedSize(1000, 300)
        row2_layout.addWidget(label)
        row2_layout.addWidget(self.tableWidget)

        #第二行
        row3_layout = QHBoxLayout()
        label5 = currentStatusLabel(self.memo_module)
        print(label5.text())
        #self.tableWidget_2 = QTableWidget()
        row3_layout.addWidget(label5)
        #row3_layout.addWidget(self.tableWidget_2)

        # UI.UI_utils.addLine(row3_layout, "V")
        label6 = SchedulerLabel(self.memo_module)
        row3_layout.addWidget(label6)
        layout.addLayout(row2_layout)
        UI.UI_utils.addLine(layout, "H")
        layout.addLayout(row3_layout)
        layout.setStretch(0,0)
        layout.setStretch(1,2)
        self.setLayout(layout)

        ## 设置定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_memory_tab)
        self.timer.start(100)

        self.update_memory_tab()

    def update_memory_tab(self):  # 内存状态图显示
        self.tableWidget.clear()

        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setRowCount(5)
        self.tableWidget.setColumnCount(10)

        self.tableWidget.horizontalHeader().hide()
        self.tableWidget.verticalHeader().hide()

        for i in range(5):
            self.tableWidget.setRowHeight(i, 55)

        for i in range(10):
            self.tableWidget.setColumnWidth(i, 95)

        for i in range(self.memo_module.pn):
            row = i // 10
            col = i % 10
            page_info = self.memo_module.physical_memory[i]
            if page_info.is_allocated == -1:
                newItem = QTableWidgetItem()
                self.tableWidget.setItem(row, col, newItem)


            elif page_info.is_allocated == 1:   # 普通文件
                newItem = QTableWidgetItem(page_info.filename)
                newItem.setBackground(QBrush(QColor(190, 88, 0)))
                self.tableWidget.setItem(row, col, newItem)

            else:   # 进程文件
                newItem = QTableWidgetItem("pid=" + str(page_info.pid))
                newItem.setBackground(QBrush(QColor(0, 120, 255)))
                self.tableWidget.setItem(row, col, newItem)








