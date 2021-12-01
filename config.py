import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    OSS_KEY = os.environ.get("OSS_KEY") or 'LTAIixwjo1x8TpHE'
    OSS_SECRET = os.environ.get('OSS_SECRET') or '5P3YUaY9mLe7jDsb9012MdrhjdIQZR'
    OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT') or 'oss-cn-hangzhou.aliyuncs.com'
    OSS_BUCKET = os.environ.get('OSS_BUCKET') or 'honeybee'

    REDIS_HOST = os.environ.get('REDIS_HOST') or '10.10.10.200'
    REDIS_PORT = os.environ.get('REDIS_PORT') or '16379'
    REDIS_DB_ID = os.environ.get('REDIS_DB_ID') or 10
    REDIS_RQ_DB_ID = os.environ.get('REDIS_RQ_DB_ID') or 14
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD') or '123'
    MACHINE_ID = os.environ.get('MACHINE_ID') or 0
    MAAS_HOST = os.environ.get('MAAS_HOST') or 'http://10.10.10.200:8099'
    MUST_LOGIN = True
    ID_ENCRYPT = False
    PARALLEL_TASK_ON = False

    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://root:Cisco123@localhost:3306/maas_tool_v3'
    # 用于绑定所需要的数据库，否则默认加载SQLALCHEMY_DATABASE_URI该数据库
    # 当需要使用SQLALCHEMY_BINDS配置时，需要在modes.py中加入 __bind_key__ = 'rules'
    SQLALCHEMY_BINDS = {
        'rules': 'mysql+pymysql://root:Cisco123@10.10.10.200:33061/authority'
    }
    ENCRYPT_FIELD = ['id', 'model_project_id', 'experiment_id', 'algorithm_id', 'binning_id', 'project_id', 'source_id']

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
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB_ID = 10
    REDIS_PASSWORD = None

    MAAS_HOST = 'http://10.10.10.200:8099'



config = {
    'development': DevelopmentConfig,
}
