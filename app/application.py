from flask import Flask

from app.log import init_log
from app.main.db.models import init_db
from config import config
from celery import Celery
from datetime import timedelta
from celery.schedules import crontab


app = None
celery = None


def create_app(config_name):
    """
    初始化数据库,路由,环境变量
    :param config_name: 环境变量对应的环境
    :return:
    """
    global app

    app = Flask(__name__)

    # 根据config_name选定环境变量
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    init_db(app)
    init_log(app)

    # init_all_blueprint(app)

    from app.main.rest import rest
    app.register_blueprint(rest)

    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    # celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery





