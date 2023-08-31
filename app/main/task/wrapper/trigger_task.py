from app.celery_application import celery, MyTask
from app.main.utils import simple_util


@celery.task(bind=True, base=MyTask, expires=1800)
def trigger(self,wrapper_path):
    clz = simple_util.get_method_by_path(wrapper_path)
    clz().split()
