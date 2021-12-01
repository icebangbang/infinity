import akshare as ak
from app.main.stock.dao import stock_dao,board_dao
from app.main.stock.service import sync_kline_service
import logging

"""
同步板块k线数据
"""

def sync():
    boards = board_dao.get_all_board()
    # 获取最近一个交易日

    for index,board in enumerate(boards):
        logging.info("同步{}:{}的日k数据,时序{}".format(board['board'],board["code"],index))
        r = sync_kline_service.sync_board_k_line(board['board'],board['type'])
        if r is not None:
            # time.sleep(0.1)
            pass
        else:
            logging.info("已经处理过")


sync()

