def scheduler(self):
    # print("进入了Scheduler")
    #FCFS
    if len(self.pcb_list) > 0:
        for i in self.pcb_list:
            self.current_running = i.pid
            break

    #时间片轮转
    #需要在manager里添加一个时间片计数器
    #若时间片没有用完，进程就结束，那么立即调度就绪队列中的队首进程运行，并启动一个新的时间片。
    time_slot=3
    manager_counter=0
    manager_counter+=1
    if(manager_counter >= time_slot):  #一个时间片的时间用完了
        if len(self.pcb_list) > 0:
            for i in self.pcb_list:
                self.current_running = i.pid
                break


    #抢占优先级


    return 0