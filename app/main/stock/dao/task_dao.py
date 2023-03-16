import importlib
import json
import logging
import logging as log
from datetime import datetime

import requests

from app.main.db.mongo import db
from app.main.stock.job import job_config
from app.main.constant import task_constant
from app.main.utils import my_redis, object_util


def finish_task(task_id):
    """
    直接更新
    :param task_id:
    :param task_name:
    :return:
    """
    job_json_info = job_config.load_job_config(task_id)
    if job_json_info is None:
        return
    job_info = json.loads(job_json_info)
    if job_info is not None and job_info['job_type'] == task_constant.TASK_TYPE_TASK_FLOW:
        notify(job_info)


def create_task(task_id, task_name, size, job_info=None):
    now = datetime.now()
    sync_record = db['sync_record']

    data = dict(create_time=now, size=size, task_name=task_name, job_info=job_info)

    sync_record.update_one({"task_id": task_id, "task_name": task_name}, {"$set": data}, upsert=True)
    my_redis.set(task_id, size)
    my_redis.expire(task_id, 60 * 60)


def update_task(task_id, size, task_name=None, job_params=None):
    i = my_redis.incrby(task_id, -size)
    log.info("{} {} try to update task,size {}".format(task_id, task_name, i))
    if i <= 0:
        now = datetime.now()
        sync_record = db['sync_record']

        job_json_info = job_config.load_job_config(task_id)

        job_info = None
        if job_json_info is not None:
            job_info = json.loads(job_json_info)
            log.info(job_json_info)
        log.info("chain_" + task_id)
        if job_info and job_info['job_type'] == task_constant.TASK_TYPE_CELERY:
            job_chain: list = job_info['job_chain']
            for job_path in job_chain:
                p, m = job_path.rsplit('.', 1)
                log.info("module {} m {}".format(p, m))
                method = getattr(importlib.import_module(p),
                                 m, None)
                next_kwargs = job_info.get('params', None)

                next_kwargs = next_kwargs if next_kwargs is not None else dict(global_task_id=task_id)
                method.apply_async(kwargs=next_kwargs)
                sync_record.update_one({"task_id": task_id, "task_name": task_name},
                                       {"$set": {"update_time": now, "job_info": job_info, "is_finished": 1}})

        if job_info and job_info['job_type'] == task_constant.TASK_TYPE_TASK_FLOW:
            notify(job_info)

        if job_info and job_info['job_type'] == task_constant.TASK_TYPE_HISTORY_TASK:
            service_callback(job_info)

        # 子任务内参数回调
        if job_params and job_params.get('job_type',-99) == task_constant.TASK_TYPE_HISTORY_TASK:
            # 历史数据跑批,执行本地服务回调
            service_callback(job_params)



        job_config.release_job(task_name)


def service_callback(job_params):
    logging.info("[celery异步任务回调]:{}".format(json.dumps(job_params)))
    callback_service = job_params['callback_service']

    # app.main.task.history_task.update_history_feature
    method = object_util.get_method_by_path(callback_service)
    # service回调
    method(job_params)


def notify(job_info):
    """
    http回调
    :param job_info:
    :return:
    """
    global_id = job_info['global_task_id']
    callback_url = job_info['callback_url']
    task_name = job_info['task_name']

    log.info("任务完成回调:global_id:{},任务信息:{}".format(global_id, json.dumps(job_info, ensure_ascii=False)))

    if callback_url is not None:
        resp = requests.post(callback_url, json=dict(globalId=global_id, taskName=task_name))

        is_finished = 0
        if resp.status_code == 200 and resp.json()['success'] is True:
            is_finished = 1
        sync_record = db['sync_record']
        sync_record.update_one({"task_id": global_id, "task_name": task_name},
                               {"$set": {"update_time": datetime.now(), "job_info": job_info, "is_finished": is_finished}},
                               upsert=True)

