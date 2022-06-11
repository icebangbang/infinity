from app.celery_worker import celery, MyTask
from app.main.db.mongo import db
from datetime import timedelta
import time
from app.main.stock.job import sync_board
from app.main.stock.dao import board_dao, stock_dao, task_dao
import logging
from datetime import datetime

from app.main.stock.service import sync_kline_service
from app.main.stock.stock_pick_filter import board_filter
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

    # switch = my_redis.get_bool("sync_after_15")
    # logging.info("switch is {}".format(switch))
    # if switch is True:
    boards = board_dao.get_all_board(type=[1, 2])
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


@celery.task(bind=True, base=MyTask, expire=1800)
def sync_board_stock_detail(self):
    """
    同步板块和个股详情
    :param self:
    :return:
    """
    sync_board.sync()


@celery.task(bind=True, base=MyTask, expires=180)
def submit_board_feature(self, to_date=None, codes=None):
    if to_date is None:
        to_date = date_util.get_start_of_day(datetime.now())
    else:
        to_date = date_util.from_timestamp(to_date)

    if date_util.if_workday(to_date) is False:
        logging.info("the day is not workday:{}".format(date_util.date_time_to_str(to_date)))
        return

    # code_name_map = stock_dao.get_code_name_map()
    from_date = to_date - timedelta(days=700)

    from_date_timestamp = int(time.mktime(from_date.timetuple()))
    to_date_timestamp = int(time.mktime(to_date.timetuple()))

    boards = board_dao.get_all_board()
    names = [board['board'] for board in boards]
    step = int(len(names) / 30)

    for i in range(0, len(names), step):
        group = names[i:i + step]
        sync_board_feature.apply_async(args=[from_date_timestamp, to_date_timestamp, group])


@celery.task(bind=True, base=MyTask, expires=3600)
def sync_board_feature(self, from_date, to_date, names):
    if isinstance(from_date, int):
        from_date = datetime.fromtimestamp(int(from_date))
        to_date = datetime.fromtimestamp(int(to_date))
    companies = board_filter.get_board_status(from_date, to_date, names)
    board_dao.dump_board_feature(companies, to_date)
