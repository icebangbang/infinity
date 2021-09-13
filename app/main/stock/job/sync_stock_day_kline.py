from app.main.stock.dao import stock_dao
from app.main.stock.service import sync_kline_service
import logging

"""
同步日k数据
"""

stocks = stock_dao.get_all_stock()
# 获取最近一个交易日

for index,stock in enumerate(stocks):
    logging.info("同步{}:{}的日k数据,时序{}".format(stock['name'],stock["code"],index))
    r = sync_kline_service.sync_day_level(stock["code"], )
    if r is not None:
        # time.sleep(0.1)
        pass
    else:
        logging.info("已经处理过")

