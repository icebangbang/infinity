from app.celery_worker import celery, MyTask
from app.main.db.mongo import db
from app.main.stock.dao import board_dao, stock_dao, task_dao
import logging
from datetime import datetime, timedelta
import time
from app.main.utils import date_util

from app.main.stock.service import sync_kline_service
from app.main.stock.stock_pick_filter import stock_filter
from app.main.utils import my_redis, date_util
import uuid

"""
个股数据同步
"""


@celery.task(bind=True, base=MyTask, expires=180)
def sync_stock_k_line(self):
    """
    同步股票日k线
    :param self:
    :return:
    """
    now = datetime.now()
    # 收盘后,不再同步

    switch = my_redis.get_bool("sync_after_15")
    logging.info("switch is {}".format(switch))
    if switch is True:
        stocks = stock_dao.get_all_stock(dict(code=1))
        # 获取最近一个交易日
        codes = [stock['code'] for stock in stocks]

        global_task_id = str(uuid.uuid1())
        task_dao.record_task(global_task_id, now)

        transform_task.apply_async(args=[codes, global_task_id, 0])


@celery.task(bind=True, base=MyTask, expires=180)
def transform_task(self, codes, task_id, deepth):
    if len(codes) <= 25:
        sync_stock_data.apply_async(args=[codes, task_id])
        return

    step = int(len(codes) / 25)
    for i in range(0, len(codes), step):
        group = codes[i:i + step]
        print("拆分个股k线任务,时序{}:{},层次:{}".format(i, i + step, deepth))

        transform_task.apply_async(args=[group, task_id, deepth + 1])


@celery.task(bind=True, base=MyTask, expires=180)
def sync_stock_data(self, codes, task_id):
    # logging.info("开始同步个股,{}".format(len(stocks)))
    try:
        for index, code in enumerate(codes):
            # logging.info("同步{}:{}的日k数据,时序{}".format(board['board'], board["code"], index))
            r = sync_kline_service.sync_day_level(code)
    except Exception as e:
        raise self.retry(exc=e, countdown=3, max_retries=5)

    task_dao.record_task(task_id)


@celery.task(bind=True, base=MyTask, expires=180)
def submit_stock_feature(self, to_date=None):
    stocks = stock_dao.get_all_stock(dict(code=1))
    code_name_map = stock_dao.get_code_name_map()

    if to_date is None:
        to_date = date_util.get_start_of_day(datetime.now())
    else:
        to_date = date_util.from_timestamp(to_date)
    from_date = to_date - timedelta(days=700)

    from_date_timestamp = int(time.mktime(from_date.timetuple()))
    to_date_timestamp = int(time.mktime(to_date.timetuple()))

    codes = [stock['code'] for stock in stocks]
    step = int(len(codes) / 400)

    for i in range(0, len(codes), step):
        group = codes[i:i + step]
        name_dict = {code: code_name_map[code] for code in group}
        sync_stock_feature.apply_async(args=[from_date_timestamp, to_date_timestamp, group, name_dict])


@celery.task(bind=True, base=MyTask, expires=3600)
def sync_stock_feature(self, from_date, to_date, codes, name_dict):
    if isinstance(from_date, int):
        from_date = datetime.fromtimestamp(int(from_date))
        to_date = datetime.fromtimestamp(int(to_date))
    companies = stock_filter.get_stock_status(from_date, to_date, codes=codes, code_name_map=name_dict)
    stock_dao.dump_stock_feature(companies, to_date)
