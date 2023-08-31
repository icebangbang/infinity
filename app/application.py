import logging
import os

from flask import Flask
from ks_base import KsWebApplication

from app.log import init_log
from app.main.client.nacos import nacos_client
from app.main.db import models
from app.main.db import mongo
from config import config

log = logging.getLogger(__name__)

app = None
celery = None


class Application(KsWebApplication):

    # your code

    def set_web_app(self):
        static_path = os.getcwd() + os.path.sep + 'static'
        log.info("static file path: " + static_path)
        self.flask = Flask(__name__, static_folder=static_path)

    def start_job_and_service(self):
        log.info("Application:start_job_and_service")

    def load_db(self):
        mongo.init_db(self.flask)
        log.info("Application:load_db")

    def load_config(self):
        self.flask.config.from_object(config[self.env])
        # config[self.env].init_app(self.flask)

        if self.kwargs:
            for k, v in self.kwargs.items():
                if v is None: continue
                self.flask.config.__setitem__(k, v)
        log.info("Application:load_config")

    def instantiate_app_service(self):
        log.info("Application:instantiate_app_service")




def create_app_v2(config_name, **kwargs):
    global app
    static_path = os.getcwd() + os.path.sep + 'static'
    log.info("static file path: " + static_path)
    app = Flask(__name__, static_folder=static_path)
    init_log()
    application = Application(app,config_name, **kwargs)

    return application


def create_app(config_name, **kwargs):
    """
    初始化数据库,路由,环境变量
    :param config_name: 环境变量对应的环境
    :return:
    """
    global app

    app = Flask(__name__)

    # 根据config_name选定环境变量
    app.config.from_object(config[config_name])

    if kwargs is not None:
        for k, v in kwargs.items():
            if v is None: continue
            app.config.__setitem__(k, v)

    config[config_name].init_app(app)
    models.init_db(app)
    init_log(app)
    mongo.init_db(app)
    # init_all_blueprint(app)

    from app.main.rest import rest
    app.register_blueprint(rest)

    nacos_client.init(app)

    return app
