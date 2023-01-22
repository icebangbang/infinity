import logging
import time
import uuid
from datetime import datetime

from app.celery_worker import celery, MyTask
from app.main.db.mongo import db
from app.main.stock.dao import stock_dao, task_dao
from app.main.stock.job import job_config
from app.main.stock.job import sync_index_kline, sync_performance
from app.main.stock.service import sync_kline_service, stock_service, report_service
from app.main.stock.stock_pick_filter import stock_filter
from app.main.stock.task_wrapper import TaskWrapper
from app.main.task import task_constant
from app.main.utils import date_util
from app.main.utils.date_util import WorkDayIterator

"""
个股数据同步
"""


@celery.task(bind=True, base=MyTask, expires=180)
def sync_stock_month_data(self, codes,global_task_id):
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
        raise self.retry(exc=e, countdown=3, max_retries=10)


@celery.task(bind=True, base=MyTask, expires=180)
def submit_stock_month_task(self,**kwargs):
    """
    schedule驱动
    提交同步月线数据任务
    :param self:
    :return:
    """
    global_task_id = kwargs['global_task_id']

    stocks = stock_dao.get_all_stock(dict(code=1))
    codes = [stock['code'] for stock in stocks]
    step = int(len(codes) / 25)
    for i in range(0, len(codes), step):
        group = codes[i:i + step]
        sync_stock_month_data.apply_async(kwargs=dict(codes=group,global_task_id=global_task_id))


@celery.task(bind=True, base=MyTask, expires=180)
def sync_stock_k_line(self, rebuild_data=None):
    """
    schedule驱动
    提交同步股票日k线任务
    :param self:
    :param reuild_data: 因为分红等关系,前复权数据会将历史收盘价进行压缩,需要重跑数据
    :return:
    """
    now = datetime.now()
    if rebuild_data is None and \
            job_config.check_status_available("app.main.task.stock_task.sync_stock_k_line") is False:
        return

    # 收盘后,不再同步
    if 20 <= now.hour < 10 and rebuild_data is None:
        return

    stocks = stock_dao.get_all_stock(dict(code=1))
    # 获取最近一个交易日
    codes = [stock['code'] for stock in stocks]

    global_task_id = str(uuid.uuid1())

    if rebuild_data:
        job_config.set_job_config(global_task_id,
                                  dict(
                                      job_chain=['app.main.task.stock_task.auto_submit_stock_feature'],
                                      normal_chain=[],
                                      kwargs=dict()
                                  ))

    task_dao.create_task(global_task_id, "app.main.task.stock_task.sync_stock_k_line", len(codes))
    transform_task.apply_async(args=[codes, global_task_id, 0])


@celery.task(bind=True, base=MyTask, expires=180)
def sync_stock_k_line_by_job(self, **kwargs):
    """
    schedule驱动
    提交同步股票日k线任务
    :param self:
    :param reuild_data: 因为分红等关系,前复权数据会将历史收盘价进行压缩,需要重跑数据
    :return:
    """
    params = kwargs.get("params", {})

    global_task_id = params.get("global_task_id", None)
    stocks = stock_dao.get_all_stock(dict(code=1))
    # 获取最近一个交易日
    codes = [stock['code'] for stock in stocks]

    task_dao.create_task(global_task_id, "同步个股日k线", len(codes), kwargs)
    transform_task.apply_async(kwargs=dict(codes=codes, global_task_id=global_task_id, deepth=0))


@celery.task(bind=True, base=MyTask, expires=180)
def transform_task(self, codes, global_task_id, deepth):
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
        sync_stock_data.apply_async(kwargs=dict(codes=codes, global_task_id=global_task_id))
        return

    step = int(len(codes) / 25)
    for i in range(0, len(codes), step):
        group = codes[i:i + step]
        logging.info("拆分个股k线任务,时序{}:{},层次:{}".format(i, i + step, deepth))

        transform_task.apply_async(kwargs=dict(codes=group, global_task_id=global_task_id, deepth=deepth + 1))


@celery.task(bind=True, base=MyTask, expires=1800)
def sync_stock_data(self, codes, global_task_id):
    """
    day_level worker驱动
    正式从第三方网站抓取数据
    :param self:
    :param codes:
    :param global_task_id:
    :return:
    """
    # logging.info("开始同步个股,{}".format(len(stocks)))
    try:
        for index, code in enumerate(codes):
            # logging.info("同步{}:{}的日k数据,时序{}".format(board['board'], board["code"], index))
            r = sync_kline_service.sync_day_level(code)
    except Exception as e:
        raise self.retry(exc=e, countdown=3, max_retries=10)


@celery.task(bind=True, base=MyTask, expires=36000)
def submit_stock_feature(self, to_date=None, codes=None, global_task_id=None):
    if to_date is None:
        t = datetime.now()
        if date_util.in_trade_time_scope(t, 0, 0.5) is False:
            logging.info("非交易时间不执行个股特征跑批")
            return
        to_date = date_util.get_start_of_day(datetime.now())
    else:
        to_date = date_util.from_timestamp(to_date)

    if date_util.if_workday(to_date) is False:
        logging.info("the day is not workday:{}".format(date_util.date_time_to_str(to_date)))
        return

    code_name_map = stock_dao.get_code_name_map()
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
def submit_stock_feature_by_job(self, **kwargs):
    params = kwargs.get("params", {})
    from_date_ts = params.get("from_date_ts", None)
    end_date_ts = params.get("end_date_ts", None)
    global_task_id = params.get("global_task_id", None)

    from_date = date_util.from_timestamp(from_date_ts)
    end_date = date_util.from_timestamp(end_date_ts)
    days = date_util.get_days_between(end_date, from_date)

    stocks = stock_dao.get_all_stock(dict(code=1))
    codes = [stock['code'] for stock in stocks]
    task_dao.create_task(global_task_id, "个股特征跑批", len(codes) * (1 + days), kwargs)

    code_name_map = stock_dao.get_code_name_map()
    for to_date in WorkDayIterator(from_date, end_date):

        base_timestamp = int(time.mktime(to_date.timetuple()))
        offset = "-252"

        step = int(len(codes) / 630)

        for i in range(0, len(codes), step):
            group = codes[i:i + step]
            name_dict = {code: code_name_map[code] for code in group}
            sync_stock_feature.apply_async(args=[base_timestamp, offset, group, name_dict, global_task_id])


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


@celery.task(bind=True, base=MyTask, expire=1800)
def submit_stock_ind_task(self):
    """
    提交该任务
    同步市值,PE等指标
    :param self:
    :return:
    """
    try:
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
    except Exception as e:
        logging.error(e, exc_info=1)


@celery.task(bind=True, base=MyTask, expire=1800)
def sync_stock_ind(self, codes, task_id, expect):
    try:
        task_wrapper = TaskWrapper(task_id, task_constant.TASK_SYNC_STOCK_IND, expect)
        stock_service.sync_stock_ind(codes, task_wrapper)
    except Exception as e:
        logging.error(e, exc_info=1)


@celery.task(bind=True, base=MyTask, expire=1800)
def auto_submit_stock_feature(self, days=1100):
    """
    全局重跑个股指标
    :param self:
    :return:
    """
    logging.info("days span is {}".format(days))
    date_start = date_util.get_work_day(datetime.now(), days)
    for day in range(days):
        date_start = date_util.add_and_get_work_day(date_start, 1)
        logging.info("submit stock feature:{}".format(date_util.dt_to_str(date_start)))
        submit_stock_feature.apply_async(args=[date_util.to_timestamp(date_start)])


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


@celery.task(bind=True, base=MyTask, expire=18000)
def sync_balance(self):
    """
    资产负债表
    :param self:
    :return:
    """
    sync_performance.sync_balance()


@celery.task(bind=True, base=MyTask, expire=18000)
def sync_cash_flow(self):
    """
    现金流
    :param self:
    :return:
    """
    sync_performance.sync_cash_flow()


@celery.task(bind=True, base=MyTask, expire=18000)
def sync_profit(self):
    """
    利润表
    :param self:
    :return:
    """
    sync_performance.sync_profit()


@celery.task(bind=True, base=MyTask, expire=18000)
def sync_analysis_indicator(self):
    """
    利润表
    :param self:
    :return:
    """
    sync_performance.sync_analysis_indicator()
