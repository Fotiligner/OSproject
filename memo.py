# coding=utf-8

import copy
from PyQt5.QtCore import pyqtSignal,QObject


class Virtual_Page:    # 一个虚页
    def __init__(self, frame=-1, valid=-1, entry=-1, visit=-1):
        self.valid = valid    # 该页是否有效
        self.frame = frame    # 内存块号
        self.entry = entry    # 入序
        self.visit = visit    # 访问
        self.is_changed = -1
        self.outaddress = None

    def clr(self):
        self.valid = -1    # 该页是否有效
        self.frame = -1    # 内存块号
        self.entry = -1     # 入序
        self.visit = -1     # 访问
        self.is_changed = -1    #修改位
        self.outaddress = None  #块号



class PageTable:  # 页表
    def __init__(self, max):
        self.table=[Virtual_Page() for i in range(max)]
        self.access=0
        self.fault=0

    def delete(self, page_num):  # 清空页表中一页
        self.table[page_num].clr()

    def transform(self, page):

        if page < len(self.table):
            index = self.table[page].frame
            return index
        else:
            return -2


class Frame:    # 一个内存块
    def __init__(self, page_size=60, content=None, is_allocated=-1, pid=-1):
        self.is_allocated = is_allocated    # 该块是否分配,1表示普通文件，2表示进程文件， -1是没分配
        self.pid = pid                      # 获得该块的进程pid
        self.filename = None
        self.content = content              # 块的内容
        self.page_size = page_size          # 一块的容量


    def clr(self):
        self.pid=-1
        self.is_allocated=-1
        self.content=None
        self.filename=None

    def getline(self,num):
        cont=self.content.split(';')
        return cont[num]

    def getonechar(self,num):
        if len(self.content)>num:
            return self.content[num]
        return False

    def write(self,offset, ch):
        num=int(offset)
        if len(self.content)>num:
            self.content = self.content[:num] + ch[0] + self.content[num + 1:]
            #self.content[num]=ch[0]
        else:
            print("WRITE WRONG !!!!") # 返回错误码


class MemoryManager(QObject):
    # 内存信号量，用来指示存储进程访存信息
    signal = pyqtSignal(PageTable, int)

    # 内存长期调度信号量，用来指示进程模块重新申请进程创建并完成长期调度
    signal_2 = pyqtSignal(str, int)

    def __init__(self,file_module,  page_size=60, command_size=10, physical_page=50, schedule="FIFO"):
        super().__init__()
        self.physical_memory = [Frame() for i in range(physical_page)]  # 物理内存
        self.ps = page_size                                               # 一页（块）的容量
        self.cs = command_size                                          # 一条指令的长度
        self.pn = physical_page                                         # 物理内存块数
        self.page_tables = {}                                           # 所有进程的页表
        self.ftables = {}                                               # 所有文件的页表
        self.schedule = schedule                                        # 调页策略
        self.allocated = 0                                              # 这个/pn是缺页率物理内存已经被分配的块数
        self.page_fault = 0                                             # 缺页中断发生次数
        self.page_access = 0                                            # 页访问次数
        self.physical_rate = 0                                          # 内存使用率记录
        self.filelist=[]                                                 # 未被满足的进程队列（文件名）
        self.sizelist=[]                                                # 未被满足的需求块数队列
        self.file_module = file_module                                  # 文件模块接口


    def change_FIFO(self):
        self.schedule = 'FIFO'

    def change_LRU(self):
        self.schedule = 'LRU'

    def search_file(self, filename):
        if filename in self.ftables.keys():
            return 1
        return -1

    def alloc(self, pid, size, filename, type):  # 给进程分配内存

        file_fcb = self.file_module.get_fcb(filename)  # 文件接口
        if file_fcb:
            disk_loc = file_fcb.disk_loc
        else:
            print("UNFOUNDE FILE !!!!")  # 返回错误码
            return
        psize = len(disk_loc)
        if psize < size:  # 分配的太多了,psize是进程虚拟内存空间，
            s = psize
        elif psize > 2 * size:  # 分配的太少了
            s = psize // 2 if psize < 30 else 15
        else:
            s = size
        if type==0 and s + self.allocated > self.pn:
            self.filelist.append(filename)
            self.sizelist.append(s)
            # 加个提醒输出
            return -1
        else:
            if type==0:
                self.allocated += s
            psize=s
            if pid in self.page_tables.keys():  # 已经有页表
                ptable = self.page_tables[pid]
            else:  # 创建页表
                ptable = PageTable(len(disk_loc))
                self.page_tables[pid] = ptable
            for i in range(len(disk_loc)):
                ptable.table[i].outaddress = disk_loc[i]
            for i in range(self.pn):
                if self.physical_memory[i].is_allocated == -1:  # 该页未分配
                    self.physical_memory[i].pid = pid
                    self.physical_memory[i].is_allocated = 2
                    ptable.table[psize - s].frame = i
                    ptable.table[psize - s].valid = 1
                    ptable.table[psize - s].entry = 1
                    self.Fage(psize - s, ptable)
                    self.physical_memory[i].content = self.file_module.disk.read_block(
                        self.file_module.disk.data_base + ptable.table[psize - s].outaddress)
                    s = s - 1
                    if s == 0:
                        break
            return psize

    def free(self, pid):    # 释放进程
        status = 0
        ptable=self.page_tables[pid]
        for i in range(len(ptable.table)):
            if ptable.table[i].valid == 1:
                status = 1
                b = ptable.table[i].frame
                if ptable.table[i].is_changed == 1:  # 有修改，写回外存,给块号和内容
                    self.file_module.disk.write_block(ptable.table[i].outaddress, self.physical_memory[b].content)
                self.physical_memory[b].clr()
                self.allocated=self.allocated-1

        self.signal.emit(ptable, pid)
        ptable.table.clear()
        self.page_tables.pop(pid)
        if status == 0:
            return False
        if self.filelist:
            if self.allocated+sizelist[0]<self.pn:
                #炳黔写信号量
                self.signal_2.emit(self.filelist[0], 1)
                self.filelist.pop(0)
                self.sizelist.pop(0)
        return True

    def access(self, pid, address):
        self.page_access += 1
        page=10*int(address[0])+int(address[1])
        page_offset = 100*int(address[2])+10*int(address[3])+int(address[4])  # 页内偏移
        ptable = self.page_tables[pid]
        ptable.access+=1
        block = ptable.transform(page)
        if block == -2:
            print("ERROR ADDRESS !!!!")
            return -2
        elif block ==-1:    #缺页中断
            ptable.fault+=1
            self.page_fault+=1
            if self.schedule == 'LRU':
                block=self.LRU(ptable)
            elif self.schedule == 'FIFO':
                block=self.FIFO(ptable)
            self.Lage(page, ptable)
            self.Fage(page, ptable)
            self.physical_memory[block].is_allocated = 2
            self.physical_memory[block].content = self.file_module.disk.read_block(self.file_module.disk.data_base + ptable.table[page].outaddress) # 接口获取页内信息
            ptable.table[page].frame=block
            ptable.table[page].valid = 1
            ptable.table[page].is_changed = -1
            print("缺页中断")
            return -1
        elif block>=0:
            self.Lage(page,ptable)
            return self.physical_memory[block].getonechar(page_offset)

    def page_PC(self, pid, address):
        self.page_access += 1
        page= int(address[:2])
        page_offset = 100*int(address[2])+10*int(address[3])+int(address[4])  # 页内偏移
        ptable = self.page_tables[pid]
        ptable.access+=1
        block = ptable.transform(page)
        if block == -2:
            print("ERROR ADDRESS !!!!")
            return
        elif block ==-1:  #缺页中断
            ptable.fault+=1
            self.page_fault+=1
            if self.schedule == 'LRU':
                block=self.LRU(ptable)
            elif self.schedule == 'FIFO':
                block=self.FIFO(ptable)
            self.Lage(page, ptable)
            self.Fage(page, ptable)
            self.physical_memory[block].is_allocated = 2
            self.physical_memory[block].content = self.file_module.disk.read_block(self.file_module.disk.data_base + ptable.table[page].outaddress)  # 接口获取页内信息
            ptable.table[page].frame = block
            ptable.table[page].valid = 1
            ptable.table[page].is_changed = -1
            return -1
        elif block>=0:
            if self.schedule == 'LRU':
                self.Lage(page,ptable)
            return self.physical_memory[block].getline(page_offset)


    def falloc(self, filename):  # 给普通文件分配内存
        s = 2
        file_fcb = self.file_module.get_fcb(filename)  # 文件接口
        if file_fcb:
            disk_loc = file_fcb.disk_loc
        else:
            print("UNFOUNDE FILE !!!!")  # 返回错误码
            return
        psize = len(disk_loc)
        a = 0
        if psize == 1:
            s=1
        if s+self.allocated > self.pn:
            self.filelist.append(filename)
            return -1
        else:
            self.allocated += s
            self.page_fault += s
            if filename in self.ftables.keys():  # 已经有页表
                ftable = self.ftables[filename]
            else:  # 创建页表
                ftable = PageTable(psize)
                self.ftables[filename] = ftable
            for i in range(psize):
                ftable.table[i].outaddress = disk_loc[i]
            for i in range(self.pn):
                if self.physical_memory[i].is_allocated == -1:  # 该页未分配
                    self.physical_memory[i].is_allocated = 1
                    self.physical_memory[i].filename=filename
                    ftable.table[a].frame = i
                    ftable.table[a].valid=1
                    ftable.table[a].entry = 1
                    self.Fage(a, ftable)
                    self.physical_memory[i].content=self.file_module.disk.read_block(self.file_module.disk.data_base + ftable.table[a].outaddress)
                    a = a + 1
                    if a == s:
                        break
            return 1

    def ffree(self, filename):    # 释放进程
        status = 0
        ftable=self.ftables[filename]
        for i in range(len(ftable.table)):
            if ftable.table[i].valid == 1:
                status = 1
                b = ftable.table[i].frame
                if ftable.table[i].is_changed == 1:  # 有修改，写回外存,给块号和内容
                    self.file_module.disk.write_block(self.file_module.disk.data_base + ftable.table[i].outaddress, self.physical_memory[b].content)
                self.physical_memory[b].clr()
                self.allocated=self.allocated-1
        ftable.table.clear()
        self.ftables.pop(filename)
        if status == 0:
            return False
        return True

    def faccess(self, filename, address):
        self.page_access += 1
        page=10*int(address[0])+int(address[1])
        page_offset = 100*int(address[2])+10*int(address[3])+int(address[4])  # 页内偏移
        ftable = self.ftables[filename]
        block = ftable.transform(page)
        if block == -2:
            print("ERROR ADDRESS !!!!")
            return -2
        elif block ==-1:    #缺页中断
            if self.schedule == 'LRU':
                block=self.LRU(ftable)
            elif self.schedule == 'FIFO':
                block=self.FIFO(ftable)
            self.Lage(page, ftable)
            self.Fage(page, ftable)
            self.physical_memory[block].is_allocated = 1
            self.physical_memory[block].content = self.file_module.disk.read_block(self.file_module.disk.data_base + ftable.table[page].outaddress) # 接口获取页内信息
            ftable.table[page].frame=block
            ftable.table[page].valid = 1
            ftable.table[page].is_changed = -1
            print("缺页中断")
            return -1
        elif block>=0:
            if self.schedule == 'LRU':
                self.Lage(page,ftable)
            return self.physical_memory[block].getonechar(page_offset)

    def fwrite(self, filename, address, ch):
        self.page_access += 1
        page=10*int(address[0])+int(address[1])
        page_offset = 100*int(address[2])+10*int(address[3])+int(address[4])  # 页内偏移
        ftable = self.ftables[filename]
        block = ftable.transform(page)
        if block == -2:
            print("ERROR ADDRESS !!!!")
            return -2
        elif block ==-1:    #缺页中断
            if self.schedule == 'LRU':
                block=self.LRU(ftable)
            elif self.schedule == 'FIFO':
                block=self.FIFO(ftable)
            self.Lage(page, ftable)
            self.Fage(page, ftable)
            self.physical_memory[block].is_allocated = 1
            self.physical_memory[block].content = self.file_module.disk.read_block(self.file_module.disk.data_base + ftable.table[page].outaddress) # 接口获取页内信息
            ftable.table[page].frame = block
            ftable.table[page].valid = 1

            print("缺页中断")
            return -1
        elif block>=0:
            self.Lage(page,ftable)
            ftable.table[page].valid = 1
            ftable.table[page].is_changed = 1
            self.physical_memory[block].write(page_offset, ch)
            return 1



    def Fage(self,idx,ptable):                      # 用于FIFO记录顺序
        for i in range(len(ptable.table)):
            if ptable.table[i].valid==1:
                ptable.table[i].entry += 1
            ptable.table[idx].entry = 0

    def Lage(self,idx,ptable):  # 用于LRU记录顺序
        for i in range(len(ptable.table)):
            if ptable.table[i].valid==1:
                ptable.table[i].visit+=1
            ptable.table[idx].visit = 0

    def LRU(self, ptable):
        max=0
        page=0
        for i in range(len(ptable.table)):
            if ptable.table[i].visit>max:
                max=ptable.table[i].visit
                page=i
        if ptable.table[page].is_changed == 1:
            self.file_module.disk.write_block(ptable.table[page].outaddress, self.physical_memory[ptable.table[page].frame].content)
        ptable.delete(page)
        return page

    def FIFO(self, ptable):
        max=0
        page=0
        for i in range(len(ptable.table)):
            if ptable.table[i].entry>max:
                max=ptable.table[i].entry
                page=i
        if ptable.table[page].is_changed == 1:
            self.file_module.disk.write_block(self.file_module.disk.database + ptable.table[page].outaddress,
                                              self.physical_memory[ptable.table[page].frame].content)
        ptable.delete(page)
        return page

if __name__ == '__main__':
    M=MemoryManager()