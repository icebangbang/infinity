from app.main.db.mongo import db
from datetime import datetime


def record_task(task_id, start_time=None):
    now = datetime.now()
    sync_record = db['sync_record']

    data = dict(end_time=now)
    if start_time is not None:
        data['start_time'] = start_time

    sync_record.update_one({"task_id": task_id}, {"$set": data}, upsert=True)


if __name__ == "__main__":
    record_task("111")
