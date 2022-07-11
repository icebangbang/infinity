import time
import uuid

from app.celery_worker import celery, MyTask
from app.main.db.mongo import db
from app.main.stock.dao import stock_dao, task_dao
from datetime import datetime

from app.main.stock.service import stock_service, trend_service
from app.main.utils import date_util
import logging as log

"""
个股提醒
"""


@celery.task(bind=True, base=MyTask, expires=180)
def submit_trend_task(self, from_date=None, end_date=None, global_task_id=None,chain=None):
    stocks = stock_dao.get_all_stock(dict(code=1))
    codes = [stock['code'] for stock in stocks]
    code_name_map = stock_dao.get_code_name_map()
    step = int(len(codes) / 630)

    if from_date and end_date:
        from_date = date_util.from_timestamp(from_date)
        end_date = date_util.from_timestamp(end_date)
    else:
        from_date = datetime.now()
        end_date = datetime.now()

    global_task_id = global_task_id if global_task_id is not None else str(uuid.uuid1())
    task_dao.create_task(global_task_id, "app.main.task.trend_task.submit_trend_task", len(codes),chain)

    for i in range(0, len(codes), step):
        codes_group = codes[i:i + step]
        name_dict = {code: code_name_map[code] for code in codes_group}
        from_timestamp = int(time.mktime(from_date.timetuple()))
        end_timestamp = int(time.mktime(end_date.timetuple()))
        sync_trend_task.apply_async(args=[from_timestamp, end_timestamp, codes_group, name_dict, global_task_id])


# 同步趋势线
@celery.task(bind=True, base=MyTask, expires=180)
def sync_trend_task(self, from_date, end_date, codes, name_dict, global_task_id):
    from_date = datetime.fromtimestamp(int(from_date))
    end_date = datetime.fromtimestamp(int(end_date))
    for code in codes:
        name = name_dict.get(code)

        for date in date_util.WorkDayIterator(from_date, end_date):
            start_of_day = date_util.get_start_of_day(date)
            features = stock_dao.get_company_feature(code, start_of_day)
            log.info("sync_trend_task {},{}".format(code,start_of_day))
            trend_service.save_stock_trend_with_features(code, name, features, start_of_day)

    task_dao.update_task(global_task_id, len(codes),
                         "app.main.task.trend_task.submit_trend_task",
                         dict(from_date=from_date,end_date=end_date,global_task_id=global_task_id))


@celery.task(bind=True, base=MyTask, expires=180)
def get_trend_data_task(self, from_date=None, end_date=None, global_task_id=None):
    """
    将趋势变化数据聚合
    :param self:
    :param date:
    :return:
    """

    from_date = date_util.get_start_of_day(from_date) \
        if from_date is not None else date_util.get_start_of_day(datetime.now())

    end_date = date_util.get_start_of_day(end_date) \
        if end_date is not None else date_util.get_start_of_day(datetime.now())

    log.info("get_trend_data_task {},{}:{}".format(global_task_id,from_date,end_date))

    trend_service.get_trend_size_info(from_date, end_date)
