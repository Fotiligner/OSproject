import os
import json
import threading
from threading import Event, Thread, current_thread
import time
import random

class IO_Module:
    def __init__(self, device_filename):  # 初始化当前设备并放入设备队列中
        self.device_table = {}   # 设备表, key是设备名，value是device类

        self.file_table = {}   # 文件表（之后考虑转移到文件模块中）， r表示有进程在读，w表示有进程在写（单次只有一个可以写，可以有多个读）
        self.disk_request_list = []   # 磁盘请求队列

        self.init_device(device_filename)

    def add_request(self, **args):
        print(args)
        request = Request(args)

        # 后期考虑死锁
        # 分配当前空闲的第一台设备

        if request.is_disk == 0:   # 设备IO请求
            for i, busy_state in enumerate(self.device_table[request.target_device].is_busy):
                if busy_state == 0:    # 空闲状态
                    request.target_device_count = i
                    self.device_table[request.target_device].is_busy[i] = 1
                    break

            # 不管是否分配到设备，全部放入设备请求队列中
            self.device_table[request.target_device].request_queue.append(request)   # 在相应设备添加请求队列

        elif request.is_disk == 1:   # 磁盘IO请求
            self.disk_request_list.append(request)   # disk类request中，默认时间为1，若有传入读写时间则按读写时间来统计
            # 文件表就是有r，w和0三种状态，0就表示这个文件曾经出现过
            if request.file_path in self.file_table.keys() and (self.file_table[request.file_path] == 'r' \
                                                               or self.file_table[request.file_path] == '0'):   # 已经存在且处于读状态
                self.file_table[request.file_path] = request.rw_state
                request.is_running = 1
            elif request.file_path not in self.file_table.keys():
                self.file_table[request.file_path] = request.rw_state
                request.is_running = 1

    def init_device(self, device_filename):     # 初始化当前设备属性和状态
        with open(device_filename, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())

        for k, v in data.items():
            device = Device(k, v)
            for i in range(v):
                device.is_busy.append(0)
            self.device_table[k] = device

    def disk_io_run(self):
        # 磁盘IO轮询
        output = []

        # running状态信息更新
        for request in self.disk_request_list:
            if request.is_running == 1:  # 正在运行
                if request.is_finish == 0 and request.is_terminate == 0:
                    request.already_time += 1

                    if request.already_time == request.IO_time:       # 完成了IO操作，显示相应的信息，并且回传给进程模块


                        # request完成状态
                        request.is_finish = 1
                        dict = {}
                        dict['pid'] = request.source_pid
                        dict['file_path'] = request.file_path
                        dict['rw_state'] = request.rw_state
                        output.append(dict)

                        # 回退文件表中当前的rw状态信息
                        state = '0'
                        for temp in self.disk_request_list:
                            if temp.is_finish == 0 and temp.is_terminate == 0 and temp.is_running == 1:
                                state = temp.rw_state

                        self.file_table[request.file_path] = state

        # 考虑非running的request更新
        for request in self.disk_request_list:
            if request.is_running == 0:
                if request.file_path in self.file_table.keys() and (self.file_table[request.file_path] == 'r' \
                                                                    or self.file_table[request.file_path] == '0'):  # 已经存在且处于读状态
                    self.file_table[request.file_path] = request.rw_state
                    request.is_running = 1
                elif request.file_path not in self.file_table.keys():
                    self.file_table[request.file_path] = request.rw_state
                    request.is_running = 1

        return output

    def device_io_run(self):  # 可以考虑多设备同时IO，IO完成后同时返回
        # 设备IO轮询
        output = []  # 当前轮询过后可返回的数据

        for device_name, device in self.device_table.items():  # 遍历设备
            for request in device.request_queue:  # 遍历每一个请求
                if request.target_device_count != -1 and request.is_finish == 0 and request.is_terminate == 0:   # 当前在使用设备,且没有完成IO
                    request.already_time += 1

                    if request.already_time == request.IO_time:       # 完成了IO操作，显示相应的信息，并且回传给进程模块
                        # request完成状态
                        request.is_finish = 1
                        dict = {}
                        dict['pid'] = request.source_pid
                        dict['device_name'] = request.target_device
                        dict['content'] = request.content
                        output.append(dict)

                        # 释放设备
                        device.is_busy[request.target_device_count] = 0   # 重新置为空闲

                        # 在有进程request释放设备时，查看是否为未开始的request分配设备
                        for request_non in device.request_queue:
                            if request_non.target_device_count == -1:
                                request_non.target_device_count = request.target_device_count
                                device.is_busy[request.target_device_count] = 1  # 重新占用设备
                                break

        return output

    def release_process_request(self, pid):  # 中止进程时释放设备和对应request
        # 遍历所有request，删除对应pid的request
        for device_name, device in self.device_table.items():  # 遍历设备
            for request in device.request_queue:  # 遍历每一个请求
                if request.source_pid == pid:
                    request.is_terminate = 1

                    if request.target_device_count != -1: # 已经分配，则释放设备
                        device.is_busy[request.target_device_count] = 0  # 重新置为空闲

    def IO_run(self):   # 整体轮询遍历函数
        #self.disk_io_run()
        return self.device_io_run()

class Device:
    def __init__(self, device_type, device_count):
        self.device_type = device_type
        self.device_count = device_count
        self.request_queue = []   # 存放进程针对对应设备的request
        self.is_busy = []   # 01列表


class Request:
    def __init__(self, args):
        self.source_pid = args["source_pid"]
        self.target_device = args["target_device"]
        self.target_device_count = -1   # 用于表示当前是否有设备接受该请求的工作，若没有则
        self.IO_time = args["IO_time"]
        self.already_time = 0
        self.content = args["content"]       # 存储设备IO传输的数据内容
        self.is_finish = 0   # 0表示未完成，1表示完成
        self.is_terminate = 0  # 0表示进程未中止，1表示中止
        self.priority_num = args["priority_num"]  # 默认优先级（暂时不设置）

        self.is_disk = args["is_disk"]
        self.file_path = args["file_path"]
        self.is_running = 0   # 0表示读写IO为阻塞状态，1表示读写IO为非阻塞状态（正常运行）
        self.rw_state = args["rw_state"]   # 'r' or 'w'



if __name__== "__main__" :
    IO = IO_Module('device.json')
