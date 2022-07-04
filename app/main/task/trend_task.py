import time

from app.celery_worker import celery, MyTask
from app.main.db.mongo import db
from app.main.stock.dao import stock_dao
from datetime import datetime

from app.main.stock.service import stock_service, trend_service
from app.main.utils import date_util

"""
个股提醒
"""


@celery.task(bind=True, base=MyTask, expires=180)
def submit_trend_task(self,from_date=None,end_date=None):
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

    for i in range(0, len(codes), step):
        codes_group = codes[i:i + step]
        name_dict = {code: code_name_map[code] for code in codes_group}
        from_timestamp = int(time.mktime(from_date.timetuple()))
        end_timestamp = int(time.mktime(end_date.timetuple()))
        sync_trend_task.apply_async(args=[from_timestamp,end_timestamp, codes, name_dict])\


@celery.task(bind=True, base=MyTask, expires=180)
def get_trend_data_task(self):
    """
    将趋势变化数据聚合
    :param self:
    :param date:
    :return:
    """
    date = date_util.get_end_of_day(datetime.now())
    trend_service.get_trend_size_info(date,date)



# 同步趋势线
@celery.task(bind=True, base=MyTask, expires=180)
def sync_trend_task(self,from_date,end_date,codes,name_dict):
    from_date = datetime.fromtimestamp(int(from_date))
    end_date = datetime.fromtimestamp(int(end_date))
    for code in codes:
        name = name_dict.get(code)

        for date in date_util.WorkDayIterator(from_date,end_date):
            start_of_day = date_util.get_start_of_day(date)
            features = stock_dao.get_company_feature(code,date)
            trend_service.save_stock_trend_with_features(code,name,features,start_of_day)

