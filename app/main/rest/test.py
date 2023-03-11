from app.main.utils import restful
from . import rest
import logging as log
from app.main.stock.service import stock_service


@rest.route("/test/remind", methods=['get'])
def remind():
    stock_service.stock_remind()
    return restful.response_obj("")


@rest.route("/test/log", methods=['get'])
def remind():
    log.debug('this is a DEBUG message')
    log.info('this is an INFO message')
    log.warning('this is a WARNING message')
    log.error('this is an ERROR message')
    log.critical('this is a CRITICAL message')
    return restful.response_obj("")


