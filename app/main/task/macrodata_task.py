from app.celery_worker import celery, MyTask
from app.main.db.mongo import db
from app.main.stock.job import sync_indicator

@celery.task(bind=True, base=MyTask)
def sync(self):
    sync_indicator.sync_cpi()
    sync_indicator.sync_pmi()
    sync_indicator.sync_ppi()
    sync_indicator.sync_pig_data()
