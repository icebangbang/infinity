from flask import Flask

from app.log import init_log
from app.main.db.models import init_db
from config import config
from flask_docs import ApiDoc

# from app.main.rest import init_all_blueprint


app = None


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

    # 文档初始化
    ApiDoc(app)

    # init_all_blueprint(app)

    from app.main.rest import rest, auth, tr
    app.register_blueprint(rest)
    app.register_blueprint(auth)
    app.register_blueprint(tr)

    return app
