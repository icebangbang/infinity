from app.main.utils import restful
from . import rest
from app.main.task import  fund_task
from flask import request
from app.main.utils import my_redis
from app import application
from app.main.rest import celery


@rest.route("/task/sync/boark_k_line/on", methods=['get'])
def send_job():
    switch = request.args.get("on", "false")
    my_redis.set("sync_after_15", switch)

    return restful.response("ok")


@rest.route("/task/sync/count", methods=['get'])
def test_incr():
    for i in range(1000):
        print(my_redis.incr("xx", 1))

    return restful.response("ok")


@rest.route("/task/sync/backtrading", methods=['get'])
def backtrading():
    fund_task.backtrading()
    return restful.response("ok")


@rest.route("/task/async/dispatch", methods=['post','get'])
def dispatch():
    """
    :return:
    """
    from app.main.client.nacos.service import tequila_client

    resp = tequila_client.task_callback(dict(a=3),{})

    celery.test()

    return restful.response("ok")