# 所有Process管理的工具类
class Process_Utils():
    #将pid转换成在POOL里的下标
    #传入pid, 返回在Pool里的下标
    def loc_pid_inPool(self,pid):
        i=-1
        for readypid in self.ready_queue:
            i+=1
            if(readypid == pid):
                #print("返回了" + str(i))
                return i