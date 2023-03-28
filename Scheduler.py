def scheduler(self):
    # print("进入了Scheduler")
    #FCFS
    if len(self.pcb_list) > 0:
        for i in self.pcb_list:
            self.current_running = i.pid
            break

    #时间片轮转
    #若时间片没有用完，进程就结束，那么立即调度就绪队列中的队首进程运行，并启动一个新的时间片。
    time_slot = 3

    #抢占优先级


    return 0