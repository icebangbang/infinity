import redis
from app.application import app
import logging as log
import pickle
import json


class RedisDBConfig:
    if app is not None:
        HOST = app.config['REDIS_HOST']
        PORT = app.config['REDIS_PORT']
        DBID = app.config['REDIS_DB_ID']
        PASSWORD = app.config['REDIS_PASSWORD']
    else:
        HOST = '39.105.104.215'
        PORT = 30004
        DBID = 1
        PASSWORD = 'ironBackRedis123'


def operator_status(func):
    """
    get operatoration status
    """

    def gen_status(*args, **kwargs):
        error, result = None, None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            error = str(e)
            log.error(error)

        return result
        # return {'result': result, 'error': error}

    return gen_status


class RedisCache(object):
    def __init__(self):
        if not hasattr(RedisCache, 'pool'):
            RedisCache.create_pool()
        self._connection = redis.StrictRedis(connection_pool=RedisCache.pool)

    @staticmethod
    def create_pool():
        RedisCache.pool = redis.ConnectionPool(
            host=RedisDBConfig.HOST,
            port=RedisDBConfig.PORT,
            db=RedisDBConfig.DBID,
            password=RedisDBConfig.PASSWORD,
            decode_responses=True)

    @operator_status
    def set_data(self, key, value):
        """
        set data with (key, value)
        """
        return self._connection.set(key, value)

    @operator_status
    def hset_data(self, key, skey, value):
        """
        set data with (key, value)
        """
        return self._connection.hset(key, skey, value)

    @operator_status
    def hget_all(self, key):
        """
        set data with (key, value)
        """
        return self._connection.hgetall(key)

    @operator_status
    def hget(self, key, skey):
        """
        set data with (key, value)
        """
        return self._connection.hget(key, skey)

    @operator_status
    def get_data(self, key):
        """
        get data by key
        """
        return self._connection.get(key)

    @operator_status
    def execute_command(self, *args, **options):
        """
        get data by key
        """
        "Execute a command and return a parsed response"
        pool = self._connection.connection_pool
        command_name = args[0]
        connection = pool.get_connection(command_name, **options)
        encoder = connection.encoder
        encoder.decode_responses = options['decode_responses']
        try:
            connection.send_command(*args)
            return self._connection.parse_response(connection, command_name, **options)
        except (ConnectionError, TimeoutError) as e:
            connection.disconnect()
            if not connection.retry_on_timeout and isinstance(e, TimeoutError):
                raise
            connection.send_command(*args)
            return self._connection.parse_response(connection, command_name, **options)
        finally:
            encoder.decode_responses = True
            pool.release(connection)

            # return self._connection.execute_command(*args, **options)

    @operator_status
    def del_data(self, *key):
        """
        delete cache by key
        """
        return self._connection.delete(*key)

    @operator_status
    def hdel(self, key, hkey):
        """
        delete cache by key
        """
        return self._connection.hdel(key, hkey)

    @operator_status
    def set_expire(self, key, time):
        """
        set expire by key
        """
        return self._connection.expire(key, time)

    @operator_status
    def r_push(self, key, value):
        """
        right push value to a list named "key"
        """
        return self._connection.rpush(key, value)

    @operator_status
    def l_range(self, key, start, end):
        return self._connection.lrange(key, start, end)

    @operator_status
    def incr(self, key, amount):
        return self._connection.incr(key, amount)\

    @operator_status
    def incrby(self, key, amount):
        return self._connection.incrby(key, amount)

    @operator_status
    def pipeline(self):
        return self._connection.pipeline()

    @operator_status
    def setnx(self, key, value):
        return self._connection.setnx(key, value)

    @operator_status
    def exists(self, key):
        return self._connection.exists(key)

    @operator_status
    def keys(self, pattern=None):
        pattern = "*" if pattern is None else pattern
        return self._connection.keys(pattern)


def get(key):
    return RedisCache().get_data(key)


def get_bool(key):
    r = RedisCache().get_data(key)
    if r is not None: return json.loads(r.lower())

    return r


def set(key, value):
    return RedisCache().set_data(key, value)


def hdel(key, hkey):
    return RedisCache().hdel(key, hkey)


def hset(key, hkey, value):
    return RedisCache().hset_data(key, hkey, value)


def hget_all(key):
    return RedisCache().hget_all(key)


def hget(key, skey):
    return RedisCache().hget(key, skey)


def delete(*key):
    return RedisCache().del_data(*key)


def execute_command(*args, **options):
    """
    get data by key
    """
    return RedisCache().execute_command(*args, **options)


def dump(key, value):
    set(key, pickle.dumps(value))


def r_push(key, value):
    return RedisCache().r_push(key, value)


def incr(key, value):
    return RedisCache().incr(key, value)

def incrby(key, value):
    return RedisCache().incrby(key, value)

def setnx(key, value):
    return RedisCache().setnx(key, value)


def l_range(key, start, end):
    return RedisCache().l_range(key, start, end)


def exists(key):
    return RedisCache().exists(key)


def load(key):
    try:
        data = execute_command('GET', key, decode_responses=False)
        if data is not None:
            return pickle.loads(data)
    except Exception as e:
        log.error(e, exc_info=1)
        return None


# 设置过期时间
def expire(key, time):
    return RedisCache().set_expire(key, time)


def keys(pattern=None):
    return RedisCache().keys(pattern)
