import threading
from threading import Event, Thread, current_thread
import time
import random
import Process.Scheduler
import Process.Process_Utils
import copy

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from IO_Module import IO_Module



from IO_Module import IO_Module

# 初始化甘特图绘图函数
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class PCB:
    def __init__(self, pid, start_time,file_name, parent_pid=None,
                 child_pid=None,
                 already_time=None,
                 waiting_time=None, priority=None,
                 page_allocated=[], pc_end=None, content="",
                 ):
        self.pid = pid
        self.parent_pid = parent_pid
        self.child_pid = child_pid

        self.pc = "00000"   # 指向当前的执行代码行数，实际上可以用逻辑地址来代替
        # self.pc_end =  pc_end   # 结束地址

        self.status = "ready"
        self.priority = priority
        self.start_time = start_time  # 进程创建的时间
        self.waiting_time = 0    # 指进程在非运行自身的时间内经过的时间
        self.already_time = 0    # 指在进程真正运行的时间内已经运行的时间
        self.command_queue = []
        self.page_allocated = 0     # 虚拟内存分配的页数

        self.command_already_time = 0
        self.final_time = 0
        self.last_time = 0

        # 新增甘特图辅助列表，记录进程所有running状态的开始和结束情况
        self.gantt_list = []    # 数字列表，结果为一个开始时间一个结束时间,后期考虑添加

        #  新加进来这个 进程附属的文件名  用于fork函数  到时候内存申请使用的
        self.file_name = file_name

    def update(self, pid, start_time,file_name ,parent_pid=None,
                 child_pid=None,
                 already_time=None,
                 waiting_time=None, priority=None,
                 page_allocated=[], pc_end=None, content=""):
        self.pid = pid
        self.parent_pid = parent_pid
        self.child_pid = child_pid

        self.pc = "00000"   # 指向当前的执行代码行数，实际上可以用逻辑地址来代替

        self.status = "ready"
        self.priority = priority
        self.start_time = start_time  # 进程创建的时间
        self.waiting_time = 0    # 指进程在非运行自身的时间内经过的时间
        self.already_time = 0    # 指在进程真正运行的时间内已经运行的时间
        self.command_queue = []
        self.page_allocated = 0     # 虚拟内存分配的页数
        self.last_time = 0
        self.gantt_list = []

        self.file_name = file_name

    def show_pcb(self):
        print("在" + str(current_time) + "时刻创建了进程" + str(self.pid) + ",优先级为" + str(
            self.priority) + ",pc_end=" + str(self.pc_end) +", pc= "+str(self.pc))


e = Event()
current_time = 0   # 全局时钟
clock_running = True

def clock():  #  模拟时钟
    global current_time
    while clock_running:
        e.clear()   # 置为False
        time.sleep(0.5)
        current_time +=1
        e.set()     # 置为True
        time.sleep(0.5)

clocking = Thread(target=clock)
clocking.setDaemon(True)
clocking.start()  # 创建一个计数器线程

# event类似于信号量，赋值True和False

class Process_Module(threading.Thread, Process.Scheduler.ProcessScheduler, Process.Process_Utils.Process_Utils):  # 多继承
    def __init__(self, memory_module):
        #初始化父类ProcessScheduler
        Process.Scheduler.ProcessScheduler.__init__(self)
        threading.Thread.__init__(self)

        self.pcb_pool = []   # 整体pcb池，存储所有pcb
        self.running_pid = -1
        self.current_pid = 0   # 计数，指向当前pcb_pool的最大进程编号
        self.executing = False
        #这两个需要移到Scheduler里
        #self.schedule_type = args.schedule_type   # "multi_feedback_queue"  "single_queue"
        #self.schedule_algorithm = args.schedule_algorithm  # 仅在single_queue下生效

        self.io_module = IO_Module('./device.json')  ##之前是../device.json也就是上一级目录, 但是他明明在同级目录下的   Nauhc
        self.memory_module = memory_module

        self.page_per_process = 3
        self.command_per_page = 5

        self.chd_pid = 0


    # def init_process_module(self):

    def create_process(self, file_name, priority):
        if file_name.split('.')[1] == "exe": # 判断是否为可执行文件
            # 注意，创建进程的时候，是使用生产者消费者模型的，这里要调用内存模块的接口
            # 需要内存返回首地址,内存模块负责将file_name 传递给文件模块，然后回传

            # my_aid = self.memory_manager.alloc(
            #                 pid=self.cur_pid, size=int(file['size']))

            # 理论上创建进程时进程已经具有了逻辑页号和地址上限

            type, self.current_pid = self.getCurrentpid()  # 从success里调到外，可能有bug

            alloc_output = self.memory_module.alloc(self.current_pid, self.page_per_process, file_name)
            # 文件总页数， 指令行数， 返回值（错误码）

            if alloc_output >= 0: # 内存分配成功
                if(type == "new"): #如果是个新PCB,也就是老PCB都没有终止
                    self.pcb_pool.append(PCB(self.current_pid, parent_pid=-1, \
                                             child_pid=-1, priority=priority, start_time=current_time, \
                                             page_allocated=alloc_output,file_name= file_name))  #pc_end=2 , content = "cpu 2;output printer asdfasdf 3;cpu 3"))   # 暂时
                    self.ready_queue.append(self.current_pid)  # 存储指向pcb_pool下标的代码
                elif(type == "old"):
                    self.pcb_pool[self.loc_pid_inPool(self.current_pid)].update(self.current_pid, parent_pid=-1, \
                                             child_pid=-1, priority=priority, start_time=current_time, \
                                             page_allocated=alloc_output,file_name=file_name) #pc_end=1 , content = "cpu 2;cpu 3")
                    self.ready_queue.append(self.current_pid)  # 存储指向pcb_pool下标的代码
            else: # 内存分配不成功
                if alloc_output == -2:
                    print("error" + " the file does not exist")
                elif alloc_output == -1:
                    print("error" + " not enough room for pages of this process")
        else:
            print(f"[error] {file_name} is not an executable file")

    def add_pc(self, pc):
        pc_front = pc[:2]
        pc_back = pc[2:]

        pc_front = int(pc_front)
        pc_back = int(pc_back)

        pc_back += 1
        if pc_back % self.command_per_page == 0:
            pc_back = "000"
            pc_front += 1
            pc_front = "0" * (2 - len(str(pc_front))) + str(pc_front)
        else:
            pc_back = "0" * (3 - len(str(pc_back))) + str(pc_back)
            pc_front = pc[:2]
        return pc_front + pc_back

    def set_start(self, running_pid, time):   # 更新对应进程gantt_list
        if running_pid != -1:
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].gantt_list.append([time])   # 重新开始一个时间

    def set_end(self, running_pid, time):
        if running_pid != -1:
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].gantt_list[-1].append(time)   # 逻辑不一样，记录ending的时间

    def run(self):  # 模拟进程调度程序,run是threading.Thread中的重载函数
        target = True   # 进程时钟控制辅助指标
        while self.executing:
            if e.is_set() and target:  #正常运行
                target = False
                #self.print_status()
                if(self.running_pid == -1):  # 如果当前没有进程,先调度一个进程再开始运行
                    self.scheduler("no running")
                    self.set_start(self.running_pid, current_time)
                if(self.running_pid != -1):
                    ## 向内存中要一段代码的位置 传递过去pid和程序计数器pc  返回一个字符串  需要提前定义好一行指令的大小
                    ## 下面这行代码会放入内存取地址的内容
                    command = self.memory_module.page_PC(self.running_pid, self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc).split()

                    # 这里需要判断是否缺页，缺页则直接中断，放入waiting_list中，同时在一个周期之后从waiting调入ready状态，其实当前时刻内存是已经将缺的页数放入了
                    # 如何确定fork无限不停止的问题？
                    # fork维持当前的pc指针？创建新的程序进入内存？执行fork指令之后所有的新指令

                    print(command)
                    # command = self.pcb_pool[self.loc_pid_inPool(self.running_pid)].command_queue[self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc]   # 从内存中获得的file 4.2 暂时修改了下
                    self.command_running(command,self.running_pid)

                # 注意，不可以在io中断的时候更新pc，不然这里就会直接释放进程，顺序问题一定要搞清楚
                # io遍历和io进程的问题

                device_output = self.io_module.IO_run()
                # print(device_output)
                if len(device_output) > 0:
                    print(device_output)

                for return_dict in device_output:   # 当前时刻返回的device信息，用来指示已完成IO的进程信息以及传输的数据
                    print("在" + str(current_time) + "时刻" + "进程" + str(
                        self.pcb_pool[self.loc_pid_inPool(return_dict["pid"])].pid) + "完成IO")
                    self.pcb_pool[self.loc_pid_inPool(return_dict["pid"])].pc = self.add_pc(self.pcb_pool[self.loc_pid_inPool(return_dict["pid"])].pc)
                    self.pcb_pool[self.loc_pid_inPool(return_dict['pid'])].status = "ready"
                    self.ready_queue.append(return_dict['pid'])  # 完成io的程序从waiting到ready
                    self.waiting_queue.remove(return_dict['pid'])

                    # if(self.pcb_pool[self.loc_pid_inPool(return_dict['pid'])].pc <= self.pcb_pool[self.loc_pid_inPool(return_dict['pid'])].pc_end):
                    #     self.pcb_pool[self.loc_pid_inPool(return_dict['pid'])].status = "ready"
                    #     self.ready_queue.append(return_dict['pid'])   # 完成io的程序从waiting到ready
                    #     self.waiting_queue.remove(return_dict['pid'])
                    # else:
                    #     print("在" + str(current_time) + "时刻" + "进程" + str(
                    #         self.pcb_pool[self.loc_pid_inPool(return_dict["pid"])].pid) + "运行结束")
                    #     self.waiting_queue.remove(return_dict['pid'])
                    #     self.pcb_pool[self.loc_pid_inPool(return_dict['pid'])].final_time = current_time
                    #     self.pcb_pool[self.loc_pid_inPool(return_dict['pid'])].status = "terminated" #把当前进程改成中止

                # 因为中断会将running_pid设为-1，因此首先判断running pid是否为-1

                if(self.running_pid != -1):
                    print("在"+str(current_time)+"时刻"+"进程"+str(self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pid)+"运行中")
                    #self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc += 1
                # elif self.running_pid != -1:
                #     print("在"+str(current_time)+"时刻"+"进程"+str(self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pid)+"运行结束")
                #     self.pcb_pool[self.loc_pid_inPool(self.running_pid)].final_time = current_time
                #     self.process_over()     # 释放进程部分的指令

            elif not e.is_set():           # 进入中断
                e.wait()  # 正在阻塞状态,当event变为True时就激活
                #print("一个原子时间结束,启动调度算法")
                self.set_end(self.running_pid, current_time)
                self.scheduler("time")  # 进程抢占在这里完成
                self.set_start(self.running_pid, current_time)
                target = True

    def io_interrupt(self, type):
        print("产生" + type + "中断")
        self.pcb_pool[self.loc_pid_inPool(self.running_pid)].status = "waiting"   # 更改PCB状态
        self.waiting_queue.append(self.running_pid)   # 更改waiting队列状态
        self.set_end(self.running_pid, current_time)  # 更新结束时间
        self.running_pid = -1   # 将当前的running 进程取消状态，便于之后scheduler
    def command_running(self, command,running_pid):
        if command[0] == "cpu":   # 普通cpu时间，理论上只可能是cpu 1
            time = int(command[1])
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].already_time += 1  # 进程进度加一（already_time）
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].command_already_time += 1   # 针对cpu指令完成时间的测试

            if self.pcb_pool[self.loc_pid_inPool(self.running_pid)].command_already_time == time:
                self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc = self.add_pc(self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc)   # 指令行数增加，指向下一条指令
                self.pcb_pool[self.loc_pid_inPool(self.running_pid)].command_already_time = 0
            return
        elif command[0] == "output" or command[0] == "input":  # output + device_name + content + time
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].already_time += 1
            # 防止结尾的中断指令被识别为进程结束，中断的pc+1在回传的时候完成
            # self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc += 1  # 指令行数增加，指向下一条指令

            self.io_module.add_request(source_pid=self.running_pid, target_device=command[1], IO_time=int(command[3]), content=command[2],\
                                       priority_num=1, is_disk=False, file_path=None, rw_state=None)
            self.io_interrupt("device_io")
        elif command[0] == "access":
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].already_time += 1  # 进程进度加一（already_time）
            address_content = self.memory_module.access(self.running_pid, command[1])

            if address_content == -2: # 地址出错
                print('\033[1;31m' + "访问的地址越界！" + '\033[0m')
            else:
                print("访问的地址内容为：" + address_content)
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc = self.add_pc(
                self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc)  # 指令行数增加，指向下一条指令
        elif command[0] == "read" or command[0] == "write":
            pass
        elif command[0] == "fork":

            type, self.chd_pid = self.getCurrentpid()  # 从success里调到外，可能有bug
            if running_pid != -1:
                name_of_file =self.pcb_pool[self.loc_pid_inPool(self.running_pid)].file_name
            alloc_output = self.memory_module.alloc(self.chd_pid, self.page_per_process,name_of_file )
            if alloc_output >= 0:  # 内存分配成功
                #先创建一个pcb 随便一个pcb  然后深层复制
                fork_pcb = PCB(self.chd_pid, parent_pid=-1, \
                                             child_pid=-1, priority=1, start_time=current_time, \
                                             page_allocated=alloc_output,file_name= name_of_file)
                fork_pcb = copy.deepcopy(self.pcb_pool[self.loc_pid_inPool(self.running_pid)])
                # 复制来的pcb需要对进程id进行更改  pc数也要加1  父进程就是当前正在运行的pid
                self.fork_pcb.pid = self.chd_pid
                self.fork_pcb.pc +=1
                self.fork_pcb.parent_pid = self.running_pid
                #  添加到pcb池子中去  并且也要放到ready队列之中
                self.pcb_pool.append(fork_pcb)
                self.ready_queue.append(self.chd_pid)
                #  将父进程 也就是running_pid 的子进程进行修改
                self.pcb_pool[self.loc_pid_inPool(self.running_pid)].child_pid = self.chd_pid
            else:# 内存分配不成功
                if alloc_output == -2:
                    print("error" + " the file does not exist")
                elif alloc_output == -1:
                    print("error" + " not enough room for pages of this process")
                pass

        elif command[0] == "exit":
            if self.running_pid != -1:
                self.set_end(self.running_pid, current_time)
                print("在" + str(current_time) + "时刻" + "进程" + str(
                    self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pid) + "运行结束")
                self.pcb_pool[self.loc_pid_inPool(self.running_pid)].final_time = current_time
                self.process_over()  # 释放进程部分的指令

    def print_status(self):
        print("========")
        print("current_time: " + str(current_time))
        print("current_running: " + str(self.running_pid))
        print("ready queue: " + str(self.ready_queue))
        print("pcb_pool: [",end='')
        for i in self.pcb_pool:
            print(i.pid,end=' ')
        print("]")
        print("========")
    ## 进程正常终止的函数 应该不存在设备队列的问题所以没有释放设备
    def process_over(self):
        if self.running_pid in self.ready_queue:
            self.ready_queue.remove(self.running_pid)
        if self.running_pid in self.waiting_queue:
            self.waiting_queue.remove(self.running_pid)
        self.memory_module.free(self.running_pid)
        ## 遍历当前进程的所有子进程并把子进程的父进程改成init进程
        self.pcb_pool[self.loc_pid_inPool(self.running_pid)].status = "terminated" #把当前进程改成中止
        self.running_pid = -1  # 把当前运行的改为没有

        self.gantt_graph()

    ## 使用kill命令终止的函数 感觉其实也没有太多变化
    def kill_process(self,pid):   # 注意，不一定是将当前运行的进程kill掉，所以要区别running_pid的使用情况
        if pid in self.ready_queue:
            self.ready_queue.remove(pid)
        if pid in self.waiting_queue:
            self.waiting_queue.remove(pid)
        ## 释放内存 大概只要传过去pid就可以
        self.memory_module.free(pid)

        ## 释放设备队列
        self.io_module.release_process_request(pid)
        self.pcb_pool[self.loc_pid_inPool(pid)].status = "terminated" #把当前进程改成中止
        ## 遍历当前进程的所有子进程并把子进程的父进程改成init进程

        if self.running_pid == pid:   # 在running kill的时候直接停止当前的running_pid
            self.running_pid = -1  # 把当前运行的改为没有

        print("在" + str(current_time) + "时刻" + "进程" + str(pid) + "被杀死")

    def gantt_graph(self):
        plt.figure(figsize=(20, 14), dpi=100)     ## 定义一个图像窗口
        plt.title("Facos进程运行甘特图", fontsize=30)   ## 标题  后面的fontsize字体大小

        color = ['b', 'g', 'r', 'y', 'c', 'm', 'k']

        for index, process in enumerate(self.pcb_pool):
            for span in process.gantt_list:       ##   self.gantt_list = []
                plt.barh(index, width=span[1] - span[0] + 1, left=span[0], color=color[index])

        # labels = [''] * len(add[0])
        # # 设置刻度字体大小
        # plt.xticks(range(50), rotation=0, fontsize=20)
        # plt.yticks(m, fontsize=20)
        # labels = ['t0', 't1', 't2']
        # # 图例绘制
        # patches = [mpatches.Patch(color=color[i], label="{:s}".format(labels[i])) for i in range(len(add[0]))]
        # plt.legend(handles=patches, loc=4, fontsize=25)
        # plt.ylabel(" ", fontsize=30)
        # # XY轴标签
        # plt.xlabel("运行时间/s", fontsize=30)
        plt.savefig("test.png")

    def create_process_test(self, priority=None, alloc_output=None):
        type, self.current_pid = self.getCurrentpid()  # 从success里调到外，可能有bug
        if (type == "new"):  # 如果是个新PCB,也就是老PCB都没有终止
            self.pcb_pool.append(PCB(self.current_pid, parent_pid=-1, \
                                     child_pid=-1, priority=priority, start_time=current_time, \
                                     page_allocated=alloc_output))  # pc_end=2 , content = "cpu 2;output printer asdfasdf 3;cpu 3"))   # 暂时
            self.ready_queue.append(self.current_pid)  # 存储指向pcb_pool下标的代码
        elif (type == "old"):
            self.pcb_pool[self.loc_pid_inPool(self.current_pid)].update(self.current_pid, parent_pid=-1, \
                                                                        child_pid=-1, priority=priority,
                                                                        start_time=current_time, \
                                                                        page_allocated=alloc_output)  # pc_end=1 , content = "cpu 2;cpu 3")
            self.ready_queue.append(self.current_pid)  # 存储指向pcb_pool下标的代码


if __name__ == '__main__':
    e = Event()  # 默认False
    Thread(target=clock).start()  # 创建一个计数器线程

    P = Process_Module()             # 创建manager
    P.setDaemon(True)
    P.start()                     # P作为线程开始运行
    ## 这里暂时把create_process当成创建进程用了
    target = True

    while 1:

        if e.is_set() and target:
            target = False
            if current_time in [2]: #创建1优先级的进程
                P.create_process("a.exe",1)
                continue
            if current_time in [6]:
                P.create_process("a.exe", 2) #创建2优先级的进程
                continue
            if current_time >40:
                break
        elif not e.is_set():
            target=True