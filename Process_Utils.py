# 所有Process管理的工具类
class Process_Utils():
    #将pid转换成在POOL里的下标
    #传入pid, 返回在Pool里的下标
    def loc_pid_inPool(self,pid):
        i=-1
        for poolpid in self.pcb_pool:
            i+=1
            if(poolpid.pid == pid):
                #print("返回了" + str(i))
                return i

    #将pid转换成在ready_queue里的下标
    #传入pid, 返回在ready_queue里的下标
    def loc_pid_inReady(self,pid):
        i=-1
        for readypid in self.ready_queue:    # 继承，可使用子类的属性
            i+=1
            if(readypid == pid):
                #print("返回了" + str(i))
                return i
    #获取当前最新可用pid的 返回两个值,是否是旧pcb 和 pid
    def getCurrentpid(self):
        count = 0
        for i in self.pcb_pool:
            #print("====正在调度get,pid="+str(i.pid) + ",status="+str(i.status))
            count+=1
            #如果发现存在已经终止的pcb,就用这个pcb
            if i.status == "terminated":
                return "old",i.pid
        #如果遍历结束发现没用可用的, 就新建一个
        return "new",count+1