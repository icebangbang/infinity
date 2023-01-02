from app.main.client.nacos import rest_api


@rest_api(service_name="tequila",path="/tequila/test/ok",method='post')
def task_callback(request_body=None,header=None):
    pass




if __name__ == "__main__":
    task_callback(dict(s=2),dict(s=3))