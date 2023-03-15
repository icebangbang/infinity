"""
历史数据跑批任务
"""
import logging
from datetime import datetime

from app.celery_worker import celery, MyTask
from app.main.constant import task_constant
from app.main.db.mongo import db
from app.main.stock.dao import task_dao
from app.main.utils import date_util, collection_util, my_redis
from app.main.utils.date_util import WorkDayIterator

wait_minute_group = {
    "个股历史特征按批次跑批": 240,
    "保存趋势信息按批次跑批": 60,
    "个股历史趋势按批次跑批": 10
}

@celery.task(bind=True, base=MyTask, expire=1800)
def submit_agg_stock_trend_by_job(self, **kwargs):
    """
    板块趋势和成交额按批次聚合
    :param self:
    :param kwargs:
    :return:
    """
    _submit_history_job(kwargs, "板块趋势和成交额聚合")

@celery.task(bind=True, base=MyTask, expire=1800)
def submit_history_stock_trend_by_job(self, **kwargs):
    """
    个股历史趋势跑批
    :param self:
    :param kwargs:
    :return:
    """
    _submit_history_job(kwargs, "个股趋势跑批")


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
    _submit_history_job(kwargs, "个股特征跑批")


def _submit_history_job(input, sub_task_name):
    history_task = db["history_task"]
    history_task_detail = db["history_task_detail"]
    global_id = input['global_task_id']
    task_name = input['task_name']

    date_start = datetime(2018, 10, 1)

    now = datetime.now()
    days = date_util.get_days_between(now, date_start)
    logging.info("days span is {}".format(days))

    # 添加历史数据跑批任务的详情
    details = []
    index = 0
    for date in WorkDayIterator(date_start, now):
        index = index + 1
        details.append(dict(global_task_id=global_id,
                            task_name=task_name,
                            sub_task_name=sub_task_name,
                            date=date,
                            status=0,
                            index=index,
                            total=days,
                            create_time=datetime.now(),
                            update_time=datetime.now()))

    history_task_detail.insert_many(details)
    # 添加历史数据跑批任务
    seconds = wait_minute_group.get(task_name, 240)
    history_task.insert_one(dict(global_task_id=global_id,
                                 task_name=task_name,
                                 is_finished=0,
                                 create_time=datetime.now(),
                                 update_time=datetime.now(),
                                 wait_seconds=seconds,
                                 task_info=input))


@celery.task(bind=True, base=MyTask, expire=1800)
def start_stock_feature_task(self, **kwargs):
    """
    定时轮询表,然后发布任务
    :return:
    """
    # 任务等待间隔
    history_task = db["history_task"]
    history_task_detail = db["history_task_detail"]
    # "task_name": "个股历史特征按批次跑批"
    task_info_list = list(history_task.find({"is_finished": 0}))

    if collection_util.is_empty(task_info_list):
        return

    for task_info in task_info_list:
        wait_seconds = task_info.get("wait_seconds", 240)
        task_name = task_info['task_name']
        seconds = date_util.get_seconds_between(datetime.now(), task_info['update_time'])

        if seconds <= wait_seconds:
            # 保持间隔,不需要跑的太猛
            return

        # 这里可能会有重复执行
        global_task_id = task_info['global_task_id']
        if my_redis.acquire_redis_lock(global_task_id, global_task_id, ex_time=20) is False:
            logging.info("[{}}]获取任务锁失败,global_task_id:{}"
                         .format(task_name, global_task_id))
            return
        # 倒序排序，从最近的日期开始执行
        task_detail_list = list(history_task_detail.find({"global_task_id": global_task_id,
                                                          "status": {"$in": [0, 1]}}).sort("_id", -1))

        if collection_util.is_not_empty(task_detail_list):
            task_detail_item = task_detail_list[0]

            date = task_detail_item['date']
            index = task_detail_item['index']
            sub_task_name = task_detail_item['sub_task_name']
            seconds = date_util.get_seconds_between(datetime.now(), task_detail_item['update_time'])

            # 最近一个任务还在处理中,不做额外处理
            if task_detail_item['status'] == 1 and seconds <= wait_seconds:
                logging.info("[{}]已有运行中的历史特征任务，执行时间为{},当前index为{},共有{}"
                             .format(task_name, date_util.dt_to_str(date), index, len(task_detail_list)))
                return

            flow_job_info = task_info['task_info']
            flow_job_info['global_task_id'] = global_task_id
            flow_job_info['params'] = dict(
                from_date_ts=date_util.to_timestamp(date),
                end_date_ts=date_util.to_timestamp(date),
                global_task_id=global_task_id + "_" + str(index),
                job_type=task_constant.TASK_TYPE_HISTORY_TASK,
                callback_service="app.main.task.history_task.update_history_feature"
            )

            # stock_task.submit_stock_feature_by_job.apply_async(kwargs=flow_job_info)
            task_constant.TASK_MAPPING[sub_task_name].apply_async(kwargs=flow_job_info)

            logging.info("[{}]提交一历史特征任务，执行时间为{},当前index为{},共有{}"
                         .format(task_name, date_util.dt_to_str(date), index, len(task_detail_list)))
            # 将状态更新为处理中
            history_task_detail.update_one({"global_task_id": global_task_id, "index": index,
                                            "date": date}, {"$set": {"status": 1, "update_time": datetime.now()}})

        else:
            # 设置任务为已完成
            history_task.update_one({"_id": task_info["_id"]}, {"$set": {"is_finished": 1}})
            task_dao.notify(task_info['task_info'])

        my_redis.release_redis_lock(global_task_id, global_task_id)


def update_history_feature(job_params):
    """
    更新历史特征跑批子任务状态
    :return:
    """
    global_task_id = job_params['global_task_id'].split("_")[0]
    index = job_params['global_task_id'].split("_")[1]
    history_task_detail = db["history_task_detail"]
    history_task_detail.update_one({"global_task_id": global_task_id, "index": int(index)},
                                   {"$set": {"status": 2, "update_time": datetime.now()}})
    history_task = db["history_task"]
    history_task.update_one({"global_task_id": global_task_id},
                            {"$set": {"update_time": datetime.now()}})
