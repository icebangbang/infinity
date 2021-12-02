from app.celery_worker import celery, MyTask
from app.main.db.mongo import db
from app.main.stock.dao import board_dao
import logging

from app.main.stock.service import sync_kline_service

"""
板块数据同步
"""

@celery.task(bind=True, base=MyTask)
def sync_board_k_line(self):

    boards = board_dao.get_all_board()
    # 获取最近一个交易日

    step = int(len(boards) / 8)
    boards_group = [boards[i:i + step] for i in range(0, len(boards), step)]
    for boards in boards_group:
        sync_data(boards)


@celery.task(bind=True, base=MyTask)
def sync_data(self, boards):
    for index, board in enumerate(boards):
        logging.info("同步{}:{}的日k数据,时序{}".format(board['board'], board["code"], index))
        r = sync_kline_service.sync_board_k_line(board['board'], board['type'])
        if r is not None:
            # time.sleep(0.1)
            pass
        else:
            logging.info("已经处理过")


