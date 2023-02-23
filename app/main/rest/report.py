"""
股市全局数据统计和展示
"""

from app.main.utils import restful, date_util
from . import rest
from datetime import datetime, timedelta
from app.main.stock.dao import k_line_dao
from ..stock.service import report_service


@rest.route("/report/overview", methods=['get'])
def overview():
    """
    报告数据概览
    :return:
    """
    r = report_service.get_overview()
    return restful.response(r)


