from app.application import app
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
    broker=app.config['CELERY_BROKER_URL']
)

celery.conf.update(
    result_expires=300,   # Celery结果存在中间件Redis的超时时间[仅针对当前的Celery的App]
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
        logging.info('MyTasks 基类回调，任务执行成功')
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # 执行失败的操作
        # 任务执行失败，可以调用接口进行失败报警等操作
        logging.info('MyTasks 基类回调，任务执行失败')
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)
