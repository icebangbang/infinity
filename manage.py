from app import application
import os
from celery.schedules import crontab

# 获取环境变量,
# pycharm启动可以在 RUN/DEBUG Configuration-Environment variables中添加FLASK_ENV
# 线上启动在 honeybee.sysconfig中指定
env = os.environ.get('FLASK_ENV') or 'development'
app = application.create_app(env)  # from .main.rest import rest as main_blueprint

from app.celery_worker import celery


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8192, debug=True, use_reloader=False, threaded=True)
