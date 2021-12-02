from app import application
import os

# 获取环境变量,
# pycharm启动可以在 RUN/DEBUG Configuration-Environment variables中添加FLASK_ENV
# 线上启动在 honeybee.sysconfig中指定
env = os.environ.get('FLASK_ENV') or 'development'
app = application.create_app(env)  # from .main.rest import rest as main_blueprint

celery = application.make_celery(app)


class MyTask(celery.Task): # celery 基类

    def on_success(self, retval, task_id, args, kwargs):
        # 执行成功的操作
        print('MyTasks 基类回调，任务执行成功')
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # 执行失败的操作
        # 任务执行失败，可以调用接口进行失败报警等操作
        print('MyTasks 基类回调，任务执行失败')
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)

