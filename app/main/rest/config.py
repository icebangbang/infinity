from app.main.utils import restful
from . import rest
from app.main.task import demo
from app.main.task import board_task
from flask import request
from app.main.stock.service import config_service


@rest.route("/config/query/save", methods=['post'])
def save_config():
    params: dict = request.json
    config_service.save_query_param(params)
    return restful.response_obj("ok")
