
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
from PyQt5.QtGui import QPalette, QIcon, QPainter, QBrush, QPixmap, QStandardItemModel, QStandardItem, QColor, QFont


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
        self.text_label3 = QLabel("长期调度队列长度")
        self.text_label3.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.text_label1)
        layout.addWidget(self.text_label)
        layout.addWidget(self.text_label2)
        layout.addWidget(self.text_label3)
        self.setLayout(layout)

    #更新文本
    def updateText(self):
        ##获取对应值
        Number_of_missing_pages=self.memory_module.page_fault
        Number_of_calls = self.memory_module.page_access
        Memory_usage = "{:.2%}".format(self.memory_module.allocated / self.memory_module.pn)
        self.text_label1.setText(f"缺页次数:{Number_of_missing_pages}")
        self.text_label.setText(f"访存次数: {Number_of_calls}")
        self.text_label2.setText(f"内存使用率:{Memory_usage}")

        output = "["
        for i, file_name in enumerate(self.memory_module.filelist):
            output += file_name
            if i < len(self.memory_module.filelist):
                output += "、"
        output += "]"
        self.text_label3.setText(f"长期调度队列:\n{output}")


### 切换调度算法的
class SchedulerLabel(QLabel):
    def __init__(self,memory_module):
        super().__init__()
        self.memory_module = memory_module

        layout = QVBoxLayout()
        self.text_label = QLabel(f"当前调页算法:{self.memory_module.schedule}")
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
        self.tableWidget.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.Window, Qt.white)
        self.tableWidget.setPalette(palette)
        self.tableWidget.setFixedSize(1000, 300)
        row2_layout.addWidget(label)
        row2_layout.addWidget(self.tableWidget)

        #第二行
        row3_layout = QHBoxLayout()
        label5 = currentStatusLabel(self.memo_module)
        self.tableWidget_2 = QTableWidget(self)
        row3_layout.addWidget(label5,2)
        row3_layout.addWidget(self.tableWidget_2,6)

        UI.UI_utils.addLine(row3_layout, "V")
        label6 = SchedulerLabel(self.memo_module)
        row3_layout.addWidget(label6,2)
        layout.addLayout(row2_layout)
        UI.UI_utils.addLine(layout, "H")
        layout.addLayout(row3_layout)
        # layout.setStretch(0,1)
        # layout.setStretch(1,0)
        self.setLayout(layout)

        ## 设置定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_memory_tab)
        self.timer.start(100)

        self.update_memory_tab()
        self.init_memo_process_tab()
        self.memo_module.signal.connect(self.update_memo_process_tab)

    def init_memo_process_tab(self):  # 各进程缺页访存数量统计
        self.tableWidget_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_2.setRowCount(0)
        self.tableWidget_2.setColumnCount(5)
        self.tableWidget_2.setHorizontalHeaderLabels(['进程程序名', '访存数', '缺页数', '缺页率', '调页算法'])


    def update_memo_process_tab(self, page_table, pid):   # 内存释放进程后将信息存入这张表中
        line = self.tableWidget_2.rowCount()
        self.tableWidget_2.setRowCount(line + 1)

        newItem = QTableWidgetItem("pid" + str(pid))
        self.tableWidget_2.setItem(line, 0, newItem)

        newItem = QTableWidgetItem(str(page_table.access))
        self.tableWidget_2.setItem(line, 1, newItem)

        newItem = QTableWidgetItem(str(page_table.fault))
        self.tableWidget_2.setItem(line, 2, newItem)

        newItem = QTableWidgetItem("{:.2%}".format(page_table.fault / page_table.access))
        self.tableWidget_2.setItem(line, 3, newItem)

        newItem = QTableWidgetItem(self.memo_module.schedule)
        self.tableWidget_2.setItem(line, 4, newItem)

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
                newItem.setBackground(QBrush(QColor(min(10 * page_info.pid, 255), min(120 + 10 * page_info.pid, 255), max(0, 255 - 20 * page_info.pid))))
                self.tableWidget.setItem(row, col, newItem)








