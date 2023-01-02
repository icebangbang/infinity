#!/user/bin/python3
# @Author:  LSY
# @Date:    2020/12/15
import json
from app.main.client.nacos.nacos_client import NacosClient
from app.main.client.nacos.service_executor import ServiceInstance
import requests

nacos_client = NacosClient()

def rest_api(**client):
    def inner(f):
        def wrapper(*args,**kwargs):
            service_name = client['service_name']
            path = client['path']
            method = client.get('method',"post")
            instances:list = nacos_client.service_executor.get_instance(service_name)
            if len(instances) > 0:
                instance:ServiceInstance = instances[0]
                url = "http://"+instance.ip+":"+str(instance.port)+path

                request_body = args[0]
                headers = args[1]

                resp = requests.request(method,url,json=request_body,headers=headers)

                return resp.json()

            # nacos_client.
            # print(json.dumps(args))
            # print(json.dumps(kwargs))
            # print(json.dumps(kk))
            return f(*args,**kwargs)
        return wrapper
    return inner