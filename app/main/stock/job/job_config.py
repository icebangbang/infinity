from app.main.utils import my_redis, date_util
import json
import logging

log = logging.getLogger(__name__)


def check_status_available(task_path):
    """
    :param method: job方法名
    :return:
    """
    status = my_redis.get_bool("job_available_" + task_path)

    if status is None: return True

    return status


def acquire_job(task_path):
    """
    :param method: job方法名
    :return:
    """
    my_redis.set("job_available_" + task_path, False)


def release_job(task_path):
    """
    :param method: job方法名
    :return:
    """
    my_redis.set("job_available_" + task_path, True)
    my_redis.expire("job_available_" + task_path, 2 * 60 * 60)


def set_job_config(task_id, chain_job_config):
    config_json = json.dumps(chain_job_config, ensure_ascii=False)
    log.info("向缓存中写入配置:{},task_id:{}".format(config_json,task_id))
    my_redis.set("job_config" + str(task_id), config_json)
    my_redis.expire("job_config" + str(task_id), 60 * 60)


def load_job_config(task_id,**kwargs):
    config_json = my_redis.get("job_config" + str(task_id))
    log.info("从缓存中读取配置内容:{},task_id:{}".format(config_json, task_id))
    return config_json