import os
import re
import datetime


class Command_Moduler:
    def __init__(self):
        self.print_info()

    def print_info(self):
        print('COS starts ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def get_command_list(self, user, path):  # , cwd, file_list):
        output_list = []
        try:
            # commands = input(cwd + '$ ').split(';')   # cwd就是当前路径,在真正的操作系统中会显示在命令行输入的开头
            commands_list = input('\033[1;36m' + user + ':' + '\033[34m' + path + '$ ').split(';')  # command用分号隔开各指令
        except BaseException:
            commands_list = []

        for command in commands_list:
            output_list.append(command.split())  # 中间多空格的情况可省略

        return output_list


if __name__ == '__main__':
    command_dealer = Command_Moduler()

    while True:
        command = command_dealer.get_command_list('hello', 'root/')
        print(command)
