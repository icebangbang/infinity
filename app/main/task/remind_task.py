from app.celery_worker import celery, MyTask
from app.main.db.mongo import db
from app.main.stock.service import stock_service
import requests
"""
板块数据同步
"""


@celery.task(bind=True, base=MyTask, expires=180)
def stock_remind(self):
    stock_service.stock_remind()
