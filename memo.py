# coding=utf-8

import copy


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

    def getline(self,num):
        cont=self.content.split(';')
        return cont[num]

    def getonechar(self,num):
        if len(self.content)>num:
            return self.content[num]
        return False


class PageTable:  # 页表
    def __init__(self, max):

        self.table=[Virtual_Page() for i in range(max)]

    def delete(self, page_num):  # 清空页表中一页
        self.table[page_num].clr()

    def transform(self, page):

        if page < len(self.table):
            index = self.table[page].outaddress
            return index
        else:
            return -2


class Frame:    # 一个内存块
    def __init__(self, page_size=50, content=None, is_allocated=-1, pid=-1):
        self.is_allocated = is_allocated    # 该块是否分配
        self.pid = pid                      # 获得该块的进程pid
        self.content = content              # 块的内容
        self.page_size = page_size          # 一块的容量

    def clr(self):
        self.pid=-1
        self.is_allocated=-1
        self.content=None

    def getline(self,num):
        cont=self.content.split(';')
        return cont[num]

    def getonechar(self,num):
        if len(self.content)>num:
            return self.content[num]
        return False


class MemoryManager:
    def __init__(self,file_module,  page_size=50, command_size=10, physical_page=50, schedule='FIFO'):

        self.physical_memory = [Frame() for i in range(physical_page)]  # 物理内存
        self.ps = page_size                                             # 一页（块）的容量
        self.cs = command_size                                          # 一条指令的长度
        self.pn = physical_page                                         # 物理内存块数
        self.page_tables = {}                                           # 所有进程的页表
        self.schedule = schedule                                        # 调页策略
        self.allocated = 0                                              # 物理内存已经被分配的块数
        self.page_fault = 0                                             # 缺页发生次数
        self.page_access = 0                                            # 页访问次数
        self.physical_rate = [0]                                        # 内存使用率记录
        self.pidlist=[]                                                 # 未被满足的进程队列
        self.sizelist=[]                                                # 未被满足的需求块数队列
        self.file_module = file_module                                  # 文件模块接口

    def alloc(self, pid, size, filename):
        s = size
        if s+self.allocated > self.pn:
            self.pidlist.append(pid)
            self.sizelist.append(size)
            return -1
        else:
            self.allocated += size
            self.page_fault += size
            file_fcb = self.file_module.get_fcb(filename)  # 文件接口
            if file_fcb:
                disk_loc = file_fcb.disk_loc
                #print("disk_loc", disk_loc)
            else:
                print("UNFOUNDE FILE !!!!") # 返回错误码
                return
            psize=len(disk_loc)
            if pid in self.page_tables.keys():  # 已经有页表
                ptable = self.page_tables[pid]
            else:  # 创建页表
                ptable = PageTable(psize)
                self.page_tables[pid] = ptable
            for i in range(psize):
                ptable.table[i].outaddress = disk_loc[i]
            for i in range(self.pn):
                if self.physical_memory[i].is_allocated == -1:  # 该页未分配
                    self.physical_memory[i].pid = pid
                    self.physical_memory[i].is_allocated = 2
                    ptable.table[size-s].frame = i
                    ptable.table[size-s].valid=1
                    ptable.table[size - s].entry = 1
                    self.Fage(size - s, ptable)
                    self.physical_memory[i].content=self.file_module.disk.read_block(ptable.table[size-s].outaddress)
                    # print(self.physical_memory[i].content)
                    s = s-1
                if s == 0:
                    break
            return psize

    def free(self, pid):
        status = 0
        ptable=self.page_tables[pid]
        for i in range(len(ptable.table)):
            if ptable.table[i].valid == 1:
                status = 1
                b = ptable.table[i].frame
                if ptable.table[i].is_changed == 1:  # 有修改，写回外存,给块号和内容
                    self.file_module.disk.write_block(ptable.table[i].outaddress,
                            self.physical_memory[ptable.table[i].frame].content)
                self.physical_memory[b].clr()
                self.allocated=self.allocated-1

        ptable.table.clear()
        self.page_tables.pop(pid)
        if status == 0:
            return False
        return True

    def access(self, pid, address):
        self.page_access += 1
        page=10*int(address[0])+int(address[1])
        page_offset = 100*int(address[2])+10*int(address[3])+int(address[4])  # 页内偏移
        ptable = self.page_tables[pid]
        block = ptable.transform(page)
        if block == -2:
            print("ERROR ADDRESS !!!!")
            return -2
        elif block ==-1:    #缺页中断
            if self.schedule == 'LRU':
                block=self.LRU(ptable)
                self.Lage(page, ptable)
            elif self.schedule == 'FIFO':
                block=self.FIFO(ptable)
                self.Fage(page, ptable)
            self.physical_memory[block].is_allocated = 2
            self.physical_memory[block].content = self.file_module.disk.read_block(ptable.table[page].outaddress) # 接口获取页内信息
            ptable.table[page].frame=block
            ptable.table[page].valid = 1
            ptable.table[page].is_changed = -1
        elif block>=0:
            if self.schedule == 'LRU':
                self.Lage(block,ptable)
        return self.physical_memory[block].getonechar(page_offset)

    def page_PC(self, pid, address):
        print("address")
        print(address)
        self.page_access += 1
        page= int(address[:2])
        page_offset = 100*int(address[2])+10*int(address[3])+int(address[4])  # 页内偏移
        ptable = self.page_tables[pid]
        block = ptable.transform(page)
        if block == -2:
            print("ERROR ADDRESS !!!!")
            return
        elif block ==-1:  #缺页中断
            if self.schedule == 'LRU':
                block=self.LRU(ptable)
                self.Lage(page, ptable)
            elif self.schedule == 'FIFO':
                block=self.FIFO(ptable)
                self.Fage(page, ptable)
            self.physical_memory[block].is_allocated = 2
            self.physical_memory[block].content = self.file_module.disk.read_block(ptable.table[page][5])  # 接口获取页内信息
            ptable.table[page].frame = block
            ptable.table[page].valid = 1
            ptable.table[page].is_changed = -1
        elif block>=0:
            if self.schedule == 'LRU':
                self.Lage(block,ptable)
        return self.physical_memory[block].getline(page_offset)

    def Fage(self,idx,ptable):                      # 用于FIFO记录顺序
        for i in range(len(ptable.table)):
            if ptable.table[i].valid==1:
                ptable.table[i].entry += 1
            ptable.table[idx].entry = 0

    def Lage(self,idx,ptable):                         # 用于LRU记录顺序
        for i in range(len(ptable.table)):
            if ptable.table[i].vaild==1:
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