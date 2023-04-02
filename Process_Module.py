import threading
from threading import Event, Thread, current_thread
import time
import random
import Scheduler
import Process_Utils
import copy

from IO_Module import IO_Module



from IO_Module import IO_Module

class PCB:
    def __init__(self, pid, start_time, parent_pid=None,
                 child_pid=None,
                 already_time=None,
                 waiting_time=None, priority=None,
                 page_allocated=[], pc_end=None, content=""
                 ):
        self.pid = pid
        self.parent_pid = parent_pid
        self.child_pid = child_pid

        self.pc = 0   # 指向当前的执行代码行数，实际上可以用逻辑地址来代替
        self.pc_end =  pc_end   # 结束地址

        self.status = "ready"
        self.priority = priority
        self.start_time = start_time  # 进程创建的时间
        self.waiting_time = 0    # 指进程在非运行自身的时间内经过的时间
        self.already_time = 0    # 指在进程真正运行的时间内已经运行的时间
        self.command_queue = []
        self.page_allocated = 0     # 虚拟内存分配的页数


        # self.last_time = last_time
        # self.event = None
        # self.content=content
        # # todo 消息队列指针/信号量
        # self.size=size
        # self.next_ptr= None
        # self.pc_time = 0
        # self.PSW=PSW
        # self.user_ptr=user_ptr
        self.last_time = 0

        # 有一个问题，last time 是没有办法通过这种方式提前预知和计算的，因为要时刻从内存中进行读取
        for command in content.split(';'):
            info = command.split( )
            info[1] = int(info[1])
            self.last_time += info[1]
            self.command_queue.append(info)
        #print(self.command_queue)
            self.show_pcb()

        # self.processor=processor
        # self.nice = 1
        # self.type = type #区分是CPU密集型还是IO型, 0代表CPU, 1代表IO

    def update(self, pid, start_time, parent_pid=None,
                 child_pid=None,
                 already_time=None,
                 waiting_time=None, priority=None,
                 page_allocated=[], pc_end=None, content=""):
        self.pid = pid
        self.parent_pid = parent_pid
        self.child_pid = child_pid

        self.pc = 0   # 指向当前的执行代码行数，实际上可以用逻辑地址来代替
        self.pc_end =  pc_end   # 结束地址

        self.status = "ready"
        self.priority = priority
        self.start_time = start_time  # 进程创建的时间
        self.waiting_time = 0    # 指进程在非运行自身的时间内经过的时间
        self.already_time = 0    # 指在进程真正运行的时间内已经运行的时间
        self.command_queue = []
        self.page_allocated = 0     # 虚拟内存分配的页数


        # self.last_time = last_time
        # self.event = None
        # self.content=content
        # # todo 消息队列指针/信号量
        # self.size=size
        # self.next_ptr= None
        # self.pc_time = 0
        # self.PSW=PSW
        # self.user_ptr=user_ptr
        self.last_time = 0

        # 有一个问题，last time 是没有办法通过这种方式提前预知和计算的，因为要时刻从内存中进行读取
        for command in content.split(';'):
            info = command.split( )
            info[1] = int(info[1])
            self.last_time += info[1]
            self.command_queue.append(info)
        #print(self.command_queue)
            self.show_pcb()

        # self.processor=processor
        # self.nice = 1
        # self.type = type #区分是CPU密集型还是IO型, 0代表CPU, 1代表IO
    def show_pcb(self):
        print("在" + str(current_time) + "时刻创建了进程" + str(self.pid) + "优先级为" + str(
            self.priority) + ",pc_end=" + str(self.pc_end) +", pc= "+str(self.pc))



current_time = 0   # 全局时钟

def clock():  #  模拟时钟
    global current_time
    while 1:
        e.clear()   # 置为False
        time.sleep(0.25)
        current_time +=1
        e.set()     # 置为True
        time.sleep(0.25)


# event类似于信号量，赋值True和False


class Process_Module(threading.Thread, Scheduler.ProcessScheduler, Process_Utils.Process_Utils):  # 多继承
    def __init__(self):
        #初始化父类ProcessScheduler
        Scheduler.ProcessScheduler.__init__(self)
        threading.Thread.__init__(self)

        self.pcb_pool = []   # 整体pcb池，存储所有pcb
        self.running_pid = -1
        self.current_pid = 0   # 计数，指向当前pcb_pool的最大进程编号
        #这两个需要移到Scheduler里
        #self.schedule_type = args.schedule_type   # "multi_feedback_queue"  "single_queue"
        #self.schedule_algorithm = args.schedule_algorithm  # 仅在single_queue下生效

        self.io_module = IO_Module('device.json')


    # def init_process_module(self):

    def create_process(self, file_name, priority):
        if file_name.split('.')[1] == "exe": # 判断是否为可执行文件
            # 注意，创建进程的时候，是使用生产者消费者模型的，这里要调用内存模块的接口
            # 需要内存返回首地址,内存模块负责将file_name 传递给文件模块，然后回传

            # my_aid = self.memory_manager.alloc(
            #                 pid=self.cur_pid, size=int(file['size']))


            # 理论上创建进程时进程已经具有了逻辑页号和地址上限

            success = True
            if success: # 内存分配成功
                type, self.current_pid = self.getCurrentpid()
                if(type == "new"): #如果是个新PCB,也就是老PCB都没有终止
                    self.pcb_pool.append(PCB(self.current_pid, parent_pid=-1, \
                                             child_pid=-1, priority=priority, start_time=current_time, \
                                             page_allocated=[], pc_end=4 , content = "cpu 1;cpu 1"))   # 暂时
                    self.ready_queue.append(self.current_pid)  # 存储指向pcb_pool下标的代码
                elif(type == "old"):
                    self.pcb_pool[self.loc_pid_inPool(self.current_pid)].update(self.current_pid, parent_pid=-1, \
                                             child_pid=-1, priority=priority, start_time=current_time, \
                                             page_allocated=[], pc_end=4 , content = "cpu 1;cpu 1")
                    self.ready_queue.append(self.current_pid)  # 存储指向pcb_pool下标的代码
            else: # 内存分配不成功
                pass
        else:
            print(f"[error] {file_name} is not an executable file")



    def run(self):  # 模拟进程调度程序,run是threading.Thread中的重载函数
        target = True   # 进程时钟控制辅助指标
        while 1:
            if e.is_set() and target:  #正常运行
                target = False
                #self.print_status()
                if(self.running_pid == -1):  # 如果当前没有进程,先调度一个进程再开始运行
                    self.scheduler("no running")
                if(self.running_pid != -1):
                    ## 向内存中要一段代码的位置 传递过去pid和程序计数器pc  返回一个字符串  需要提前定义好一行指令的大小
                    command = "cpu 5"   # 从内存中获得的file 4.2 暂时修改了下
                    self.command_running(command.split())
                    if(self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc <= self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc_end):
                        print("在"+str(current_time)+"时刻"+"进程"+str(self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pid)+"运行中")
                        #self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc += 1
                    else:
                        print("在"+str(current_time)+"时刻"+"进程"+str(self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pid)+"结束")
                        self.process_over()     # 释放进程部分的指令

            elif not e.is_set():           # 进入中断
                e.wait()  # 正在阻塞状态,当event变为True时就激活
                #print("一个原子时间结束,启动调度算法")
                self.scheduler("time")  # 进程抢占在这里完成
                target = True

    def io_interrupt(self, type):
        print("产生" + type + "中断")
        self.pcb_pool[self.loc_pid_inPool(self.running_pid)].status = "waiting"   # 更改PCB状态
        self.waiting_queue.append(self.running_pid)   # 更改waiting队列状态
        self.running_pid = -1   # 将当前的running 进程取消状态，便于之后scheduler
    def command_running(self, command):
        if command[0] == "cpu":   # 普通cpu时间，理论上只可能是cpu 1
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].already_time += 1  # 进程进度加一（already_time）
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc += 1   # 指令行数增加，指向下一条指令
            return
        elif command[0] == "output" or command[0] == "input":  # output + device_name + content + time
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].already_time += 1
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pc += 1  # 指令行数增加，指向下一条指令

            self.io_module.add_request(source_pid=self.running_pid, target_device=command[1], IO_time=command[3], content=command[2],\
                                       priority_num=1, is_disk=False, file_path=None, rw_state=None)
            self.io_interrupt("device_io")
        elif command[0] == "access":
            pass
        elif command[0] == "read" or command[0] == "write":
            pass
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
        ## 释放内存 大概只要传过去self.running_pid就可以

        ## 遍历当前进程的所有子进程并把子进程的父进程改成init进程
        self.pcb_pool[self.loc_pid_inPool(self.running_pid)].status = "terminated" #把当前进程改成中止
        self.running_pid = -1  # 把当前运行的改为没有

    ## 使用kill命令终止的函数 感觉其实也没有太多变化
    def kill_process(self,pid):
        if pid in self.ready_queue:
            self.ready_queue.remove(pid)
        if pid in self.waiting_queue:
            self.waiting_queue.remove(pid)
        ## 释放内存 大概只要传过去self.running_pid就可以
        ## 释放进程队列  大概只要传过去self.running_pid就可以
        self.pcb_pool[self.loc_pid_inPool(self.running_pid)].status = "terminated" #把当前进程改成中止
        ## 遍历当前进程的所有子进程并把子进程的父进程改成init进程
        self.running_pid = -1  # 把当前运行的改为没有

if __name__ == '__main__':
    e = Event()  # 默认False
    Thread(target=clock).start()  # 创建一个计数器线程

    P = Process_Module()             # 创建manager
    P.setDaemon(True)
    P.start()                     # P作为线程开始运行
    ## 这里暂时把create_process当成创建进程用了
    for i in range(0,3):
        time.sleep(1)
        P.create_process("a.exe",1)
    time.sleep(1)
    P.create_process("b.exe",2)
    time.sleep(2)
    P.create_process("b.exe",2)
