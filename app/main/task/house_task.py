from app.celery_application import celery, MyTask
from app.main.house.service import hangzhou

"""
板块数据同步
"""


@celery.task(bind=True, base=MyTask, expires=180)
def sync_hangzhou_house(self):
    hangzhou.sync_on_sale()
    hangzhou.sync_detail()
    hangzhou.sync_basic()
