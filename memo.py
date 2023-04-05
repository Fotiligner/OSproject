# coding=utf-8

import copy


class PageTable:
    def __init__(self):
        # frame number represent the virtual page's location in physical memory
        # the table has a k_v as (page, [frame_number, validation])
        self.max_address = 10#接口获取最大页数,每页物理地址
        self.table = [[-1, -1, -1, -1, -1, None] for i in range(self.max_address)]#块号、状态位、入序、访问、修改位、外存地址
        for i in range(self.max_address):
            self.table[i][5] = "address"+str(i)

    def insert(self, page_num):  # allocated virtual page number
        self.table[page_num] = [None, -1]

    def delete(self, page_num):  # free virtual page number
        self.table.pop(page_num)

    def transform(self, page):

        if page < len(self.table):
            index = self.table[page][0]  # 块号
            return index
        else:
            return -2


class Page:
    def __init__(self, page_size=30, content=None, is_allocated=-1, pid=-1):
        self.is_allocated = is_allocated
        self.pid = pid
        self.content = content
        self.page_size = page_size

    def clr(self):
        self.pid=-1
        self.is_allocated=-1
        self.content=None

    def getline(self,num):
        cont=self.content.split(':')
        return cont[num]

    def getonechar(self,num):
        return self.content[num]

class MemoryManager:
    def __init__(self,  page_size=30, command_size=10, physical_page=50, schedule='FIFO'):

        # 是否分配、pid、字符串1-3
        self.physical_memory = [Page() for i in range(physical_page)]  #物理内存


        self.ps = page_size
        self.cs = command_size
        self.pn = physical_page
        self.page_tables = {}
        self.schedule = schedule

        self.physical_rate = [0]
        self.physical_history = [copy.deepcopy(self.physical_memory)]
        self.allocated = 0
        self.page_fault = 0
        self.page_access = 0
        self.pidlist=[]
        self.sizelist=[]

    def alloc(self, pid, size):  #进程创建时分配size个内存块

        return self.page_alloc(pid, size)



    def free(self, pid):

        return self.page_free(pid, aid)


    # command: dms


    def access(self, pid, address):

        self.page_access(pid, address)


    def page_alloc(self, pid, size,filename):
        s = size

        if s+self.allocated > self.pn:
            self.pidlist.append(pid)
            self.sizelist.append(size)
            return False
        else:
            file = ["13265", "41817", "79116", "778878"] #文件接口
            psize=len(file)
            if pid in self.page_tables.keys():  # 已经有页表
                ptable = self.page_tables[pid]
            else:  # 创建页表
                ptable = PageTable()
                self.page_tables[pid] = ptable
            for i in range(psize):
                ptable[i][5]=file[i]
            for i in range(self.pn):
                if self.physical_memory[i].is_allocated == -1:  # 该页未分配

                    self.physical_memory[i].pid = pid
                    self.physical_memory[i].is_allocated = 2

                    ptable[size-s][0]=i
                    ptable[size-s][1]=1
                    ptable[size - s][2] = 1
                    self.Fage(size - s, ptable)
                    #文件接口
                    self.physical_memory[i].content="content"+str(i)+"line1:line2:line3"
                    s = s-1


                if s == 0:
                    self.allocated += size
                    self.page_fault+=size
                    break

            return psize

    def page_free(self, pid):

        status = 0
        ptable=self.page_tables[pid]
        for i in range(ptable.size()):
            if ptable[i][1] == 1:
                status = 1
                b = ptable[i][0]
                #if ptable[i][4] == 1:  接口写回外存,给块号和内容

                self.physical_memory[b].clr()
                self.allocated=self.allocated-1

        ptable.clear()
        self.page_tables.pop(pid)

        if status == 0:
            return False
        return True

    def page_access(self, pid, address):

        self.page_access += 1
        page=10*int(address[0])+int(address[1])
        page_offset = 100*int(address[2])+10*int(address[3])+int(address[4])  # 页内偏移

        ptable = self.page_tables[pid]

        block = ptable.transform(page)
        if block == -2:
            print("ERROR ADDRESS !!!!")
            return
        elif block ==-1:
            if self.schedule == 'LRU':
                block=self.LRU(page, ptable)
                self.Lage(block, ptable)
            elif self.schedule == 'FIFO':
                block=self.FIFO(page, ptable)
                self.Fage(block, ptable)
            self.physical_memory[block].is_allocated = 2
            #文件接口
            self.physical_memory[block].content = "content"+str(block)+"line1:line2:line3" # 接口获取页内信息

        elif block>=0:

            if self.schedule == 'LRU':
                self.Lage(block,ptable)
        return self.physical_memory[block].getonechar(page_offset)

    def page_PC(self, pid, address):
        self.page_access += 1
        page=10*int(address[0])+int(address[1])
        page_offset = 100*int(address[2])+10*int(address[3])+int(address[4])  # 页内偏移

        ptable = self.page_tables[pid]

        block = ptable.transform(page)
        if block == -2:
            print("ERROR ADDRESS !!!!")
            return
        elif block ==-1:
            if self.schedule == 'LRU':
                block=self.LRU(page, ptable)
                self.Lage(block, ptable)
            elif self.schedule == 'FIFO':
                block=self.FIFO(page, ptable)
                self.Fage(block, ptable)
            self.physical_memory[block].is_allocated = 2
            #文件接口
            self.physical_memory[block].content = "content"+str(block)+"line1:line2:line3" # 接口获取页内信息

        elif block>=0:

            if self.schedule == 'LRU':
                self.Lage(block,ptable)
        return self.physical_memory[block].getline(page_offset)



    def Fage(self,idx,ptable):                      #用于FIFO记录顺序
        for i in range(ptable.size()):
            if ptable[i][1]==1:
                ptable[i][2]+=1
            ptable[idx][2] = 0

    def Lage(self,idx,ptable):                         #用于LRU记录顺序
        for i in range(ptable.size()):
            if ptable[i][1]==1:
                ptable[i][3]+=1
            ptable[idx][3] = 0

    def LRU(self, idx, ptable):

        max=0
        block=0
        for i in range(ptable.size()):
            if ptable[i][3]>max:
                max=ptable[i][3]
                block=i
        return block



    def FIFO(self, idx, ptable):

        max=0
        block=0
        for i in range(ptable.size()):
            if ptable[i][2]>max:
                max=ptable[i][2]
                block=i
        return block


