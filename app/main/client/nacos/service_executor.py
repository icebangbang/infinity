#!/user/bin/python3
from app.main.client.nacos.schedule.executor import Executor
import logging as log

class ServiceInstance:
    def __init__(self,ip,port,service_name,cluster_name,weight):
        self.ip = ip
        self.port = port
        self.service_name = service_name
        self.cluster_name = cluster_name
        self.weight = weight


class ServiceExecutor(Executor):

    def __init__(self, parent, service_name_list):
        self.parent = parent
        self.service_name_list = service_name_list
        self.instances = {}

    def get_instance(self,serviec_name):
        return self.instances[serviec_name]

    def callable(self):
        try:
            for service_name in self.service_name_list:
                client = self.parent.client
                resp = client.list_naming_instance(service_name)
                hosts = resp['hosts']
                instance_list = []
                for host in hosts:
                    instance_list.append(ServiceInstance(host['ip'],
                                                         host['port'],
                                                         host['serviceName'],
                                                         host['clusterName'],
                                                         host['weight']
                                                         ))
                self.instances[service_name] = instance_list

        except Exception as e:
            pass
            # log.error(e, exc_info=1)
