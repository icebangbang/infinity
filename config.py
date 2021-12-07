import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    @staticmethod
    def init_app(app):
        """
        自定义回调方法
        :param app:
        :return:
        """
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://root:Cisco123@10.10.10.200:33061/maas_tool_v3'
    # 用于绑定所需要的数据库，否则默认加载SQLALCHEMY_DATABASE_URI该数据库
    # 当需要使用SQLALCHEMY_BINDS配置时，需要在modes.py中加入 列如：__bind_key__ = 'rules'
    SQLALCHEMY_BINDS = {
        # 'rules': 'mysql+pymysql://root:123456@127.0.0.1:3306/test'
        'rules': 'mysql+pymysql://root:Cisco123@10.10.10.200:33061/authority'
    }

    # REDIS_HOST = '10.10.10.200'
    # REDIS_PORT = 16379
    # REDIS_DB_ID = 10
    # REDIS_PASSWORD = '123'
    # MACHINE_ID = 0
    # 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    REDIS_HOST = '172.16.1.184'
    REDIS_PORT = 30004
    REDIS_DB_ID = 1
    REDIS_PASSWORD = 'ironBackRedis123'

    CELERY_BROKER_URL = 'redis://:ironBackRedis123@172.16.1.184:30004/1'
    RESULT_BACKEND = 'redis://:ironBackRedis123@172.16.1.184:30004/1'



config = {
    'development': DevelopmentConfig,
}
