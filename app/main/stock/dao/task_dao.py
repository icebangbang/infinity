import importlib

from app.main.db.mongo import db
from datetime import datetime

from app.main.stock.job import job_config
from app.main.task import task_constant
from app.main.utils import my_redis
import json
import logging as log
import requests


def create_task(task_id, task_name, size, chain=None):
    now = datetime.now()
    sync_record = db['sync_record']

    data = dict(create_time=now, size=size, task_name=task_name, chain=chain)

    sync_record.update_one({"task_id": task_id, "task_name": task_name}, {"$set": data}, upsert=True)
    my_redis.set(task_id, size)


def update_task(task_id, size, task_name=None):
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
        if job_info is not None and job_info['job_type'] == task_constant.TASK_TYPE_CELERY:
            job_chain: list = job_info['job_chain']
            for job_path in job_chain:
                p, m = job_path.rsplit('.', 1)
                log.info("module {} m {}".format(p, m))
                method = getattr(importlib.import_module(p),
                                 m, None)
                next_kwargs = job_info['kwargs']

                next_kwargs = next_kwargs if next_kwargs is not None else dict(global_task_id=task_id)
                method.apply_async(kwargs=next_kwargs)
                sync_record.update_one({"task_id": task_id, "task_name": task_name},
                                       {"$set": {"update_time": now, "job_info": job_info, "is_finished": 1}})

        if job_info is not None and job_info['job_type'] == task_constant.TASK_TYPE_TASK_FLOW:
            notify(job_info)
        job_config.release_job(task_name)


def notify(job_info):
    global_id = job_info['global_id']
    callback_url = job_info['callback_url']
    task_name = job_info['task_name']
    resp = requests.post(callback_url, json=dict(executionId=global_id))

    is_finished = 0
    if resp.status_code == 200 and resp.json()['success'] is True:
        is_finished = 1
    sync_record = db['sync_record']
    sync_record.update_one({"task_id": global_id, "task_name": task_name},
                           {"$set": {"update_time": datetime.now(), "job_info": job_info, "is_finished": is_finished}})


if __name__ == "__main__":
    create_task("111")
