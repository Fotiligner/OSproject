# coding=utf-8

import copy


class PageTable:  # 页表
    def __init__(self, max):

        self.table = [[-1, -1, -1, -1, -1, None] for i in range(max)]
        # 块号、状态位、入序、访问、修改位、外存地址

    def delete(self, page_num):  # 清空页表中一页
        self.table[page_num]=[-1, -1, -1, -1, -1, None]

    def transform(self, page):

        if page < len(self.table):
            index = self.table[page][0]  # 块号
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
                print("disk_loc", disk_loc)
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
                ptable.table[i][5]=disk_loc[i]
            for i in range(self.pn):
                if self.physical_memory[i].is_allocated == -1:  # 该页未分配
                    self.physical_memory[i].pid = pid
                    self.physical_memory[i].is_allocated = 2
                    ptable.table[size-s][0]=i
                    ptable.table[size-s][1]=1
                    ptable.table[size - s][2] = 1
                    self.Fage(size - s, ptable)
                    self.physical_memory[i].content=self.file_module.disk.read_block(ptable.table[size-s][5])
                    # print(self.physical_memory[i].content)
                    s = s-1
                if s == 0:
                    break
            return psize

    def free(self, pid):
        status = 0
        ptable=self.page_tables[pid]
        for i in range(len(ptable.table)):
            if ptable.table[i][1] == 1:
                status = 1
                b = ptable.table[i][0]
                if ptable.table[i][4] == 1:  # 有修改，写回外存,给块号和内容
                    self.file_module.disk.write_block(ptable.table[i][0],
                            self.physical_memory[ptable.table[i][0]].content)
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
            self.physical_memory[block].content = self.file_module.disk.read_block(ptable.table[page][5]) # 接口获取页内信息
            ptable.table[page][0]=block
            ptable.table[page][1] = 1
            ptable.table[page][4] = -1
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
            ptable.table[page][0] = block
            ptable.table[page][1] = 1
            ptable.table[page][4] = -1
        elif block>=0:
            if self.schedule == 'LRU':
                self.Lage(block,ptable)
        return self.physical_memory[block].getline(page_offset)

    def Fage(self,idx,ptable):                      # 用于FIFO记录顺序
        for i in range(len(ptable.table)):
            if ptable.table[i][1]==1:
                ptable.table[i][2]+=1
            ptable.table[idx][2] = 0

    def Lage(self,idx,ptable):                         # 用于LRU记录顺序
        for i in range(len(ptable.table)):
            if ptable.table[i][1]==1:
                ptable.table[i][3]+=1
            ptable.table[idx][3] = 0

    def LRU(self, ptable):
        max=0
        page=0
        for i in range(len(ptable.table)):
            if ptable.table[i][3]>max:
                max=ptable.table[i][3]
                page=i
        if ptable.table[page][4]==1:
            self.file_module.disk.write_block(ptable.table[page][0], self.physical_memory[ptable.table[page][0]].content)
        ptable.delete(page)
        return page

    def FIFO(self, ptable):
        max=0
        page=0
        for i in range(len(ptable.table)):
            if ptable.table[i][2]>max:
                max=ptable.table[i][2]
                page=i
        if ptable.table[page][4] == 1:
            self.file_module.disk.write_block(self.file_module.disk.database + ptable.table[page][0], \
                                              self.physical_memory[ptable.table[page][0]].content)
        ptable.delete(page)
        return page

if __name__ == '__main__':
    M=MemoryManager()