from app.main.stock.dao import stock_dao, k_line_dao
from app.main.stock.service import sync_kline_service
import logging
from datetime import datetime

"""
同步周k数据
"""

if __name__ == "__main__":
    stocks = stock_dao.get_all_stock()
    # 获取最近一个交易日


    k_line_dao.clear_k_line()
    from_date = datetime(2020, 1, 1)

    for index, stock in enumerate(stocks):
        logging.info("同步{}:{}的周k数据,时序{}".format(stock['name'], stock["code"], index))
        r = sync_kline_service.sync_week_level(stock["code"],from_date )
        if r is not None:
            # time.sleep(0.1)
            pass
        else:
            logging.info("已经处理过")
