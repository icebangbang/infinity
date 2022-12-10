from app.celery_worker import celery, MyTask
from app.main.utils import simple_util


@celery.task(bind=True, base=MyTask, expires=1800)
def cpu_task(self,invoke_info):
    """

    :param self:
    :param path: 方法路径
    :return:
    """
    path = invoke_info['path']
    kwargs = invoke_info['kwargs']
    # 获取方法路径和参数，然后进行执行
    clz = simple_util.get_method_by_path(path)
    clz().invoke(**kwargs)

@celery.task(bind=True, base=MyTask, expires=1800)
def io_task(self,invoke_info):
    """

    :param self:
    :param path: 方法路径
    :return:
    """
    path = invoke_info['path']
    kwargs = invoke_info['kwargs']
    # 获取方法路径和参数，然后进行执行
    clz = simple_util.get_method_by_path(path)
    clz().invoke(**kwargs)


