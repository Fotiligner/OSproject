import threading
from threading import Event, Thread, current_thread
import time
import random
import Scheduler
import Process_Utils
import copy



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
        self.pc_end = pc_end  # 结束地址

        self.status = "ready"
        self.priority = priority
        self.start_time = start_time
        self.waiting_time = 0
        self.already_time = 0
        self.command_queue = []
        self.page_allocated = page_allocated


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
        for command in content.split(';'):
            info = command.split( )
            info[1] = int(info[1])
            self.last_time += info[1]
            self.command_queue.append(info)
        #print(self.command_queue)

        print("在"+str(current_time)+"时刻创建了进程"+str(self.pid) + ", last_time: "+str(self.last_time) + "优先级为" + str(self.priority))
        # self.processor=processor
        # self.nice = 1
        # self.type = type #区分是CPU密集型还是IO型, 0代表CPU, 1代表IO

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


class Process_Module(threading.Thread, Scheduler.ProcessScheduler, Process_Utils.Process_Utils):
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


    # def init_process_module(self):

    def create_process_a(self, file_name, priority):
        if file_name.split('.')[1] == "exe": # 判断是否为可执行文件
            # 注意，创建进程的时候，是使用生产者消费者模型的，这里要调用内存模块的接口
            # 需要内存返回首地址,内存模块负责将file_name 传递给文件模块，然后回传

            # my_aid = self.memory_manager.alloc(
            #                 pid=self.cur_pid, size=int(file['size']))

            success = True
            if success: # 内存分配成功
                self.pcb_pool.append(PCB(pid=self.current_pid, parent_pid=-1, \
                                         child_pid=-1, priority=priority, start_time=current_time, \
                                         page_allocated=[], pc_end=5 , content = "cpu 5;cpu 5"))   # 暂时
                self.ready_queue.append(self.current_pid)  # 存储指向pcb_pool下标的代码

                self.current_pid += 1
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
                    #print("无进程使用,启动调度算法")
                    b=self.scheduler("no running")
                if(self.running_pid != -1):

                    ## 向内存中要一段代码的位置 传递过去pid和程序计数器  返回一个字符串  需要提前定义好一行指令的大小
                    #if self.pcb_list[self.running_pid].pc!= len(self.pcb_list[self.running_pid].command_queue):
                    #    pass
                    #print("当前进程下标" + str(self.loc_pid_inPool(self.running_pid)))
                    if(self.pcb_pool[self.loc_pid_inPool(self.running_pid)].already_time < self.pcb_pool[self.loc_pid_inPool(self.running_pid)].last_time-1):
                        print("在"+str(current_time)+"时刻"+"进程"+str(self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pid)+"运行中")
                        self.pcb_pool[self.loc_pid_inPool(self.running_pid)].already_time+=1
                    else:
                        print("在"+str(current_time)+"时刻"+"进程"+str(self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pid)+"运行中")
                        self.pcb_pool[self.loc_pid_inPool(self.running_pid)].already_time += 1 #执行完最后一部分代码
                        self.process_over()

            elif not e.is_set():           # 进入中断
                e.wait()  # 正在阻塞状态,当event变为True时就激活
                #print("一个原子时间结束,启动调度算法")
                self.scheduler("time")
                target = True

    def print_status(self):
        print("========")
        print("current_time: " + str(current_time))
        print("current_running: " + str(self.running_pid))
        print("ready queue: " + str(self.ready_queue))
        print("pcb_pool" + str(self.pcb_pool))
        print("========")

    def process_over(self):
        self.pcb_pool[self.loc_pid_inPool(self.running_pid)].already_time += 1
        self.running_pid = -1 # 把当前运行的改为没有
        ## 释放内存

if __name__ == '__main__':
    e = Event()  # 默认False
    Thread(target=clock).start()  # 创建一个计数器线程

    P = Process_Module()             # 创建manager
    P.setDaemon(True)
    P.start()                     # P作为线程开始运行
    ## 这里暂时把create_process当成创建进程用了
    for i in range(0,3):
        time.sleep(1)
        P.create_process_a("a.exe",1)

    time.sleep(1)
    P.create_process_a("b.exe",2)
