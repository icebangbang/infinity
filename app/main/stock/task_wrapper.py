from app.main.constant import task_constant
from app.main.utils import my_redis
from app.main.db.mongo import db
from datetime import datetime
import logging

class TaskWrapper:

    def __init__(self, task_id, job_name, expect):
        """

        :param task_id:  任务id
        :param expect:  任务完结期待序号
        """
        self.task_id = task_id
        self.expect = expect
        self.job_name = job_name

    def trigger_count(self):
        count = my_redis.incr(self.task_id, 1)
        if count == self.expect:
            logging.info("count is {} equals expect".format(count))
            task_set = db['task_center']
            task_set.update({"task_id": self.task_id, "job_name": task_constant.TASK_SYNC_STOCK_IND},
                            {"$set": {"is_finished": 1, "update_time": datetime.now()}}, upsert=True)

            my_redis.delete(self.task_id)

