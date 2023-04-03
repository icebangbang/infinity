from app.celery_worker import celery, MyTask
from app.main.house.service import hangzhou
from app.main.stock.dao import stock_dao
from app.main.stock.service import fund_service

"""
板块数据同步
"""


@celery.task(bind=True, base=MyTask, expires=1800)
def sync_etf_kline(self):
    """
    同步etf基金的k线
    该方法会一次性etf基金历史时间内所有的k线数据
    如果调用方法的时候处于交易时间，将不会返回当日的盘中数据
    需要real_time去同步
    :param self:
    :return:
    """
    fund_service.sync_etf_kline()


@celery.task(bind=True, base=MyTask, expires=1800)
def sync_etf_kline_real_time(self):
    """
    同步etf基金的k线
    同步相关etf基金当日的盘中数据
    :param self:
    :return:
    """
    fund_service.sync_etf_kline_real_time()


@celery.task(bind=True, base=MyTask, expires=1800)
def stock_value_backtrading(self):
    stocks = stock_dao.get_stock_detail_list()
    fund_service.backtrading_stock_value(stocks, 4)
