import msvcrt, sys, os

disk_path = os.path.abspath(r"..") + "\\MYDISK"


class Disk:
    '''
    todo:
    '''
    file_path = None
    track_tot_num = 100
    sector_per_track = 10
    blk_size = 30
    blk_tot_num = track_tot_num * sector_per_track
    size = blk_tot_num * blk_size
    blk_free_num = blk_tot_num
    super_blk_num = 80
    dir_base = super_blk_num
    dir_blk_num = 120  # 目录区
    data_base = dir_base + dir_blk_num
    data_blk_num = blk_tot_num - super_blk_num - dir_blk_num
    # 位图是针对数据区的
    bitmap = '0' * data_blk_num  # 0表示free,1表示占用

    def __init__(self, file_path):
        self.file_path = file_path

    def init_disk(self):
        with open(self.file_path, 'w') as f:
            buf = [' ' for _ in range(self.size)]
            buf[self.dir_base * self.blk_size] = '\0'
            buf = ''.join(buf)
            f.write(buf)

    def write_block(self, loc, buf):
        with open(self.file_path, 'r+') as f:
            f.seek(loc * self.blk_size)
            if len(buf)<self.blk_size:
                f.write(buf)
            else:
                f.write(buf[:self.blk_size])

    def read_block(self, loc):
        with open(self.file_path, 'r') as f:
            f.seek(loc * self.blk_size)
            return f.read(self.blk_size)

    # def read_blk2end(self, loc):
    #     buf = self.read_block(loc)
    #     while buf.count('\0') == 0:
    #         loc = loc + 1
    #         buf = buf + self.read_block(loc)
    #     return buf
    #
    # def write_blk2end(self,loc,buf):
    #     size=len(buf)
    #     while size>0:
    #         self.write_block(loc,buf)
    #         loc=loc+1
    #         buf=buf[self.blk_size:]
    #         size=size-self.blk_size



    def display(self):
        # a+模式下，刚打开时文件指针位置在文件结尾
        with open(self.file_path, 'a+') as f:
            size = f.tell()
            f.seek(0)
            track_no = 0
            sector_no = 0
            print('%2d' % track_no, end=': ')
            while f.tell() < size:
                if sector_no < self.sector_per_track:
                    print('%2d' % sector_no, end=': ')
                    print(repr(f.read(self.blk_size)), end='|')
                    sector_no = sector_no + 1
                else:
                    sector_no = 0
                    track_no = track_no + 1
                    print('\n%d' % track_no, end=':\n')
            print('\n')

    def display_info(self):
        print('track_tot_num:', self.track_tot_num)
        print('sector_per_track:', self.sector_per_track)
        print('blk_size:', self.blk_size)

    def write_super_blk(self):
        with open(self.file_path, 'r+') as f:
            buf = str(self.track_tot_num) + ' ' + \
                  str(self.sector_per_track) + ' ' + \
                  str(self.blk_size) + ' ' + \
                  self.bitmap
            f.write(buf)

    def read_super_blk(self):
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
        '''
        todo:
        :param num:
        :return:
        '''
        addr=[]
        bitmap=list(self.bitmap)
        for i in range(self.data_blk_num):
            if bitmap[i] == '0':
                addr.append(i)
                if len(addr) >= num:
                    break
        if len(addr) >= num:
            for i in range(len(addr)):
                bitmap[addr[i]]='1'
                self.bitmap=''.join(bitmap)
                if i == len(addr)-1:
                    self.write_block(self.data_base+addr[i],'\0')
        else:
            addr=[]
        return addr


class Dir:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.childs = []


class FCB:
    def __init__(self, name, disk_loc, size, auth):
        self.size = size
        self.blk_num = int(size / Disk.blk_size) + 1
        self.name = name
        self.auth = auth
        self.disk_loc = disk_loc
        self.parent = None


class FileSystem:
    root_path = '~'
    root_dir = Dir('~')
    work_path = root_path
    work_dir = root_dir

    def __init__(self, file_path):
        self.disk = Disk(file_path)

    def read_dir_tree(self):
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
                    size = int(nodes[index + 1])
                    for i in range(int(size / self.disk.blk_size) + 1):
                        disk_loc.append(int(nodes[index+2+i]))
                    auth = nodes[index + 3]
                    new_fcb = FCB(name, disk_loc, size, auth)
                    new_fcb.parent = now_dir
                    now_dir.childs.append(new_fcb)
                    index = index + 3
            index = index + 1

    def write_dir_tree(self):
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
                    buf = buf + str(c.size) + ' '
                    for i in range(int(c.size/self.disk.blk_size)+1):
                        buf = buf + str(c.disk_loc[i])+' '
                    buf = buf + c.auth + ' '
            buf = buf + ' \0 '
        dir_base = self.disk.dir_base
        blk_size = self.disk.blk_size
        with open(self.disk.file_path, 'r+') as f:
            f.seek(dir_base * blk_size)
            f.write(buf)

    def make_fcb(self, name, disk_addr, size, auth):
        new_fcb = FCB(name, disk_addr, size, auth)
        new_fcb.parent = self.work_dir
        self.work_dir.childs.append(new_fcb)

    def make_dir(self, name):
        new_dir = Dir(name)
        new_dir.parent = self.work_dir
        self.work_dir.childs.append(new_dir)

    def read_file(self,fcb):
        buf=''
        for i in fcb.disk_loc:
            buf=buf+self.disk.read_block(self.disk.data_base+i)
        return buf

    def write_file(self,fcb,buf):
        size=len(buf)
        new_blk_num=int(size/self.disk.blk_size)+1
        if new_blk_num > fcb.blk_num:
            fcb.disk_loc.extend(self.disk.disk_alloc(new_blk_num-fcb.blk_num))
            fcb.blk_num=new_blk_num
        for i in range(fcb.blk_num):
            self.disk.write_block(self.disk.data_base+fcb.disk_loc[i],buf)
            buf = buf[self.blk_size:]

    def find_node(self, path):
        '''
        返回路径所需结点
        :param path: 文件路径
        :return: 存在则返回节点，不存在则返回None
        '''
        nodes = path.split('\\')
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
        '''
        todo:
        对于是否能够创建目录的异常检测，即目录区是否足够
        :param name:
        :return:
        '''
        self.make_dir(name)

    def touch(self, name, size=0, auth='wrx'):
        disk_loc = self.disk.disk_alloc(int(size / self.disk.blk_size) + 1)
        if len(disk_loc) != -1:
            self.make_fcb(name, disk_loc, size, auth)

    def cd(self, dir_name):
        if dir_name == '..':
            temp = self.work_path.split('\\')
            self.work_path = '\\'.join(temp[:-1])
            self.work_dir = self.find_node(self.work_path)
        elif dir_name == '~':
            self.work_path = self.root_path
            self.work_dir = self.root_dir
        else:
            for c in self.work_dir.childs:
                if isinstance(c, Dir) and c.name == dir_name:
                    self.work_path = self.work_path + '\\' + c.name
                    self.work_dir = c

    def ls(self):
        for c in self.work_dir.childs:
            print(c.name, end=' ')
        print('')

    def vi(self,name):
        file_node=None
        for c in self.work_dir.childs:
            if isinstance(c,FCB) and c.name == name:
                file_node=c
        buf=self.disk.read_blk2end(file_node.disk_loc+self.disk.data_base)
        for c in buf:
            msvcrt.putwch(c)
        while True:
            ch = msvcrt.getwch()
            if ch == '\r':
                msvcrt.putwch('\n')
            elif ch == '\x08':
                if buf:
                    buf = buf[:-1]
                    msvcrt.putwch('\b')
                    msvcrt.putwch(' ')
                    msvcrt.putwch('\b')
            elif ch == '\x1b':
                break

            else:
                buf = buf + ch
                msvcrt.putwch(ch)
        print('buf:%s'%buf)
        self.disk.write_blk2end(file_node.disk_loc+self.disk.data_base,buf)



if __name__ == '__main__':
    file_system = FileSystem(disk_path)
    file_system.read_dir_tree()
    active = True
    while active:
        cmds = input(file_system.work_path + ':')
        cmd = cmds.split()
        if len(cmd) == 0:
            continue
        if cmd[0] == 'exit':
            file_system.disk.write_super_blk()
            file_system.write_dir_tree()
            active = False
        elif cmd[0]=='save':
            file_system.disk.write_super_blk()
            file_system.write_dir_tree()
        elif cmd[0] == 'display':
            file_system.disk.display()
        elif cmd[0] == 'display_info':
            file_system.disk.display_info()
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
            file_system.read_dir_tree()
        else:
            print('no such command')
