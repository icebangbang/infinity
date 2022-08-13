import importlib

from app.main.db.mongo import db
from datetime import datetime

from app.main.stock.job import job_config
from app.main.utils import my_redis
import json
import logging as log


def create_task(task_id, task_path, size, chain=None):
    now = datetime.now()
    sync_record = db['sync_record']

    data = dict(create_time=now, size=size, task_path=task_path, chain=chain)

    sync_record.update_one({"task_id": task_id, "task_path": task_path}, {"$set": data}, upsert=True)
    my_redis.set(task_id, size)


def update_task(task_id, size, task_path=None, next_kwargs=None):
    i = my_redis.incrby(task_id, -size)
    log.info("{} {} try to update task,size {}".format(task_id, task_path, i))
    if i <= 0:
        now = datetime.now()
        sync_record = db['sync_record']

        chain_json = job_config.load_job_config(task_id)

        chain_obj = None
        if chain_json is not None:
            chain_obj = json.loads(chain_json)

        sync_record.update_one({"task_id": task_id, "task_path": task_path},
                               {"$set": {"update_time": now, "chain": chain_obj}})
        log.info("chain_" + task_id)
        if chain_obj is not None:
            job_chain: list = chain_obj['job_chain']
            for job_path in job_chain:
                p, m = job_path.rsplit('.', 1)
                log.info("module {} m {}".format(p, m))
                method = getattr(importlib.import_module(p),
                                 m, None)

                next_kwargs = next_kwargs if next_kwargs is not None else dict(global_task_id=task_id)
                method.apply_async(kwargs=next_kwargs)
    job_config.release_job(task_path)


if __name__ == "__main__":
    create_task("111")
