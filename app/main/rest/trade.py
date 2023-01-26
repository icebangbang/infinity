from app.main.stock.job import job_config
from app.main.utils import restful, date_util
from . import rest
from app.main.task import fund_task, trade_constant
from flask import request


@rest.route("/trade/sync/dispatch", methods=['post', 'get'])
def trade_sync_dispatch():
    """
    :param
        globalId: 任务流水号
        tradeDate： 交易日期
        taskName：任务名称
    :return:
    """
    req = request.json
    # trade_date_str = req['tradeDate']
    # trade_date = date_util.parse_date_time(trade_date_str)
    method = trade_constant.TRADE_MAPPING[req['taskName']]

    result = method(**req)

    return restful.response({"status":"ok","method":method,"result":result})
