import time
import random
from multiprocessing import Pool
from app.main.db.mongo import db
from app.main.stock.dao import board_dao, stock_dao
import logging

from app.main.stock.service import sync_kline_service


def run(stock_group):
    for index, stock in enumerate(stock_group):
        logging.info("同步{}:{}的日k数据,时序{}".format(stock['name'], stock["code"], index))
        r = sync_kline_service.sync_day_level(stock["code"], )
        if r is not None:
            # time.sleep(0.1)
            pass
        else:
            logging.info("已经处理过")


if __name__ == '__main__':

    stocks = stock_dao.get_all_stock()
    total = len(stocks)

    step = int(len(stocks) / 8)
    stock_groups = [stocks[i:i + step] for i in range(0, len(stocks), step)]

    pool = Pool()
    pool.map(run, stock_groups)

    pool.close()
    pool.join()
