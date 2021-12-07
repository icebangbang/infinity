from app.main.utils import restful
from . import rest
from app.main.task import demo
from app.main.task import board_task
from flask import request
from app.main.utils import my_redis


@rest.route("/task/sync/boark_k_line/on", methods=['get'])
def send_job():
    switch = request.args.get("on","false")
    my_redis.set("board_sync_after_15",switch)

    return restful.response("ok")
