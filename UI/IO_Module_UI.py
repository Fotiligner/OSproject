from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *

import IO_Module as IO_Module

import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QPushButton

from UI.IOui import Ui_QWidget

# 用于根据时钟实时显示IO状态
import threading
from threading import Event, Thread, current_thread
import time
import random

from Process.Process_Module import e, current_time  # 直接拿过来是静态变量
class IO_Tab(Ui_QWidget, threading.Thread):
    def __init__(self, io_module):
        super().__init__()
        self.setupUi(self)
        self.io_module = io_module
        self.device_name = []

        self.colcount = 4  # 列数

        self.pushButton_2.clicked.connect(self.update_device_count)
        self.pushButton_3.clicked.connect(self.send_keyboard_input)

    def send_keyboard_input(self):
        self.io_module.keyboard_input_content = self.textEdit.toPlainText()
        self.io_module.keyboard_event = True

    def run(self):   # 线程函数
        target = True  # 进程时钟控制辅助指标
        while self.executing:
            if e.is_set() and target:  # 正常运行
                target = False
                self.table_update()
            elif not e.is_set():  # 进入中断
                e.wait()  # 正在阻塞状态,当event变为True时就激活
                target = True

    def table_update(self):   # 更新三张表中的内容,是实时更新的
        # 界面不如弄成横过来的
        self.tableWidget.clear()
        self.tableWidget_2.clear()
        self.tableWidget_3.clear()

        #print(self.io_module.device_table["printer"].is_busy)
        device_count = []   # 设备数量，可自定义

        for k, v in self.io_module.device_table.items():  # 设备名和设备device类
            self.device_name.append(k)
            device_count.append(v.device_count)

        # 设为内容不可修改状态
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_3.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # 设定行列数和设备当前使用信息
        #print(device_count)
        self.tableWidget.setRowCount(device_count[0])
        self.tableWidget_2.setRowCount(device_count[1])
        self.tableWidget_3.setRowCount(1)

        self.tableWidget.setColumnCount(self.colcount)
        self.tableWidget_2.setColumnCount(self.colcount)
        self.tableWidget_3.setColumnCount(self.colcount)

        self.tableWidget.setHorizontalHeaderLabels(['设备名', 'pid', 'IO内容', '已执行时间'])
        self.tableWidget_2.setHorizontalHeaderLabels(['设备名', 'pid', 'IO内容', '已执行时间'])
        self.tableWidget_3.setHorizontalHeaderLabels(['文件名', 'pid', '磁盘读写信息', '已执行时间'])

        self.table_info(self.tableWidget, self.device_name[0])
        self.table_info(self.tableWidget_2, self.device_name[1])
        #self.table_info(self.tableWidget_3, "disk")

    def line_info_device(self, device_name, pid, content, time, line, table):
        newItem = QTableWidgetItem(device_name)
        table.setItem(line, 0, newItem)

        newItem = QTableWidgetItem(pid)
        table.setItem(line, 1, newItem)

        newItem = QTableWidgetItem(content)
        table.setItem(line, 2, newItem)

        newItem = QTableWidgetItem(time)
        table.setItem(line, 3, newItem)
    def table_info(self, tablewidget, device_name):
        if device_name != "disk":
            device_info = self.io_module.device_table[device_name]
            for i, state in enumerate(device_info.is_busy):
                if state == 0:   # 当前是空闲状态
                    content1 = "NULL"
                    content2 = "NULL"
                    content3 = "NULL"
                else:   # 该设备当前是忙状态
                    for request in device_info.request_queue:
                        if request.target_device_count == i:
                            content1 = str(request.source_pid)
                            content2 = request.content
                            content3 = str(request.IO_time - request.already_time)
                self.line_info_device(device_name + str(i), content1, content2, content3, i, tablewidget)
        elif device_name == "Disk":
            pass


    def update_device_count(self):  # 自定义当前设备数量
        # 首先判断当前是否为可修改状态
        is_changeable = True
        for k, v in self.io_module.device_table.items():  # 设备名和设备device类
            for request in v.request_queue:
                if request.is_finish != 1:
                    is_changeable = False
                    break

        if not is_changeable:
            reply = QMessageBox.information(self, "Error", "There are some requests waiting",  QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            print("hello")
            count = self.spinBox.value()
            device_name = self.comboBox.currentText()

            self.io_module.device_table[device_name].device_count = count
            self.io_module.device_table[device_name].is_busy = [0] * count





        
