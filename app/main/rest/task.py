from app.main.stock.job import job_config
from app.main.utils import restful, date_util
from . import rest
from app.main.task import fund_task, task_constant
from flask import request
from app.main.utils import my_redis
from app import application
from app.main.rest import celery


@rest.route("/task/sync/boark_k_line/on", methods=['get'])
def send_job():
    switch = request.args.get("on", "false")
    my_redis.set("sync_after_15", switch)

    return restful.response("ok")


@rest.route("/task/sync/count", methods=['get'])
def test_incr():
    for i in range(1000):
        print(my_redis.incr("xx", 1))

    return restful.response("ok")


@rest.route("/task/sync/backtrading", methods=['get'])
def backtrading():
    fund_task.backtrading()
    return restful.response("ok")


@rest.route("/task/async/dispatch", methods=['post', 'get'])
def dispatch():
    """
    :return:
    """
    req = request.json
    global_task_id = req['globalId']
    callbackUrl = req['callbackUrl']

    date_start_str = req['start']
    date_end_str = req['end']

    date_start = date_util.parse_date_time(date_start_str)
    date_end = date_util.parse_date_time(date_end_str)

    flow_job_info = dict(
        task_name=req['taskName'],
        job_type=task_constant.TASK_TYPE_TASK_FLOW,
        callback_url=callbackUrl,
        kwargs=dict(from_date_ts=date_util.to_timestamp(date_start),
                    end_date_ts=date_util.to_timestamp(date_end),
                    from_date=date_start_str,
                    end_date=date_end_str,
                    global_task_id=global_task_id)
    )

    job_config.set_job_config(global_task_id, flow_job_info)

    method = task_constant.TASK_MAPPING[req['taskName']]
    method.apply_async(kwargs=flow_job_info)

    return restful.response("ok")
