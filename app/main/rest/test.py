from app.main.utils import restful
from . import rest
from app.main.task import demo
from app.main.task import board_task
from flask import request
from app.main.stock.service import stock_service


@rest.route("/test/remind", methods=['get'])
def remind():
    stock_service.stock_remind()
    return restful.response_obj("")
