from app.application import app,create_app
import os
from celery import Celery
import logging

# 获取环境变量,
# pycharm启动可以在 RUN/DEBUG Configuration-Environment variables中添加FLASK_ENV
# 线上启动在 honeybee.sysconfig中指定
# env = os.environ.get('FLASK_ENV') or 'development'
# app = application.create_app(env)  # from .main.rest import rest as main_blueprint

celery = Celery(
    app.import_name,
    backend=app.config['RESULT_BACKEND'],
    broker=app.config['BROKER_URL']
)

celery.config_from_object(app.config['CELERY_CONFIG'])

celery.conf.update(
    result_expires=3600,   # Celery结果存在中间件Redis的超时时间[仅针对当前的Celery的App]
    broker_heartbeat=10
)


# celery.conf.update(app.config)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask


class MyTask(celery.Task):  # celery 基类

    def on_success(self, retval, task_id, args, kwargs):
        # 执行成功的操作
        # logging.info('MyTasks 基类回调，任务执行成功')
        self.update_task(kwargs)
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # 执行失败的操作
        # 任务执行失败，可以调用接口进行失败报警等操作
        logging.info('MyTasks 基类回调，任务执行失败')
        self.update_task(kwargs)
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def get_size(self,kwargs:dict):
        keys = kwargs.keys()
        if "codes" in keys:
            return len(kwargs["codes"])
        if "boards" in keys:
            return len(kwargs["boards"])

    def update_task(self,kwargs):
        task_path = self.request.task

        from app.main.stock.dao import task_dao
        from app.main.task.task_constant import PATH_TASK_MAPPING

        if task_path in PATH_TASK_MAPPING.keys():
            global_task_id = kwargs['global_task_id']
            size = self.get_size(kwargs)
            task_dao.update_task(global_task_id, size, PATH_TASK_MAPPING.get(task_path),kwargs)

