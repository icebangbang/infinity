from app.celery_worker import celery, MyTask
from app.main.db.mongo import db
from app.main.stock.dao import board_dao, stock_dao, task_dao
import logging
from datetime import datetime, timedelta
import time

from app.main.stock.job import sync_stock_indicator, sync_index_kline
from app.main.stock.task_wrapper import TaskWrapper
from app.main.task import task_constant
from app.main.utils import date_util

from app.main.stock.service import sync_kline_service, stock_service, report_service, trend_service
from app.main.stock.stock_pick_filter import stock_filter
from app.main.utils import my_redis, date_util
import uuid
import akshare as ak

"""
个股数据同步
"""


@celery.task(bind=True, base=MyTask, expires=180)
def sync_stock_month_data(self, codes):
    """
    worker驱动
    开始同步月线数据
    :param self:
    :param codes:
    :return:
    """
    try:
        for index, code in enumerate(codes):
            r = sync_kline_service.sync_month_level(code)
    except Exception as e:
        raise self.retry(exc=e, countdown=3, max_retries=5)


@celery.task(bind=True, base=MyTask, expires=180)
def submit_stock_month_task(self):
    """
    schedule驱动
    提交同步月线数据任务
    :param self:
    :return:
    """
    stocks = stock_dao.get_all_stock(dict(code=1))
    codes = [stock['code'] for stock in stocks]
    step = int(len(codes) / 25)
    for i in range(0, len(codes), step):
        group = codes[i:i + step]
        sync_stock_month_data.apply_async(args=[group])


@celery.task(bind=True, base=MyTask, expires=180)
def sync_stock_k_line(self):
    """
    schedule驱动
    提交同步股票日k线任务
    :param self:
    :return:
    """
    now = datetime.now()
    # 收盘后,不再同步

    stocks = stock_dao.get_all_stock(dict(code=1))
    # 获取最近一个交易日
    codes = [stock['code'] for stock in stocks]

    global_task_id = str(uuid.uuid1())
    task_dao.create_task(global_task_id, "app.main.task.stock_task.sync_stock_k_line", len(codes))
    transform_task.apply_async(args=[codes, global_task_id, 0])


@celery.task(bind=True, base=MyTask, expires=180)
def transform_task(self, codes, task_id, deepth):
    """
    默认worker驱动
    拆分同步股票日k线任务,然后提交
    :param self:
    :param codes:
    :param task_id:
    :param deepth:
    :return:
    """
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
    """
    day_level worker驱动
    正式从第三方网站抓取数据
    :param self:
    :param codes:
    :param task_id:
    :return:
    """
    # logging.info("开始同步个股,{}".format(len(stocks)))
    try:
        for index, code in enumerate(codes):
            # logging.info("同步{}:{}的日k数据,时序{}".format(board['board'], board["code"], index))
            r = sync_kline_service.sync_day_level(code)
    except Exception as e:
        raise self.retry(exc=e, countdown=3, max_retries=5)

    task_dao.update_task(task_id, len(codes))


@celery.task(bind=True, base=MyTask, expires=180)
def submit_stock_feature(self, to_date=None, codes=None, global_task_id=None):
    if to_date is None:
        t = datetime.now()
        if t.hour >= 20:
            logging.info("will not run job after 16")
            return
        to_date = date_util.get_start_of_day(datetime.now())
    else:
        to_date = date_util.from_timestamp(to_date)

    if date_util.if_workday(to_date) is False:
        logging.info("the day is not workday:{}".format(date_util.date_time_to_str(to_date)))
        return

    # switch = my_redis.get_bool("sync_after_15")
    # if not switch:
    #     logging.info("will not run job after 15")
    #     return

    code_name_map = stock_dao.get_code_name_map()
    # from_date = to_date - timedelta(days=500)

    # from_date_timestamp = int(time.mktime(from_date.timetuple()))
    base_timestamp = int(time.mktime(to_date.timetuple()))
    offset = "-252"

    global_task_id = global_task_id if global_task_id is not None else str(uuid.uuid1())
    if codes is None:
        stocks = stock_dao.get_all_stock(dict(code=1))
        codes = [stock['code'] for stock in stocks]
        step = int(len(codes) / 630)

        task_dao.create_task(global_task_id, "app.main.task.stock_task.submit_stock_feature", len(codes))

        for i in range(0, len(codes), step):
            group = codes[i:i + step]
            name_dict = {code: code_name_map[code] for code in group}
            sync_stock_feature.apply_async(args=[base_timestamp, offset, group, name_dict, global_task_id])
    else:
        task_dao.create_task(global_task_id, "app.main.task.stock_task.submit_stock_feature", len(codes))
        name_dict = {code: code_name_map[code] for code in codes}
        sync_stock_feature.apply_async(args=[base_timestamp, offset, codes, name_dict, global_task_id])


@celery.task(bind=True, base=MyTask, expires=36000)
def sync_stock_feature(self, base_date, offset, codes, name_dict, global_task_id):
    """
    同步
    :param self:
    :param base_date: 基准时间
    :param offset:
    :param codes:
    :param name_dict:
    :return:
    """
    if isinstance(base_date, int):
        # from_date = datetime.fromtimestamp(int(from_date))
        base_date = datetime.fromtimestamp(int(base_date))
    companies = stock_filter.get_stock_status(base_date, int(offset), codes=codes, code_name_map=name_dict)
    if companies is not None:
        stock_dao.dump_stock_feature(companies, base_date)

        # sync_trend_disable = my_redis.get_bool("sync_trend_disable")
        # 禁用同步
        # if not sync_trend_disable:
        #     for company in companies:
        #         trend_service.save_stock_trend_with_company(company, base_date)
    task_dao.update_task(global_task_id, len(codes), 'app.main.task.stock_task.submit_stock_feature',)


@celery.task(bind=True, base=MyTask, expire=1800)
def submit_stock_ind_task(self):
    """
    提交该任务
    同步市值,PE等指标
    :param self:
    :return:
    """
    stocks = stock_dao.get_all_stock(dict(code=1))
    codes = [stock['code'] for stock in stocks]
    t = datetime.now()

    task_id = str(uuid.uuid1())
    task_set = db['task_center']
    task_set.update({"task_id": task_id, "job_name": task_constant.TASK_SYNC_STOCK_IND},
                    {"$set": {"is_finished": 0, "create_time": t, "update_time": t}}, upsert=True)

    step = int(len(codes) / 100)
    for i in range(0, len(codes), step):
        group = codes[i:i + step]
        # logging.info("submit group index {} - {},{},{}".format(i, i + step,task_id,len(stocks)))
        sync_stock_ind.apply_async(args=[group, task_id, len(stocks)])


@celery.task(bind=True, base=MyTask, expire=1800)
def sync_stock_ind(self, codes, task_id, expect):
    task_wrapper = TaskWrapper(task_id, task_constant.TASK_SYNC_STOCK_IND, expect)
    stock_service.sync_stock_ind(codes, task_wrapper)


@celery.task(bind=True, base=MyTask, expire=1800)
def sync_index_data(self):
    """
    同步大盘指标
    :param self:
    :param codes:
    :param task_id:
    :param expect:
    :return:
    """
    sync_index_kline.sync()

@celery.task(bind=True, base=MyTask, expire=1800)
def sync_rps_analysis_250(self):
    report_service.rps_analysis(offset=-250)


@celery.task(bind=True, base=MyTask, expire=1800)
def sync_rps_analysis_120(self):
    report_service.rps_analysis(offset=-120)


@celery.task(bind=True, base=MyTask, expire=1800)
def sync_rps_analysis_60(self):
    report_service.rps_analysis(offset=-60)


@celery.task(bind=True, base=MyTask, expire=1800)
def sync_rps_analysis_30(self):
    report_service.rps_analysis(offset=-30)


@celery.task(bind=True, base=MyTask, expire=1800)
def sync_bellwether(self):
    stock_service.sync_bellwether()
