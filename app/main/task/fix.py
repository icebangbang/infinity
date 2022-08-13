from app.celery_worker import celery, MyTask
from app.main.house.service import hangzhou
from app.main.stock.dao import stock_dao
from app.main.stock.service import fund_service

"""
板块数据同步
"""


@celery.task(bind=True, base=MyTask, expires=1800)
def fix(self):
    stocks = stock_dao.get_stock_detail_list()
    fund_service.backtrading_stock_value(stocks, 4)
