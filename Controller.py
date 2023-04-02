from time import sleep

from Command import Command_Moduler
from Process_Module import Process_Module


class Controller:
    def __init__(self):
        # 初始化操作系统模块
        self.command_moduler = Command_Moduler()
        self.process_module = Process_Module()


        self.current_path = "root/"
        self.current_user = "chafakao"

        self.command_dict = {
            "cd" : "cd [file name or path]",
            "ls" : "ls [file name or path]",
            "mkdir" : "mkdir [directory path]",
            "touch" : "touch [file name]",
            "rm" : "rm [file name or path or directory path]",
            "chmod" : "chmod [file name or path] [authority]",
            "run" : "run [file name or path]",     # 运行进程文件
            "fmode" : "fmode, display file module state",
            "pmode" : "pmode, display process module state",
            "mmode" : "mmode, display memory module state"
        }

    def print_error_info(self, error_info, command=None):
        # 输出错误信息
        print('\033[1;31m' + '[error]: ' + error_info)
        if command:
            print('\033[1;31m' + command + " : " + self.command_dict[command])



    # 运行操作系统，循环检测控制台输入并调用相应的模块
    def execute(self):
        while True:
            commands_list = self.command_moduler.get_command_list(self.current_user, self.current_path)
            # 每个元素是一个列表，整体长度是当前行输入指令的个数

            if len(commands_list) == 0:
                continue

            for command in commands_list:
                # 输入的指令不存在于操作系统指令集中
                argc = len(command)
                if argc == 0:   # 空指令，比如换行
                    continue

                if command[0] not in self.command_dict.keys():
                    self.print_error_info("command not found")

                    # 遍历指令库，查看相似指令并给出提示
                    command_count = 0
                    for k, v in self.command_dict.items():
                        if k.__contains__(command[0]):
                            if command_count == 0:
                                print('\033[1;31m' + "    Did you mean these commands:")
                            print('\033[1;31m' + "       " + k + " : " + v + '\033[0m')
                            command_count += 1
                    continue

                if command[0] == 'run':   # 运行进程文件指令,可以指定多个进程文件进行合并
                    # 后期添加执行文件权限
                    if argc == 1:
                        self.print_error_info("command error ", "run")
                    else:
                        # 列出可执行文件列表
                        for file_name in command[1:]:
                            self.process_module.create_process(file_name)






















if __name__ == '__main__':
    os_controller = Controller()
    os_controller.execute()








