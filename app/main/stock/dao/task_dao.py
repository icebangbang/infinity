import importlib

from app.main.db.mongo import db
from datetime import datetime
from app.main.utils import my_redis
import json
import logging as log


def create_task(task_id, task_path, size, chain=None):
    now = datetime.now()
    sync_record = db['sync_record']

    data = dict(create_time=now, size=size, task_path=task_path, chain=chain)

    sync_record.update_one({"task_id": task_id, "task_path": task_path}, {"$set": data}, upsert=True)
    my_redis.set(task_id, size)

    if chain:
        my_redis.set("chain_" + task_id, json.dumps(chain))


def update_task(task_id, size, task_path=None, next_kwargs=None):
    i = my_redis.incrby(task_id, -size)
    if i <= 0:
        now = datetime.now()
        sync_record = db['sync_record']
        sync_record.update_one({"task_id": task_id, "task_path": task_path}, {"$set": {"update_time": now}})

        chain_json = my_redis.get("chain_" + task_id)
        log.info("chain_" + task_id)
        if chain_json is not None:
            chain: list = json.loads(chain_json)

            index = chain.index(task_path)
            if index == len(chain) - 1:
                return
            # 执行下一个任务
            next = chain[index + 1]
            p, m = next.rsplit('.', 1)
            log.info("module {} m {}".format(p, m))
            method = getattr(importlib.import_module(p),
                        m, None)

            next_kwargs = next_kwargs if next_kwargs is not None else dict(global_task_id=task_id)
            method.apply_async(kwargs=next_kwargs)


if __name__ == "__main__":
    create_task("111")
