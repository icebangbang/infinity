from app.main.stock.service import trend_service
from app.main.utils import restful
from . import rest
from app.main.task import demo
from app.main.task import board_task, fund_task
from flask import request
from app.main.utils import my_redis


@rest.route("/trend/board/list", methods=['get'])
def trend_list():
    total = ""
    return restful.response(total)

