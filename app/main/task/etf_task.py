import time
import uuid

from app.celery_worker import celery, MyTask
from datetime import datetime
import logging

from app.main.stock.dao import etf_dao, task_dao
from app.main.stock.etf_pick_feature import etf_filter
from app.main.stock.stock_pick_filter import stock_filter
from app.main.utils import date_util


@celery.task(bind=True, base=MyTask, expires=180)
def submit_etf_feature(self, to_date=None, codes=None, global_task_id=None):
    if to_date is None:
        t = datetime.now()
        if t.hour >= 20:
            logging.info("will not run job after 20")
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
    etfs = etf_dao.get_eft_list()
    code_name_map = {etf['code']: etf['name'] for etf in etfs}
    # from_date = to_date - timedelta(days=500)

    # from_date_timestamp = int(time.mktime(from_date.timetuple()))
    base_timestamp = int(time.mktime(to_date.timetuple()))
    offset = "-252"

    global_task_id = global_task_id if global_task_id is not None else str(uuid.uuid1())
    if codes is None:
        etfs = etf_dao.get_eft_list()
        codes = [etf['code'] for etf in etfs]
        step = int(len(codes) / 20)

        task_dao.create_task(global_task_id, "app.main.task.etf_task.submit_etf_feature", len(codes))

        for i in range(0, len(codes), step):
            group = codes[i:i + step]
            name_dict = {code: code_name_map[code] for code in group}
            sync_etf_feature.apply_async(args=[base_timestamp, offset, group, name_dict, global_task_id])
    else:
        task_dao.create_task(global_task_id, "app.main.task.etf_task.submit_etf_feature", len(codes))
        name_dict = {code: code_name_map[code] for code in codes}
        sync_etf_feature.apply_async(args=[base_timestamp, offset, codes, name_dict, global_task_id])


@celery.task(bind=True, base=MyTask, expires=36000)
def sync_etf_feature(self, base_date, offset, codes, name_dict, global_task_id):
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
    companies = etf_filter.get_etf_status(base_date, int(offset), codes=codes, code_name_map=name_dict)
    if companies is not None:
        etf_dao.dump_etf_feature(companies, base_date)

        # sync_trend_disable = my_redis.get_bool("sync_trend_disable")
        # 禁用同步
        # if not sync_trend_disable:
        #     for company in companies:
        #         trend_service.save_stock_trend_with_company(company, base_date)
    task_dao.update_task(global_task_id, len(codes), 'app.main.task.etf_task.submit_etf_feature', )
