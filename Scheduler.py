import Process_Utils
#专门负责进程调度的类
class ProcessScheduler(Process_Utils.Process_Utils):
    def __init__(self):
        self.schedule_type="Preempting"
        self.ready_queue = []
        self.waiting_queue = []
        self.time_slot = 3        #代表时间片为三个单位时间
        self.current_time_slot_count = 0

    def scheduler(self, type):
        #print("Scheduler")
        if (self.schedule_type == "FCFS"):   # 因为没有抢占，如果是中断的话，在那个时刻会从running转为waiting
            #FCFS只在没有运行程序的时候才会被调度
            if type == "no running" and len(self.ready_queue) != 0:
                self.Scheduler_FCFS()
        # 时间片轮转
        # 若时间片没有用完，进程就结束，那么立即调度就绪队列中的队首进程运行，并启动一个新的时间片。
        elif (self.schedule_type == "RR"):
            self.Scheduler_RR()

        # 抢占优先级 在no running 和time情况下都会被调用
        elif (self.schedule_type == "Preempting"):
            self.Scheduler_preempting()

    #FCFS算法
    def Scheduler_FCFS(self):
        print("正在使用FCFS")
        if len(self.ready_queue) != 0:
            self.running_pid = self.ready_queue[0]
            self.pcb_pool[self.loc_pid_inPool(self.running_pid)].status = "running"
            self.ready_queue.remove(self.running_pid)
            return self.running_pid

        else:
            return -1

    ##  等七哥写
    ##  等七哥写
    def Scheduler_RR(self):
        #print("发生RR")
        if len(self.ready_queue) != 0:
            self.running_pid = self.ready_queue[0]
            self.pcb_pool[self.running_pid].status = "running"

            #self.pcb_pool[self.running_pid].already_time += 1

            #print(self.pcb_pool[self.running_pid].already_time)
            #print(self.pcb_pool[self.running_pid].last_time)

            if(self.pcb_pool[self.running_pid].already_time < self.pcb_pool[self.running_pid].last_time):
                if ((self.pcb_pool[self.running_pid].already_time+1) % self.time_slot == 0 ) :
                    self.ready_queue.remove(self.running_pid)
                    self.ready_queue.append(self.running_pid)
                    return self.running_pid
            if((self.pcb_pool[self.running_pid].already_time+1) >= self.pcb_pool[self.running_pid].last_time):
                #print("asdasd")
                self.ready_queue.remove(self.running_pid)
                return self.running_pid

            #return self.running_pid
        else:
            return -1


    ##抢占优先级算法
    def Scheduler_preempting(self):
        if len(self.ready_queue) != 0:
            if(self.running_pid == -1):
                self.running_pid = self.ready_queue[0]
                self.pcb_pool[self.loc_pid_inPool(self.running_pid)].status = "running"
                self.ready_queue.remove(self.running_pid)
            else:
                #从ready_queue选出最高优先级
                highest_priority_pcb = self.pcb_pool[self.loc_pid_inPool(self.ready_queue[0])]
                for i in self.ready_queue:
                    if(self.pcb_pool[self.loc_pid_inPool(i)].priority>
                            self.pcb_pool[self.loc_pid_inPool(highest_priority_pcb.pid)].priority):
                        highest_priority_pcb = self.pcb_pool[self.loc_pid_inPool(i)]
                #print("存在"+str(highest_priority_pcb))
                #如果等待队列里最高优先级的大于正在运行的优先级
                if(highest_priority_pcb.priority > self.pcb_pool[self.loc_pid_inPool(self.running_pid)].priority):
                    print("发生抢占 此时ready里最高的优先级:"+ str(highest_priority_pcb.priority) + " 正在运行的优先级:" + str(self.pcb_pool[self.loc_pid_inPool(self.running_pid)].priority))
                    #保存现场 塞到ready队列队尾
                    self.ready_queue.append(self.pcb_pool[self.loc_pid_inPool(self.running_pid)].pid)
                    self.running_pid = highest_priority_pcb.pid
                    self.pcb_pool[self.loc_pid_inPool(self.running_pid)].status = "running"
                    self.ready_queue.remove(self.running_pid)
                    return self.running_pid