from flask import Flask

from app.log import init_log
from app.main.db import models
from app.main.db import mongo
from config import config
from datetime import timedelta


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
    models.init_db(app)
    init_log(app)
    mongo.init_db(app)

    # init_all_blueprint(app)



    from app.main.rest import rest
    app.register_blueprint(rest)

    return app





