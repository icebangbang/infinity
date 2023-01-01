import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    REGISTERED_SERVER_TO_NACOS = True
    CELERY_CONFIG = "celeryconfig"
    KLINE_TIME_WINDOW = 2190

    @staticmethod
    def init_app(app):
        """
        自定义回调方法
        :param app:
        :return:
        """
        pass


class DevelopmentConfig(Config):
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
    REDIS_HOST = '39.105.104.215'
    REDIS_PORT = 30004
    REDIS_DB_ID = 1
    REDIS_PASSWORD = 'ironBackRedis123'

    BROKER_URL = 'redis://:ironBackRedis123@10.8.0.2:30004/1'
    RESULT_BACKEND = 'redis://:ironBackRedis123@10.8.0.2:30004/1'
    MONGO_URL = "mongodb://root:whosyourdaddy$879@39.105.104.215:20017/"


class TestConfig(Config):
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
    REDIS_HOST = '172.17.156.159'
    REDIS_PORT = 30004
    REDIS_DB_ID = 1
    REDIS_PASSWORD = 'ironBackRedis123'

    BROKER_URL = 'redis://:ironBackRedis123@10.8.0.2:30004/1'
    RESULT_BACKEND = 'redis://:ironBackRedis123@10.8.0.2:30004/1'
    MONGO_URL = "mongodb://root:whosyourdaddy$879@172.17.156.159:20017/"


class Offline(Config):
    """
    线下服务的配置
    """
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
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 30004
    REDIS_DB_ID = 1
    REDIS_PASSWORD = 'ironBackRedis123'

    BROKER_URL = 'redis://:ironBackRedis123@0.0.0.0:30004/1'
    RESULT_BACKEND = 'redis://:ironBackRedis123@0.0.0.0:30004/1'
    MONGO_URL = "mongodb://root:whosyourdaddy$879@172.16.1.184:20017/"

    CELERY_CONFIG = "celeryconfig_offline"
    KLINE_TIME_WINDOW = 7300


class Infinity(Config):
    """
    线下服务的配置
    """

    # REDIS_HOST = '10.10.10.200'
    # REDIS_PORT = 16379
    # REDIS_DB_ID = 10
    # REDIS_PASSWORD = '123'
    # MACHINE_ID = 0
    # 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 30004
    REDIS_DB_ID = 1
    REDIS_PASSWORD = 'ironBackRedis123'

    BROKER_URL = 'redis://:ironBackRedis123@0.0.0.0:30004/1'
    RESULT_BACKEND = 'redis://:ironBackRedis123@0.0.0.0:30004/1'
    MONGO_URL = "mongodb://root:whosyourdaddy$879@0.0.0.0:20017/"


class InfinityLocal(Config):
    """
    线下服务的配置
    """

    # REDIS_HOST = '10.10.10.200'
    # REDIS_PORT = 16379
    # REDIS_DB_ID = 10
    # REDIS_PASSWORD = '123'
    # MACHINE_ID = 0
    # 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    REDIS_HOST = '10.8.0.2'
    REDIS_PORT = 30004
    REDIS_DB_ID = 1
    REDIS_PASSWORD = 'ironBackRedis123'

    BROKER_URL = 'redis://:ironBackRedis123@10.8.0.2:30004/1'
    RESULT_BACKEND = 'redis://:ironBackRedis123@10.8.0.2:30004/1'
    MONGO_URL = "mongodb://root:whosyourdaddy$879@10.8.0.2:20017/"

    SERVER_HOST = "10.8.0.3"
    SERVER_PORT = 20060
    NACOS_SERVICE_NAME = "infinity"
    NACOS_CLUSTER_NAME = "DEFAULT"

    REGISTERED_SERVER_TO_NACOS = True
    NACOS_SERVER_ADDRESSES = "10.8.0.2:20048"
    NACOS_NAMESPACE = "public"
    IS_AUTH_MODE = False
    NACOS_WEIGHT = 1
    NACOS_HEARTBEAT_INTERVAL = 5


config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'offline': Offline,
    'infinity': Infinity,
    'infinityLocal': InfinityLocal
}
