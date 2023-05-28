import logging
import time
from datetime import datetime

import dateutil

from app.main.stock.dao import stock_change_dao, stock_dao
from app.main.utils import date_util

log = logging.getLogger(__name__)


def add_stock_share_change():
    """
    个股股本结构同步
    :return:
    """
    stocks = stock_dao.get_all_stock(dict(code=1, date=1, MarketValue=1, name=1, _id=0))

    for index,stock in enumerate(stocks):
        name = stock['name']
        code = stock['code']
        # 股票上市时间
        start = stock['date']
        start = start - dateutil.relativedelta.relativedelta(months=3)
        market_value = stock['MarketValue']
        if index <814:
            continue

        log.info("同步个股的股本结构信息:{},{}".format(index, name))

        if market_value == 0:
            log.info("个股已经退市:{},{}".format(index, name))
            continue

        end = date_util.get_start_of_day(datetime.now())
        stock_change_dao.dump_stock_share_change(code, start, end)


if __name__ == "__main__":
    add_stock_share_change()
