def scheduler(self):
    # print("进入了Scheduler")
    if len(self.pcb_list) > 0:
        for i in self.pcb_list:
            self.current_running = i.pid
    return 0