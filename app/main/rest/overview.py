"""
股市全局数据统计和展示
"""

from app.main.utils import restful, date_util
# from . import rest
from datetime import datetime, timedelta
from app.main.stock.dao import k_line_dao


# @rest.route("/overview/stock", methods=['get'])
def stock_info():
    now = datetime.now()
    now = now - timedelta(days=1)
    start, end = date_util.get_work_day(now, 1)
    k_line_dao.get_k_line_data(start, end)

    return restful.response("ok")


