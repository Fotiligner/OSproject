def scheduler(self):
    # print("进入了Scheduler")
    if(self.schedule_type == "FCFS"):
        Scheduler_FCFS(self)

    #时间片轮转
    #需要在manager里添加一个时间片计数器
    #若时间片没有用完，进程就结束，那么立即调度就绪队列中的队首进程运行，并启动一个新的时间片。
    elif(self.schedule_type == "RR"):
        Scheduler_RR(self, time_slice)

    #抢占优先级
    elif(self.schedule_type == "Preempting"):
        Scheduler_preempting(self)

    return 0

    #   self.running_pid = -1  当前运行的
    #    self.pcb_pool = []   # 整体pcb池，存储所有pcb
    def Scheduler_FCFS(self):
        if len(self.ready_queue) != 0:
            self.running_pid = self.ready_queue[0]
            self.pcb_pool[self.running_pid].status = "running"
            self.ready_queue.remove(self.running_pid)
            return self.running_pid

        else:
            return -1



    #   self.start_time = start_time
    def Scheduler_RR(self,time_slice):
        if len(self.ready_queue) != 0:
            self.running_pid = self.ready_queue[0]
            self.pcb_pool[self.running_pid].status = "running"
            if self.pcb_pool[self.running_pid].last_time <= time_slice:
                self.ready_queue.remove(self.running_pid)
                return self.running_pid
            else:
                self.pcb_pool[self.running_pid].last_time = self.pcb_pool[self.running_pid].last_time - time_slice
                self.ready_queue.remove(self.running_pid)
                self.ready_queue.append(self.running_pid)
                return self.running_pid
        else:
            return -1



    def Scheduler_preempting(self):
        plist = []                               #  保存 ready队列里面 所有进程的优先级  按照队列的顺序
        for i in range(len(self.ready_queue)):
            plist[i] = self.pcb_pool[self.ready_queue[i]].priority

        temp = max(plist)            # 得出最大的优先级数字

        for j in range(len(plist)):
            if temp == plist[j]:
                tempnumber = j          #得到最大优先级对面的下标  从而在ready队列里面找到 对应的进程
                break
        self.running_pid = self.ready_queue[tempnumber]
        self.pcb_pool[self.running_pid].status = "running"
        self.ready_queue.remove(self.running_pid)
        return self.running_pid


