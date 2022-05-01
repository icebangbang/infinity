from app.celery_worker import celery, MyTask
from app.main.db.mongo import db
from app.main.stock.job import sync_indicator
from app.main.stock.service import report_service

@celery.task(bind=True, base=MyTask)
def sync(self):
    sync_indicator.sync_cpi()
    sync_indicator.sync_pmi()
    sync_indicator.sync_ppi()
    sync_indicator.sync_pig_data()

@celery.task(bind=True, base=MyTask)
def baotuan_update(self):
    report_service.baotuan_analysis()

@celery.task(bind=True, base=MyTask)
def market_status_analysis(self):
    report_service.market_status_analysis()
