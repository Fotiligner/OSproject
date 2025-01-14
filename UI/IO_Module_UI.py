from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *

import IO_Module as IO_Module

import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QPushButton

from UI.IOui import Ui_QWidget

from PyQt5.QtCore import pyqtSignal,QObject

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

        # 中断输出表tab4初始化
        self.tableWidget_4.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_4.setRowCount(0)
        self.tableWidget_4.setColumnCount(self.colcount)
        self.tableWidget_4.setHorizontalHeaderLabels(['中断类型', 'pid', '设备/文件', '中断总时长'])

        # IO中断，缺页中断和keyboard外在中断
        self.io_module.signal.connect(self.tab_interrupt)

        # 开启时钟
        self.timer = QTimer()
        self.timer.timeout.connect(self.waiting_update)
        self.timer.start(100)

    def tab_interrupt(self, request):
        line = self.tableWidget_4.rowCount()
        self.tableWidget_4.setRowCount(line + 1)

        if request.rw_state == 'r':
            type = "读中断"
        elif request.rw_state == 'w':
            type = "写中断"
        elif request.rw_state == 'p':
            type = "缺页中断"
        elif request.is_disk == False:
            type = "设备IO中断"
        newItem = QTableWidgetItem(type)
        self.tableWidget_4.setItem(line, 0, newItem)

        newItem = QTableWidgetItem(str(request.source_pid))
        self.tableWidget_4.setItem(line, 1, newItem)

        if request.is_disk:
            content = request.file_path
        else:
            content = request.target_device

        newItem = QTableWidgetItem(content)
        self.tableWidget_4.setItem(line, 2, newItem)

        newItem = QTableWidgetItem(str(request.IO_time))
        self.tableWidget_4.setItem(line, 3, newItem)
    def send_keyboard_input(self):
        self.io_module.keyboard_input_content = self.textEdit.toPlainText()
        self.io_module.keyboard_event = True

        line = self.tableWidget_4.rowCount()
        self.tableWidget_4.setRowCount(line + 1)

        type = "设备IO中断"
        newItem = QTableWidgetItem(type)
        self.tableWidget_4.setItem(line, 0, newItem)

        newItem = QTableWidgetItem("外部中断")
        self.tableWidget_4.setItem(line, 1, newItem)

        newItem = QTableWidgetItem("keyboard")
        self.tableWidget_4.setItem(line, 2, newItem)

        newItem = QTableWidgetItem("1")
        self.tableWidget_4.setItem(line, 3, newItem)

    def run(self):   # 线程函数
        target = True  # 进程时钟控制辅助指标
        while self.executing:
            if e.is_set() and target:  # 正常运行
                target = False
                self.table_update()
            elif not e.is_set():  # 进入中断
                e.wait()  # 正在阻塞状态,当event变为True时就激活
                target = True

    def waiting_update(self):
        pass

    def table_update(self):   # 更新三张表中的内容,是实时更新的
        # 界面不如弄成横过来的
        self.tableWidget.clear()
        self.tableWidget_2.clear()
        self.tableWidget_3.clear()

        device_count = []   # 设备数量，可自定义

        for k, v in self.io_module.device_table.items():  # 设备名和设备device类
            self.device_name.append(k)
            device_count.append(v.device_count)

        # 设为内容不可修改状态
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_3.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # 设定行列数和设备当前使用信息
        self.tableWidget.setRowCount(device_count[0])
        self.tableWidget_2.setRowCount(device_count[1])
        self.tableWidget_3.setRowCount(0)

        self.tableWidget.setColumnCount(self.colcount)
        self.tableWidget_2.setColumnCount(self.colcount)
        self.tableWidget_3.setColumnCount(self.colcount)

        self.tableWidget.setHorizontalHeaderLabels(['设备名', 'pid', 'IO内容', '已执行时间'])
        self.tableWidget_2.setHorizontalHeaderLabels(['设备名', 'pid', 'IO内容', '已执行时间'])
        self.tableWidget_3.setHorizontalHeaderLabels(['文件名', 'pid', '磁盘读写状态', '已执行时间'])

        self.table_info(self.tableWidget, self.device_name[0])
        self.table_info(self.tableWidget_2, self.device_name[1])
        self.table_info(self.tableWidget_3, "disk")

        printer_out = ""
        screen_out = ""
        disk_out = ""

        for request in self.io_module.device_table["printer"].request_queue:
            if request.target_device_count == -1 and request.is_finish != 1 and request.is_terminate != 1:
                printer_out += str(request.source_pid) + " "

        for request in self.io_module.device_table["screen"].request_queue:
            if request.target_device_count == -1 and request.is_finish != 1 and request.is_terminate != 1:
                screen_out += str(request.source_pid) + " "

        for request in self.io_module.disk_request_list:
            if request.is_running == 0 and request.is_finish != 1 and request.is_terminate != 1:
                disk_out += str(request.source_pid) + " "

        self.label1.setText(printer_out)
        self.label2.setText(screen_out)
        self.label3.setText(disk_out)
        #self.textEdit_2.setText("hello")
        # self.textBrowser_2.setText(screen_out)
        # print("hello2")
        # self.textBrowser_3.setText(disk_out)
        # print("hello2")

    def line_info_device(self, device_name, pid, content, time, line, table):
        newItem = QTableWidgetItem(device_name)
        table.setItem(line, 0, newItem)

        newItem = QTableWidgetItem(pid)
        table.setItem(line, 1, newItem)

        newItem = QTableWidgetItem(content)
        table.setItem(line, 2, newItem)

        newItem = QTableWidgetItem(time)
        table.setItem(line, 3, newItem)

    def line_info_disk(self, device_name, pid, content, time, table):
        line = table.rowCount()
        table.setRowCount(line + 1)
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
                            content3 = str(request.already_time)
                self.line_info_device(device_name + str(i), content1, content2, content3, i, tablewidget)
        elif device_name == "disk":
            disk_info = self.io_module.disk_request_list
            for i, request in enumerate(disk_info):
                # '文件名', 'pid', '磁盘读写状态', '已执行时间'
                if request.is_running != 0 and request.is_finish == 0 and request.is_terminate == 0:  # 对于所有非中止的内容都进行打印
                    content1 = request.file_path
                    content2 = str(request.source_pid)
                    if request.rw_state == 'r':
                        content3 = "读"
                    elif request.rw_state == 'w':
                        content3 = "写"
                    elif request.rw_state == 'p':
                        content3 = "缺页调入"

                    content4 = str(request.already_time)
                    self.line_info_disk(content1, content2, content3, content4, tablewidget)



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
            count = self.spinBox.value()
            device_name = self.comboBox.currentText()

            self.io_module.device_table[device_name].device_count = count
            self.io_module.device_table[device_name].is_busy = [0] * count





        
