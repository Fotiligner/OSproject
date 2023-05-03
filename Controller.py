from time import sleep

from Command import Command_Moduler
from Process_Module import Process_Module, clock_running
from File_Module import File_Module, Ret_State
from memo_test import MemoryManager
import threading
from threading import Event, Thread, current_thread
import time

import os

class Controller:
    def __init__(self):
        # 初始化操作系统模块
        self.command_moduler = Command_Moduler()
        self.disk_path = os.path.abspath(r".") + "\\MYDISK"
        self.file_module = File_Module(self.disk_path)
        self.memory_module = MemoryManager(self.file_module)
        self.process_module = Process_Module(self.memory_module)

        self.process_module.setDaemon(True)
        self.process_module.executing = True
        self.process_module.start()  # P作为线程开始运行,使用重定义的run函数

        self.current_user = "chafakao"

        self.command_dict = {
            "cd": "cd [file name or path]",
            "ls": "ls [file name or path]",
            "mkdir": "mkdir [directory path]",
            "vi": "vi [file name]",
            "touch": "touch [file name]",
            "rm": "rm [-option] [file name or dir]",
            "chmod": "chmod [file name or path] [authority]",
            "run": "run [file name or path]",  # 运行进程文件
            "fmode": "fmode, display file module state",
            "pmode": "pmode, display process module state",
            "mmode": "mmode, display memory module state",
            "exit": "exit"
        }

    def print_error_info(self, error_info, ret_code=None, command=None):
        if ret_code and ret_code == Ret_State.Success:
            return
        # 输出错误信息
        print('\033[1;31m' + '[error]: ' + '\033[0m' + error_info)
        if ret_code:
            if ret_code == Ret_State.Error_File_Exist:
                print('\033[1;31m ' + "the file already exist." + '\033[0m')
            elif ret_code == Ret_State.Error_File_Not_Exist:
                print('\033[1;31m ' + "the file doesn't exist." + '\033[0m')
            elif ret_code == Ret_State.Error_Path_Not_Exist:
                print('\033[1;31m ' + "the path doesn't exist." + '\033[0m')
            elif ret_code == Ret_State.Error_Dir_Exist:
                print('\033[1;31m ' + "the dir already exist." + '\033[0m')
            elif ret_code == Ret_State.Error_Dir_Not_Exist:
                print('\033[1;31m ' + "the dir doesn't exist." + '\033[0m')

        if command:
            print('\033[1;31m' + command + " : " + self.command_dict[command] + '\033[0m')

    # 运行操作系统，循环检测控制台输入并调用相应的模块
    def execute(self):
        while True:
            commands_list = self.command_moduler.get_command_list(self.current_user, self.file_module.work_path)
            # 每个元素是一个列表，整体长度是当前行输入指令的个数

            if len(commands_list) == 0:
                continue

            for command in commands_list:
                # 输入的指令不存在于操作系统指令集中
                argc = len(command)
                if argc == 0:  # 空指令，比如换行
                    continue

                if command[0] not in self.command_dict.keys():
                    self.print_error_info("command not found")

                    # 遍历指令库，查看相似指令并给出提示
                    command_count = 0
                    for k, v in self.command_dict.items():
                        if k.__contains__(command[0]):
                            if command_count == 0:
                                print('\033[1;31m' + "    Did you mean these commands:" + '\033[0m')
                            print('\033[1;31m' + "       " + k + " : " + v + '\033[0m')
                            command_count += 1
                    continue

                if command[0] == 'run':  # 运行进程文件指令,可以指定多个进程文件进行合并
                    # 后期添加执行文件权限
                    if argc == 1:
                        self.print_error_info("command error ", command="run")
                    else:
                        # 列出可执行文件列表
                        for file_name in command[1:]:
                            self.process_module.create_process(file_name, 1)

                elif command[0] == 'touch':
                    if argc != 2:
                        self.print_error_info("command error", command="touch")
                    else:
                        ret_code = self.file_module.touch(command[1])
                        self.print_error_info("touch error", ret_code=ret_code)

                elif command[0] == "cd":
                    if argc != 2:
                        self.print_error_info("command error", command="cd")
                    else:
                        ret_code = self.file_module.cd(command[1])
                        self.print_error_info("cd error", ret_code=ret_code)

                elif command[0] == "ls":
                    if argc != 1:
                        self.print_error_info("command error", command="ls")
                    else:
                        self.file_module.ls()

                elif command[0] == "mkdir":
                    if argc != 2:
                        self.print_error_info("command error", command="mkdir")
                    else:
                        ret_code = self.file_module.mkdir(command[1])
                        self.print_error_info("mkdir error", ret_code=ret_code)

                elif command[0] == "vi":
                    if argc != 2:
                        self.print_error_info("command error", command="vi")
                    else:
                        ret_code = self.file_module.vi(command[1])
                        self.print_error_info("vi error", ret_code=ret_code)

                elif command[0] == "rm":
                    if argc != 2 and argc != 3:
                        self.print_error_info("command error", command="rm")
                    else:
                        ret_code=None
                        if argc == 2:
                            ret_code=self.file_module.rm(command[1])
                        else:
                            ret_code=self.file_module.rm(mode=command[1],name=command[2])
                        self.print_error_info("rm error", ret_code=ret_code)

                elif command[0] == "kill":
                    self.process_module.kill_process(int(command[1]))

                elif command[0] == "exit":
                    self.process_module.executing = False
                    return

if __name__ == '__main__':
    os_controller = Controller()
    os_controller.execute()
    clock_running = False

