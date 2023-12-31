#!/user/bin/python3
# @Author:  LSY
# @Date:    2018/7/4
from app.main.client.nacos.schedule.executor import Executor
import logging as log


class HeartBeatExecutor(Executor):

    def __init__(self, parent, service_name, ip, port, cluster_name):
        self.parent = parent
        self.service_name = service_name
        self.ip = ip
        self.port = port
        self.cluster_name = cluster_name

    def callable(self):
        try:
            self.parent.client.send_heartbeat(self.service_name, self.ip, self.port, self.cluster_name)
        except Exception as e:
            pass
            # log.error(e, exc_info=1)