from app.celery_worker import celery, MyTask
from app.main.db.mongo import db
from app.main.stock.job import sync_board
from app.main.stock.dao import board_dao, stock_dao, task_dao
import logging
from datetime import datetime

from app.main.stock.service import sync_kline_service
from app.main.utils import my_redis, date_util
import uuid

"""
板块数据同步
"""


@celery.task(bind=True, base=MyTask, expires=180)
def sync_board_k_line(self):
    """
    同步板块k线
    :param self:
    :return:
    """
    now = datetime.now()
    # 收盘后,不再同步

    switch = my_redis.get_bool("sync_after_15")
    logging.info("switch is {}".format(switch))
    if switch is True:
        boards = board_dao.get_all_board()
        # 获取最近一个交易日

        step = int(len(boards) / 50)
        boards_group = [boards[i:i + step] for i in range(0, len(boards), step)]
        for index, boards in enumerate(boards_group):
            logging.info("提交同步任务,时序{}".format(index))
            sync_data.apply_async(args=[boards])


@celery.task(bind=True, base=MyTask, expires=180)
def sync_data(self, boards):
    logging.info("开始同步,{}".format(len(boards)))
    for index, board in enumerate(boards):
        # logging.info("同步{}:{}的日k数据,时序{}".format(board['board'], board["code"], index))
        r = sync_kline_service.sync_board_k_line(board['board'], board['type'])


@celery.task(bind=True,base=MyTask,expire=1800)
def sync_board_stock_detail(self):
    """
    同步板块和个股详情
    :param self:
    :return:
    """
    sync_board.sync()



