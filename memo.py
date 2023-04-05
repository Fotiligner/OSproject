# coding=utf-8
import numpy as np
import seaborn
import pandas as pd
import matplotlib.pyplot as plt
import copy


class PageTable:
    def __init__(self):
        # frame number represent the virtual page's location in physical memory
        # the table has a k_v as (page, [frame_number, validation])
        self.max_address = 10#接口获取最大页数,每页物理地址
        #outadd =
        #self.table = {}
        self.table = [[-1, -1, -1, -1, -1, None] for i in range(self.max_address)]#块号、状态位、入序、访问、修改位、外存地址
        for i in range(self.max_address):
            self.table[i][5] = "address"+str(i)

    def insert(self, page_num):  # allocated virtual page number
        self.table[page_num] = [None, -1]

    def delete(self, page_num):  # free virtual page number
        self.table.pop(page_num)

    def transform(self, address, page_size):
        """
        :param address: the visited relative address
        :param page_size: size of each page
        :return: if find valid,return the physical_page_number, else return -1
        """
        idx = address // page_size  # 页表偏移量
        if idx < len(self.table):
            index = self.table[idx][0]  # 块号
            return index
        else:
            return -2

    # when the virtual page being schedule in/out the physical memory
    def modify(self, idx, fnum, valid):
        """
        :param idx: which virtual page to modify
        :param fnum: the frame number to add
        :param valid: if this virtual page in physical memory. = 1 in/ -1 not
        """
        if valid == 1:
            self.table[idx] = [fnum, valid]
        else:
            self.table[idx][1] = valid

class Page:
    def __init__(self, page_size=None, content=None, is_allocated=-1, pid=-1):
        self.is_allocated = is_allocated
        self.pid = pid
        self.content = content
        self.page_size = page_size

    def getline(self,num):
        cont=self.content.split(':')
        return cont[num]

    def getonechar(self,num):

class MemoryManager:
    def __init__(self,  page_size=30, command_size=10, page_number=255,
                 physical_page=50, schedule='FIFO'):
        """
        :param page_size: the size of each page(useful when mode == 'p')
        :param page_number: the total page num of the virtual memory
        :param physical_page: the total page num of the physical memory
        """

        # record the virtual memory

        self.virtual_memory = np.array([Page() for i in range(page_number)])  #255个【1024，-1，0】
        # 是否分配、pid、字符串1-3
        self.physical_memory = [[-1, -1, None, None, None] for i in range(physical_page)]  #50个[-1,0,None, None,None]
        # for LRU algorithm, the first one is the Least Recent Used, the
        # last is recently visited
        self.schedule_queue = []
        self.ps = page_size
        self.cs = command_size
        self.vn = page_number
        self.pn = physical_page  # the number of physical page
        # record the page table of all the process, has a k_v as (pid:
        # PageTable)
        self.page_tables = {}
        self.schedule = schedule

        self.pidlist = []
        self.sizelist = []
        self.physical_rate = [0]
        self.physical_history = [copy.deepcopy(self.physical_memory)]
        self.allocated = 0
        self.page_fault = 0
        self.page_access = 0

    # load executable file into memory
    # if failed, report error and return -1
    def alloc(self, pid, size):

        return self.page_alloc(pid, size)


    # pid and aid not all be None
    # return True or False, if failed, report error
    def free(self, pid, aid=None):

        return self.page_free(pid, aid)


    # command: dms


    def access(self, pid, address):

        self.page_access(pid, address)


    # if the memory has the page structure
    def page_alloc(self, pid, size):
        s = size
        if s+self.allocated > self.pn:
            self.pidlist.append(pid)
            self.sizelist.append(size)
        else:
            for i in range(self.pn):
                if self.physical_memory[i][0] == -1:  # the page is empty
                    self.physical_memory[i][1] = pid
                    self.physical_memory[i][0] = 1
                    s = s-1
                    if pid in self.page_tables.keys():  # the process has a page table
                        ptable = self.page_tables[pid]
                    else:  # the process does not have a page table
                        ptable = PageTable()  # create one
                        self.page_tables[pid] = ptable

                if s == 0:
                    self.allocated += size
                    break




    # find the aiming page and delete it from page table
    def page_free(self, pid):

        status = 0
        ptable=self.page_tables[pid]
        for i in range(ptable.size()):
            if ptable[i][1] == 1:
                status = 1
                b = ptable[i][0]
                #if ptable[i][4] == 1:  接口写回外存

                self.physical_memory[b] = [-1, -1, None, None,None]
                self.allocated=self.allocated-1

        ptable.clear()
        self.page_tables.pop(pid)

        if status == 0:
            # print("error! That memory not Found.")
            return False
        return True

    def page_access(self, pid, address):
        '''
        :param pid: the process to visit
        :param address: the relative address of the process
        '''
        self.page_access += 1  # plus 1 every time you access a page
        page_offset = address % self.ps  # the offset within the page

        ptable = self.page_tables[pid]  # get the page table to be visited
        # calculate the exact page to be visited
        block = ptable.transform(address, self.ps)
        idx = address/self.ps
        if block == -2:
            print("ERROR ADDRESS !!!!")
            return
        elif block ==-1:
            if self.allocated<self.pn:
                for i in range(self.pn):
                    if self.physical_memory[i][0] == 1 & self.physical_memory[i][1] == pid:
                        block=i
                        self.allocated += 1
                        break;
            elif self.schedule == 'LRU':
                block=self.LRU(idx, ptable)
                self.Lage(block, ptable)
            elif self.schedule == 'FIFO':
                block=self.FIFO(idx, ptable)
                self.Fage(block, ptable)
            self.physical_memory[block][0] = 2
            self.physical_memory[block][2:4] = [str(i) + 'a', str(i) + 'b', str(i) + 'c']  # 接口获取页内信息

        elif block>=0:

            if self.schedule == 'LRU':
                self.Lage(block,ptable)
        offset = address % self.ps % self.cs + 2
        return self.physical_memory[block][offset]

    def Fage(self,idx,ptable):                      #用于FIFO记录顺序
        ptable[idx][2]=0
        for i in range(ptable.size()):
            if ptable[i][1]==1&i!=idx:
                ptable[i][2]+=1

    def Lage(self,idx,ptable):                         #用于LRU记录顺序
        ptable[idx][3]=0
        for i in range(ptable.size()):
            if ptable[i][1]==1&i!=idx:
                ptable[i][3]+=1

    def LRU(self, idx, ptable):
        """
        :param idx: the virtual page to be switched in physical memory
        :param ptable: the ptable records the virtual page
        """
        max=0
        block=0
        for i in range(ptable.size()):
            if ptable[i][3]>max:
                max=ptable[i][3]
                block=i
        return block



    def FIFO(self, idx, ptable):
        """
        :param idx: the virtual page to be switched in physical memory
        :param ptable: the ptable records the virtual page
        :return:
        """
        max=0
        block=0
        for i in range(ptable.size()):
            if ptable[i][2]>max:
                max=ptable[i][2]
                block=i
        return block


