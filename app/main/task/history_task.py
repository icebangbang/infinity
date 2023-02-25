"""
历史数据跑批任务
"""
from datetime import datetime
import logging

from app.main.db.mongo import db
from app.main.stock.dao import task_dao
from app.main.task import stock_task, task_constant
from app.main.utils import date_util, collection_util
from app.celery_worker import celery, MyTask


@celery.task(bind=True, base=MyTask, expire=1800)
def submit_history_stock_feature_by_job(self, **kwargs):
    """
    1. 获取任务,设置任务tag
    2. 并拆分任务
    3. 提交到redis的zset中,用日级别的时间戳正序排序,完成任务的tag放到最后
    4. dao本体订阅redis的zset进行任务的分发,日级别任务的分发必须在前一日所有任务完成后才能执行
    5. 读取到tag后,就更新任务为成功,并回调
    :return:
    """
    history_task = db["history_task"]
    history_task_detail = db["history_task_detail"]
    global_id = kwargs['global_task_id']
    task_name = kwargs['task_name']
    days = 31
    logging.info("days span is {}".format(days))
    date_start = date_util.get_work_day(datetime.now(), days)

    # 添加历史数据跑批任务的详情
    details = []
    for day in range(days):
        date_start = date_util.add_and_get_work_day(date_start, 1)

        details.append(dict(global_task_id=global_id,
                            task_name=task_name,
                            date=date_start,
                            status=0,
                            index = day,
                            total = days,
                            create_time=datetime.now(),
                            update_time=datetime.now()))

    history_task_detail.insert_many(details)
    # 添加历史数据跑批任务
    history_task.insert_one(dict(global_task_id=global_id,
                                 task_name=task_name,
                                 is_finished=0,
                                 create_time=datetime.now(),
                                 update_time=datetime.now(),
                                 task_info=kwargs))


@celery.task(bind=True, base=MyTask, expire=1800)
def start_stock_feature_task(self, **kwargs):
    """
    定时轮询表,然后发布任务
    :return:
    """
    history_task = db["history_task"]
    history_task_detail = db["history_task_detail"]
    task_info = history_task.find_one({"is_finished": 0, "task_name": "个股历史特征按批次跑批"})

    if task_info is None:
        return

    minutes = date_util.get_minutes_between(datetime.now(), task_info['update_time'])

    if minutes <= 10:
        # 保持间隔,不需要跑的太猛
        return

    # 这里可能会有重复执行
    global_task_id = task_info['global_task_id']
    # 正序排序
    task_detail_list = list(history_task_detail.find({"global_task_id": global_task_id,
                                                      "status": {"$in": [0, 1]}}).sort("_id", 1))

    if collection_util.is_not_empty(task_detail_list):
        task_detail_item = task_detail_list[0]
        # 最近一个任务还在处理中,不做额外处理
        if task_detail_item['status'] == 1:
            return

        date = task_detail_item['date']
        index = task_detail_item['index']

        flow_job_info = task_info['task_info']
        flow_job_info['global_task_id'] = global_task_id +"_"+str(index)
        flow_job_info['callback_service'] = "app.main.task.history_task.update_history_feature"
        flow_job_info['params'] = dict(
            from_date_ts=date_util.to_timestamp(date),
            end_date_ts=date_util.to_timestamp(date),
            global_task_id=global_task_id
        )

        stock_task.submit_stock_feature_by_job.apply_async(kwargs=flow_job_info)
    else:
        history_task.update_one({"_id": task_info["_id"]}, {"$set": {"is_finished": 1}})
        task_dao.notify(task_info['task_info'])


def update_history_feature(global_task_id, date):
    """
    更新历史特征跑批子任务状态
    :return:
    """
    history_task_detail = db["history_task_detail"]
    history_task_detail.update_one({"global_task_id": global_task_id,
                                    "date": date}, {"$set": {"status": 2}})
