import json
import logging

from flask import Blueprint
from flask import request

from app.main.utils import restful, string_util

rest = Blueprint('op', __name__, url_prefix='/api')
log = logging.getLogger(__name__)


# def init_all_blueprint(app):
#     app.register_blueprint(rest)
#     app.register_blueprint(auth)
#     app.register_blueprint(tr)

@rest.before_request
def before():
    """
    针对app实例定义全局拦截器
    """
    url = request.path  # 读取到当前接口的地址
    args = request.args
    body = request.json
    log.info(
        """
        [http请求]url:{},method:{}
                 路径入参:{}
                 body入参:{}
        """.format(url, request.method, string_util.to_string(args), json.dumps(body,ensure_ascii=False)))


@rest.after_request
def after(response):
    """在每次请求(视图函数处理)之后都被执行, 前提是视图函数没有出现异常"""
    resp_content = response.json
    log.info(
        """
        [http响应]resp:{}
                 statusCode:{}
        """.format(resp_content, response.status_code))
    return response


@rest.errorhandler(Exception)
def all_exception_handler(error):
    log.error(error, exc_info=1)
    return restful.response_error(error)


from . import indicator, task, \
    board, celery, \
    stock, login, \
    other, config, \
    test, report, \
    trend, common, trade
