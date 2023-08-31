from app.celery_application import celery, MyTask
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
def sync_board_k_line(self,**kwargs):
    """
    同步板块k线
    :param self:
    :return:
    """
    params = kwargs.get("params", {})

    global_task_id = params.get("global_task_id", None)

    boards = board_dao.get_all_board(type=[1, 2])
    # 获取最近一个交易日
    task_dao.create_task(global_task_id, "同步东财板块日k线", len(boards), kwargs)

    step = int(len(boards) / 10)
    boards_group = [boards[i:i + step] for i in range(0, len(boards), step)]
    for index, boards in enumerate(boards_group):
        logging.info("[东财板块日k线同步]global_task_id:{},时序:{}".format(global_task_id,index))
        sync_data.apply_async(kwargs=dict(boards=boards,global_task_id=global_task_id))


@celery.task(bind=True, base=MyTask, expires=180)
def sync_data(self, boards,global_task_id):
    """
    具体的同步板块k线的任务
    :param self:
    :param boards:
    :param global_task_id:
    :return:
    """
    name = [board['board'] for board in boards]
    logging.info("[东财板块日k线]global_task_id:{},板块:{}".format(global_task_id, name))
    try:
        for index, board in enumerate(boards):
            # logging.info("同步{}:{}的日k数据,时序{}".format(board['board'], board["code"], index))
            r = sync_kline_service.sync_board_k_line(board['board'], board['type'])
    except Exception as e:
        raise self.retry(exc=e, countdown=3, max_retries=10)


@celery.task(bind=True, base=MyTask, expire=1800)
def sync_board_stock_detail(self):
    """
    从东财同步板块和个股详情
    单线程同步操作
    :param self:
    :return:
    """
    sync_board.sync_and_update_stock()


@celery.task(bind=True, base=MyTask, expires=180)
def submit_board_feature(self, to_date=None, codes=None):
    """
    拆分任务,然后各个节点执行任务
    :param self:
    :param to_date:
    :param codes:
    :return:
    """
    if to_date is None:
        to_date = date_util.get_start_of_day(datetime.now())
    else:
        to_date = date_util.from_timestamp(to_date)

    if date_util.if_workday(to_date) is False:
        logging.info("the day is not workday:{}".format(date_util.date_time_to_str(to_date)))
        return

    # code_name_map = stock_dao.get_code_name_map()
    # from_date = to_date - timedelta(days=700)

    # from_date_timestamp = int(time.mktime(from_date.timetuple()))
    base_timestamp = int(time.mktime(to_date.timetuple()))
    offset = -252

    boards = board_dao.get_all_board(type=[2])
    names = [board['board'] for board in boards]
    step = int(len(names) / 30)

    for i in range(0, len(names), step):
        group = names[i:i + step]
        sync_board_feature.apply_async(args=[base_timestamp, offset, group])


@celery.task(bind=True, base=MyTask, expires=3600)
def sync_board_feature(self, base_timestamp, offset, names):
    """
    获取板块特征任务
    :param self:
    :param base_timestamp:
    :param offset:
    :param names:
    :return:
    """
    if isinstance(base_timestamp, int):
        # from_date = datetime.fromtimestamp(int(from_date))
        # to_date = datetime.fromtimestamp(int(to_date))
        base_date = datetime.fromtimestamp(int(base_timestamp))
    companies = board_filter.get_board_status(base_date, offset, names)
    board_dao.dump_board_feature(companies, base_date)

