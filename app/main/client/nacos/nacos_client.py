#!/user/bin/python3
# @Author:  LSY
# @Date:    2020/12/15
import nacos

from app.main.client.nacos.heart_beat_executor import HeartBeatExecutor
from app.main.client.nacos.service_executor import ServiceExecutor
from app.main.client.nacos.schedule.schedule_executor_service import ScheduleService
import logging
import atexit

log = logging.getLogger(__name__)

class NacosClient:
    def init(self, app):
        if app.config['REGISTERED_SERVER_TO_NACOS'] is False:
            return
        self.ip = app.config['SERVER_HOST']
        self.port = app.config['SERVER_PORT']
        self.__init(app)
        self.schedule = ScheduleService()
        self.heart_beat_executor = HeartBeatExecutor(self,
                                                     service_name=app.config['NACOS_SERVICE_NAME'],
                                                     ip=self.ip,
                                                     port=self.port,
                                                     cluster_name=app.config['NACOS_CLUSTER_NAME'])
        self.service_executor = ServiceExecutor(self,['tequila'])

        self.register(app)
        atexit.register(self.deregister, app=app)

    def __init(self, app):
        if app.config['IS_AUTH_MODE']:
            self.client = nacos.NacosClient(app.config['NACOS_SERVER_ADDRESSES'],
                                            namespace=app.config['NACOS_NAMESPACE'],
                                            username=app.config['NACOS_USERNAME'],
                                            password=app.config['NACOS_PASSWORD'])
        else:
            self.client = nacos.NacosClient(app.config['NACOS_SERVER_ADDRESSES'],
                                            namespace=app.config['NACOS_NAMESPACE'],
                                            )

        self.client.set_options(default_timeout=4)

    def register(self, app):
        self.client.add_naming_instance(service_name=app.config['NACOS_SERVICE_NAME'],
                                        ip=self.ip,
                                        port=self.port,
                                        cluster_name=app.config['NACOS_CLUSTER_NAME'],
                                        weight=app.config['NACOS_WEIGHT'])
        # 添加心跳
        self.schedule.schedule_at_fixed_rate("{}_HeartBeatExecutor"
                                             .format(app.config['NACOS_SERVICE_NAME']),
                                             self.heart_beat_executor,
                                             0,
                                             app.config['NACOS_HEARTBEAT_INTERVAL'])

        self.schedule.schedule_at_fixed_rate('ServiceExecutor',self.service_executor,
                                             0,10)

        # self.client.subscribe([a], 7,service_name="earring")


    def deregister(self,app):
        log.info("start deregister nacos service")
        self.client.remove_naming_instance(service_name=app.config['NACOS_SERVICE_NAME'],
                                           ip=self.ip,
                                           port=self.port,
                                           cluster_name=app.config['NACOS_CLUSTER_NAME'])
        log.info("end to deregister nacos service")

    def service(self,service_name):
        return self.client.list_naming_instance(service_name)




