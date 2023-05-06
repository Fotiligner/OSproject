import msvcrt
import os
import prettytable
from enum import Enum

disk_path = os.path.abspath(r".") + "\\MYDISK"


class Ret_State(Enum):
    Success = 0
    Error_File_Exist = 1
    Error_File_Not_Exist = 2
    Error_Dir_Exist = 3
    Error_Dir_Not_Exist = 4
    Error_Path_Not_Exist = 5


class Disk:
    file_path = None  # 磁盘文件路径
    track_tot_num = 100  # 总磁道数
    sector_per_track = 10  # 每个磁道的扇区数
    blk_size = 60  # 块的大小，以字符为单位
    blk_tot_num = track_tot_num * sector_per_track  # 总块数
    size = blk_tot_num * blk_size  # 总大小，以字符为单位
    super_blk_num = 80  # 超级块的数目
    dir_base = super_blk_num  # 目录区开始的块号
    dir_blk_num = 120  # 目录区块数目
    data_base = dir_base + dir_blk_num  # 数据区开始块号
    data_blk_num = blk_tot_num - super_blk_num - dir_blk_num  # 数据区块数目
    bitmap = '0' * data_blk_num  # 位图是针对数据区的。0表示free,1表示占用

    def __init__(self, file_path):
        self.file_path = file_path

    def init_disk(self):
        """
        用于初始化磁盘文件
        :return:
        """
        with open(self.file_path, 'w') as f:
            buf = [' ' for _ in range(self.size)]
            buf[self.dir_base * self.blk_size] = '\0'
            buf = ''.join(buf)
            f.write(buf)

    def write_block(self, loc, buf):
        """
        以块为单位向磁盘文件指定位置写入内容
        :param loc: 磁盘指定位置
        :param buf: 需写入内容
        :return:
        """
        buf=buf.replace('\n','\1')  # 因为\n在文件中其实是\r\n，占两个偏移量，却只算一个字符
        with open(self.file_path, 'r+') as f:
            f.seek(loc * self.blk_size)
            if len(buf) < self.blk_size:
                f.write(buf)
            else:
                f.write(buf[:self.blk_size])

    def read_block(self, loc):
        """
        以块为单位从磁盘文件指定位置读出内容
        :param loc: 磁盘指定位置
        :return: 读出的内容
        """
        with open(self.file_path, 'r') as f:
            f.seek(loc * self.blk_size)
            buf=f.read(self.blk_size)
            return buf.replace('\1','\n')

    def display(self):
        """
        用于展示磁盘文件
        :return:
        """
        # a+模式下，刚打开时文件指针位置在文件结尾
        with open(self.file_path, 'a+') as f:
            size = f.tell()
            f.seek(0)
            track_no = 0
            sector_no = 0
            table_head = ['磁道号']
            table_head.extend(['扇区' + str(i) for i in range(self.sector_per_track)])
            table = prettytable.PrettyTable(table_head)
            row = [str(track_no)]
            cflag = 'y'
            while cflag == 'y' and f.tell() < size:
                if sector_no < self.sector_per_track:
                    row.append(repr(f.read(self.blk_size)))
                    sector_no = sector_no + 1
                else:
                    table.add_row(row)
                    sector_no = 0
                    track_no = track_no + 1
                    if track_no != 0 and track_no % 10 == 0:
                        print(table)
                        while True:
                            cflag = input('show more? [y/n]')
                            if cflag == 'y' or cflag == 'n':
                                break
                    row = [str(track_no)]
            if cflag == 'y':
                print(table)

    def write_super_blk(self):
        """
        写入超级块
        :return:
        """
        with open(self.file_path, 'r+') as f:
            buf = str(self.track_tot_num) + ' ' + \
                  str(self.sector_per_track) + ' ' + \
                  str(self.blk_size) + ' ' + \
                  self.bitmap
            f.write(buf)

    def read_super_blk(self):
        """
        读出超级块
        :return:
        """
        with open(self.file_path, 'r') as f:
            buf = f.read(self.super_blk_num * self.blk_size)
            info_list = buf.split()
            self.track_tot_num = int(info_list[0])
            self.sector_per_track = int(info_list[1])
            self.blk_size = int(info_list[2])
            self.bitmap = info_list[3]
        self.blk_tot_num = self.track_tot_num * self.sector_per_track
        self.size = self.blk_tot_num * self.blk_size
        self.blk_free_num = self.blk_tot_num

    def disk_alloc(self, num):
        """
        分配所需数目的磁盘块。
        :param num:所需数目。
        :return:分配的磁盘块的下标列表。
        """
        addr = []
        bitmap = list(self.bitmap)
        for i in range(self.data_blk_num):
            if bitmap[i] == '0':
                addr.append(i)
                if len(addr) >= num:
                    break
        if len(addr) >= num:
            for i in range(len(addr)):
                bitmap[addr[i]] = '1'
                self.bitmap = ''.join(bitmap)
                self.write_super_blk()
        else:
            addr = []
        return addr


class Dir:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.childs = []


class FCB:
    def __init__(self, name, disk_loc, size, auth):
        self.size = size  # 文件大小，以字符为单位，不包括结束符'\0'
        self.blk_num = int((size + 1) / Disk.blk_size) + 1
        self.name = name
        self.auth = auth
        self.disk_loc = disk_loc
        self.parent = None


class File_Module:
    root_path = '~'
    root_dir = Dir('~')
    work_path = root_path
    work_dir = root_dir

    def __init__(self, file_path):
        self.disk = Disk(file_path)
        if not os.path.isfile(file_path):
            self.disk.init_disk()
            self.disk.write_super_blk()
        self.read_dir_tree()

    def read_dir_tree(self):
        """
        从磁盘中读取目录树到文件系统
        :return:
        """
        dir_base = self.disk.dir_base
        blk_size = self.disk.blk_size
        with open(self.disk.file_path, 'r') as f:
            f.seek(dir_base * blk_size)
            buf = f.read(self.disk.dir_blk_num * blk_size)
        nodes = buf.split()
        dir_queue = [self.root_dir]
        index = 0
        while len(dir_queue) > 0:
            now_dir = dir_queue[0]
            if nodes[index] == '\0':
                dir_queue.pop(0)
            else:
                name = nodes[index]
                index = index + 1
                if nodes[index] == 'd':  # 目录
                    new_dir = Dir(name)
                    new_dir.parent = now_dir
                    now_dir.childs.append(new_dir)
                    dir_queue.append(new_dir)
                else:  # 文件
                    disk_loc = []
                    auth = nodes[index + 1]
                    size = int(nodes[index + 2])
                    blk_num = int(nodes[index + 3])
                    for i in range(blk_num):
                        disk_loc.append(int(nodes[index + 4 + i]))
                    new_fcb = FCB(name, disk_loc, size, auth)
                    new_fcb.parent = now_dir
                    now_dir.childs.append(new_fcb)
                    index = index + 3 + blk_num
            index = index + 1

    def write_dir_tree(self):
        """
        向磁盘中写入目录树。
        :return:
        """
        dir_queue = [self.root_dir]
        buf = ''
        while len(dir_queue) > 0:
            now_dir = dir_queue.pop(0)
            for c in now_dir.childs:
                if isinstance(c, Dir):
                    dir_queue.append(c)
                    buf = buf + c.name + ' d '
                else:
                    buf = buf + c.name + ' f '
                    buf = buf + c.auth + ' '
                    buf = buf + str(c.size) + ' '
                    buf = buf + str(c.blk_num) + ' '
                    for i in range(c.blk_num):
                        buf = buf + str(c.disk_loc[i]) + ' '
            buf = buf + ' \0 '
        dir_base = self.disk.dir_base
        blk_size = self.disk.blk_size
        with open(self.disk.file_path, 'r+') as f:
            f.seek(dir_base * blk_size)
            f.write(buf)

    def make_fcb(self, name, disk_addr, size, auth):
        """
        创建fcb。
        :param name: 文件名。
        :param disk_addr: 初始分配的磁盘块地址。
        :param size: 初始大小。
        :param auth: 初始权限。
        :return: 新创建的fcb节点。
        """
        new_fcb = FCB(name, disk_addr, size, auth)
        new_fcb.parent = self.work_dir
        self.work_dir.childs.append(new_fcb)
        self.write_dir_tree()
        return new_fcb

    def del_fcb(self, file_node):
        """
        删除fcb
        :param file_node:指定的fcb。
        :return:
        """
        bitmap = list(self.disk.bitmap)
        for loc in file_node.disk_loc:
            bitmap[loc] = '0'
        self.disk.bitmap = ''.join(bitmap)
        self.disk.write_super_blk()
        del file_node

    def get_fcb(self, file_name):
        """
        用于在工作目录寻找fcb节点。
        :param file_name:
        :return: 若成功，返回目标fcb节点；若失败，返回None
        """
        file_node = None
        for c in self.work_dir.childs:
            if isinstance(c, FCB) and c.name == file_name:
                file_node = c
        return file_node

    def make_dir(self, name):
        """
        创建目录。
        :param name:目录名。
        :return:
        """
        new_dir = Dir(name)
        new_dir.parent = self.work_dir
        self.work_dir.childs.append(new_dir)
        self.write_dir_tree()

    def del_dir(self, dir_node: Dir):
        """
        递归删除给定的目录节点。
        :param dir_node: 给定的目录节点。
        :return:
        """
        for c in dir_node.childs:
            if isinstance(c, Dir):
                self.del_dir(c)
            else:
                self.del_fcb(c)
        del dir_node
        self.write_dir_tree()

    def read_file(self, fcb):
        """
        读取文件内容。
        :param fcb:给定的fcb。
        :return: 返回文件内容，字符串类型。
        """
        buf = ''
        for i in fcb.disk_loc:
            buf = buf + self.disk.read_block(self.disk.data_base + i)
            if buf.find('\0') != -1:
                buf = buf[: buf.find('\0') + 1]
                break
        return buf[:-1]  # 去除末尾的结尾符

    def write_file(self, fcb, buf):
        """
        写入文件。
        :param fcb:所需写入的文件fcb节点。
        :param buf: 所需写入的内容。
        :return:
        """
        fcb.size = len(buf)
        buf = buf + '\0'
        new_blk_num = int((fcb.size + 1) / self.disk.blk_size) + 1
        if new_blk_num > fcb.blk_num:
            new_disk_loc = self.disk.disk_alloc(new_blk_num - fcb.blk_num)
            print('more alloc'+str(new_disk_loc))
            fcb.disk_loc.extend(new_disk_loc)
            fcb.blk_num = new_blk_num
        for i in range(fcb.blk_num):
            self.disk.write_block(self.disk.data_base + fcb.disk_loc[i], buf)
            print("buf:%s" % repr(buf))
            buf = buf[self.disk.blk_size:]

    def find_node(self, path):
        """
        返回路径所需结点。
        :param path: 文件路径。
        :return: 存在则返回节点，不存在则返回None。
        """
        nodes = path.split('/')
        now_dir = self.root_dir
        last_node = self.root_dir
        for i in range(1, len(nodes)):
            flag = False
            for c in now_dir.childs:
                if nodes[i] == c.name:
                    if i == len(nodes) - 1:
                        last_node = c
                    elif isinstance(c, Dir):
                        now_dir = c
                        flag = True
            if not flag:
                last_node = None
                break
        return last_node

    def mkdir(self, name):
        """
        为shell提供的命令，创建目录。
        :param name: 目录名。
        :return: 返回执行结果。
        """
        for c in self.work_dir.childs:
            if isinstance(c, Dir) and c.name == name:
                return Ret_State.Error_Dir_Exist
        self.make_dir(name)
        return Ret_State.Success

    def touch(self, name, size=0, auth='wr-'):
        """
        为shell提供的命令，创建文件。
        :param name: 文件名
        :param size: 文件大小，默认为0。
        :param auth: 文件权限，默认为读写。
        :return: 返回执行结果。
        """
        for c in self.work_dir.childs:
            if isinstance(c, FCB) and c.name == name:
                return Ret_State.Error_File_Exist
        disk_loc = self.disk.disk_alloc(int(size / self.disk.blk_size) + 1)
        fcb = None
        if len(disk_loc) != -1:
            fcb = self.make_fcb(name, disk_loc, size, auth)
        self.write_file(fcb, '')  # 添加文件结束符，以免这个块是脏的
        return Ret_State.Success

    def cd(self, dir_name):
        """
        进入目录。
        :param dir_name:所需进入的目录。
        :return: 返回执行结果。
        """
        if dir_name == '..':
            temp = self.work_path.split('/')
            self.work_path = '/'.join(temp[:-1])
            self.work_dir = self.find_node(self.work_path)
        elif dir_name == '~':
            self.work_path = self.root_path
            self.work_dir = self.root_dir
        else:
            flag = False
            for c in self.work_dir.childs:
                if isinstance(c, Dir) and c.name == dir_name:
                    self.work_path = self.work_path + '/' + c.name
                    self.work_dir = c
                    flag = True
            if not flag:
                return Ret_State.Error_File_Not_Exist
        return Ret_State.Success

    def ls(self):
        """
        展示当前目录下的文件。
        :return:返回文件名和文件类型的列表[[filename1,type1],[filename2,type2]..]
        """
        ret_list=[]
        for c in self.work_dir.childs:
            if isinstance(c, Dir):
                node=[c.name,"d"]
                print('\033[34m' + c.name + '\033[0m', end=' ')
            else:
                node=[c.name,"f"]
                print('\033[38m' + c.name + '\033[0m', end=' ')
            ret_list.append(node)
        print('')
        return ret_list

    def vi(self, name):
        """
        修改文件内容。
        :param name:文件名。
        :return: 返回执行结果。
        """
        file_node = None
        for c in self.work_dir.childs:
            if isinstance(c, FCB) and c.name == name:
                file_node = c
        if not file_node:
            return Ret_State.Error_File_Not_Exist
        buf = self.read_file(file_node)
        os.system('cls')
        for c in buf:
            msvcrt.putwch(c)

        while True:
            ch = msvcrt.getwch()
            if '\x20' <= ch <= '\x7e':  # 可显示字符
                buf = buf + ch
            elif ch == '\r' or ch == '\n':  # 换行
                buf = buf + '\n'
            elif ch == '\x08':  # 退格
                if len(buf) > 0:
                    buf = buf[:-1]
            elif ch == '\x11':  # 自定义退出键 ctrl + q
                msvcrt.putwch('\n')
                break
            os.system('cls')
            for c in buf:
                msvcrt.putwch(c)

        # print(repr(buf))
        self.write_file(file_node, buf)
        self.write_dir_tree()
        return Ret_State.Success

    def rm(self, name, mode=None):
        """
        删除目录或文件。
        :param name: 所需删除的目录名或文件名。
        :param mode: 默认删除文件。
            -r:删除目录
        :return: 返回执行结果
        """
        target_node = None
        if mode and mode.count('r') != 0:
            for c in self.work_dir.childs:
                if isinstance(c, Dir) and c.name == name:
                    target_node = c
            if not target_node:
                return Ret_State.Error_Dir_Not_Exist
            else:
                self.del_dir(target_node)
        else:
            for c in self.work_dir.childs:
                if isinstance(c, FCB) and c.name == name:
                    target_node = c
            if not target_node:
                return Ret_State.Error_File_Not_Exist
            else:
                self.del_fcb(target_node)
        self.work_dir.childs.remove(target_node)
        self.write_dir_tree()
        return Ret_State.Success


if __name__ == '__main__':
    file_system = File_Module(disk_path)
    active = True
    print(file_system.disk.read_block(201))
    while active:
        cmds = input(file_system.work_path + ':')
        cmd = cmds.split()
        ret_code = 0
        if len(cmd) == 0:
            continue
        if cmd[0] == 'exit':
            file_system.disk.write_super_blk()
            file_system.write_dir_tree()
            active = False
        elif cmd[0] == 'save':
            file_system.disk.write_super_blk()
            file_system.write_dir_tree()
        elif cmd[0] == 'display':
            file_system.disk.display()
        elif cmd[0] == 'ls':
            file_system.ls()
        elif cmd[0] == 'mkdir':
            file_system.mkdir(cmd[1])
        elif cmd[0] == 'touch':
            file_system.touch(cmd[1])
        elif cmd[0] == 'cd':
            file_system.cd(cmd[1])
        elif cmd[0] == 'wdt':
            file_system.write_dir_tree()
        elif cmd[0] == 'vi':
            file_system.vi(cmd[1])
        elif cmd[0] == 'init':
            file_system.disk.init_disk()
            file_system.disk.write_super_blk()
            file_system.del_dir(file_system.root_dir)
            file_system.root_dir = Dir('~')
            file_system.work_path = '~'
            file_system.read_dir_tree()
        elif cmd[0] == 'rdt':
            file_system.read_dir_tree()
        elif cmd[0] == 'rm':
            file_system.rm(mode=cmd[1], name=cmd[2])
        else:
            print('no such command')
