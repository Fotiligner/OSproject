import threading
from threading import Event, Thread, current_thread
import time
import random

from IO_Module import IO_Module

class PCB:
    def __init__(self, pid, start_time, parent_pid=None,
                 child_pid=None,
                 already_time=None,
                 waiting_time=None, priority=None,
                 page_allocated=[], pc_end=None
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
        # for command in content.split(';'):
        #     info = command.split( )
        #     info[1] = int(info[1])
        #     self.command_queue.append(info)
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

class Process_Module(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.pcb_pool = []   # 整体pcb池，存储所有pcb
        self.running_pid = -1
        self.current_pid = 0   # 计数，指向当前pcb_pool的最大进程编号

        self.schedule_type = args.schedule_type   # "multi_feedback_queue"  "single_queue"
        self.schedule_algorithm = args.schedule_algorithm  # 仅在single_queue下生效

        self.ready_queue = []
        self.waiting_queue = []

    # def init_process_module(self):

    def create_process(self, file_name):
        if file_name.split('.')[1] == "exe": # 判断是否为可执行文件
            # 注意，创建进程的时候，是使用生产者消费者模型的，这里要调用内存模块的接口
            # 需要内存返回首地址,内存模块负责将file_name 传递给文件模块，然后回传

            # my_aid = self.memory_manager.alloc(
            #                 pid=self.cur_pid, size=int(file['size']))

            success = True
            if success: # 内存分配成功
                self.pcb_pool.append(PCB(pid=self.current_pid, parent_pid=-1, \
                                         child_pid=-1, priority=1, start_time=current_time, \
                                         page_allocated=[], pc_end=5))   # 暂时
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
                print(current_time)
                if(self.current_running != -1):
                    if self.pcb_list[self.current_running].pc!= len(self.pcb_list[self.current_running].command_queue):
                        pass
                elif(self.current_running == -1):
                    b=self.scheduler()
            elif not e.is_set():           # 进入中断
                e.wait()  # 正在阻塞状态,当event变为True时就激活
                target = True

    def create_process(self, file):
        a = PCB.pcb(file.pid,
                    "cpu 5;cpu 10",
                    current_time,
                    "cpu")
        self.pcb_list.append(a)
        #self.current_running = a.pid

    def scheduler(self):
        # print("进入了Scheduler")
        if len(self.pcb_list) > 0:
            for i in self.pcb_list:
                self.current_running = i.pid
        return 0


if __name__ == '__main__':
    e = Event()  # 默认False
    Thread(target=clock).start()  # 创建一个计数器线程

    P = Process_Module()             # 创建manager
    P.setDaemon(True)
    P.start()                     # P作为线程开始运行
