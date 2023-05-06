from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *

import IO_Module as IO_Module

import PyQt5.QtWidgets as QtWidgets

from UI.IO_ui import Ui_QWidget

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
        self.device_count = []

        self.colcount = 3  # 列数

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

        for k, v in self.io_module.device_table.items():  # 设备名和设备device类
            self.device_name.append(k)
            self.device_count.append(v.device_count)

        # 设为内容不可修改状态
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_3.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # 设定行列数和设备当前使用信息
        self.tableWidget.setRowCount(self.device_count[0])
        self.tableWidget_2.setRowCount(self.device_count[1])
        self.tableWidget_3.setRowCount(self.device_count[2])

        self.tableWidget.setColumnCount(self.colcount)
        self.tableWidget_2.setColumnCount(self.colcount)
        self.tableWidget_3.setColumnCount(self.colcount)

        self.tableWidget.setHorizontalHeaderLabels(['设备名', 'pid', 'IO内容'])
        self.tableWidget_2.setHorizontalHeaderLabels(['设备名', 'pid', 'IO内容'])
        self.tableWidget_3.setHorizontalHeaderLabels(['设备名', 'pid', 'IO内容'])

        self.table_info(self.tableWidget, self.device_name[0])
        self.table_info(self.tableWidget_2, self.device_name[1])
        self.table_info(self.tableWidget_3, self.device_name[2])

    def line_info(self, device_name, pid, content, line, table):
        newItem = QTableWidgetItem(device_name)
        table.setItem(line, 0, newItem)

        newItem = QTableWidgetItem(pid)
        table.setItem(line, 1, newItem)

        newItem = QTableWidgetItem(content)
        table.setItem(line, 2, newItem)
    def table_info(self, tablewidget, device_name):
        device_info = self.io_module.device_table[device_name]
        for i, state in enumerate(device_info.is_busy):
            if state == 0:   # 当前是空闲状态
                content1 = "NULL"
                content2 = "NULL"
                #self.line_info(device_name + str(i), "NULL", "NULL", i, tablewidget)
                #self.line_info(device_name + str(i), str(current_time), str(current_time), i, tablewidget)
            else:   # 该设备当前是忙状态
                for request in device_info.request_queue:
                    if request.target_device_count == i:
                        content1 = str(request.source_pid)
                        content2 = request.content
            self.line_info(device_name + str(i), content1, content2, i, tablewidget)

        if device_name == "keyboard":
            test = []
            for request in device_info.request_queue:
                test.append(request.target_device_count)

            if len(test) != 0:
                print(test)



        
