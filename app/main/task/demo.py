from app.celery_application import celery, MyTask
from app.main.db.mongo import db


@celery.task(bind=True, base=MyTask)
def parent(self):
    for i in range(3):
        sub.delay(i)


@celery.task(bind=True, base=MyTask)
def sub(self, b):
    print(b)
