import logging
import uuid

from app.main.stock.dao import board_dao
from app.main.stock.job import sync_board, job_config
from app.main.utils import restful
from . import rest
from app.main.utils import date_util
from app.main.task import demo, trend_task
from app.main.task import board_task
from datetime import datetime, timedelta
from app.main.task import board_task, stock_task,etf_task
from flask import request

@rest.route("/celery/stock/feature/rebuild", methods=['get'])
def rebuild_stock_feature():
    """
    重跑个股特征
    :return:
    """
    days=300
    logging.info("days span is {}".format(days))
    date_start = date_util.get_work_day(datetime.now(), days)
    for day in range(days):
        date_start = date_util.add_and_get_work_day(date_start, 1)
        logging.info("submit stock feature:{}".format(date_util.dt_to_str(date_start)))
        stock_task.submit_stock_feature.apply_async(args=[date_util.to_timestamp(date_start)])

    return restful.response("ok")

@rest.route("/celery/performance/profit", methods=['get'])
def performance_profit():
    """
    业绩数据拉取
    :return:
    """
    stock_task.sync_profit.apply_async(args=[])
    return restful.response("ok")

@rest.route("/celery/performance/sync_balance", methods=['get'])
def performance_sync_balance():
    """
    业绩数据拉取
    :return:
    """
    stock_task.sync_balance.apply_async(args=[])
    return restful.response("ok")

@rest.route("/celery/performance/cash_flow", methods=['get'])
def performance_cash_flow():
    """
    业绩数据拉取
    :return:
    """
    stock_task.sync_cash_flow.apply_async(args=[])
    return restful.response("ok")

@rest.route("/celery/performance/analysis_indicator", methods=['get'])
def performance_analysis_indicator():
    """
    业绩数据拉取
    :return:
    """

    stock_task.sync_analysis_indicator.apply_async(args=[])
    return restful.response("ok")

@rest.route("/celery/board", methods=['get'])
def maunlly():
    boards = board_dao.get_all_board()
    # 获取最近一个交易日

    step = int(len(boards) / 100)
    boards_group = [boards[i:i + step] for i in range(0, len(boards), step)]
    for index, boards in enumerate(boards_group):
        logging.info("提交同步任务,时序{}".format(index))
        board_task.sync_data.apply_async(args=[boards])

    return restful.response("ok")


@rest.route("/celery/stock/trend", methods=['post'])
def get_stock_trend():
    """
    个股趋势跑批
    fork get_trend_data_task方法
    :return:
    """
    body = request.json
    date_start_str = body.get("start", None)
    date_end_str = body.get("end", None)
    global_task_id = str(uuid.uuid1())

    if date_start_str is not None:
        date_start = date_util.parse_date_time(date_start_str, "%Y-%m-%d")
        date_end = date_util.parse_date_time(date_end_str, "%Y-%m-%d")
    else:
        date_start = datetime.now()
        date_end = datetime.now()

    chain_job_info = dict(
        job_chain=['app.main.task.trend_task.get_trend_data_task'],
        normal_chain=[],
        kwargs=dict(from_date_ts=date_util.to_timestamp(date_start),
                    end_date_ts=date_util.to_timestamp(date_end),
                    global_task_id=global_task_id)
    )
    job_config.set_job_config(global_task_id,chain_job_info)

    trend_task.submit_trend_task.apply_async(kwargs=dict(from_date=date_util.to_timestamp(date_start),
                    end_date=date_util.to_timestamp(date_end),
                    global_task_id=global_task_id))

    return restful.response("ok")


@rest.route("/celery/stock/feature", methods=['post'])
def get_stock_feature():
    """
    手动跑批个股特征
    :return:
    """
    body = request.json
    date_start_str = body.get("start", None)
    date_end_str = body.get("end", None)
    codes = body.get("codes", None)

    if date_start_str is not None:
        date_start = date_util.parse_date_time(date_start_str, "%Y-%m-%d")
        date_end = date_util.parse_date_time(date_end_str, "%Y-%m-%d")
    else:
        date_start = datetime.now()
        date_end = datetime.now()

    days = date_util.get_days_between(date_end, date_start)
    logging.info("days span is {}".format(days))
    if days == 0:
        logging.info("submit stock feature:{}".format(date_start_str))
        stock_task.submit_stock_feature(date_util.to_timestamp(date_start), codes)
    else:
        for day in range(days):
            date_start = date_start + timedelta(days=1)
            logging.info("submit stock feature:{}".format(date_util.dt_to_str(date_start)))
            stock_task.submit_stock_feature(date_util.to_timestamp(date_start), codes)

    return restful.response("ok")

@rest.route("/celery/stock/etf", methods=['post'])
def get_etf_feature():
    """
    手动跑批etf特征
    :return:
    """
    body = request.json
    date_start_str = body.get("start", None)
    date_end_str = body.get("end", None)
    codes = body.get("codes", None)

    if date_start_str is not None:
        date_start = date_util.parse_date_time(date_start_str, "%Y-%m-%d")
        date_end = date_util.parse_date_time(date_end_str, "%Y-%m-%d")
    else:
        date_start = datetime.now()
        date_end = datetime.now()

    days = date_util.get_days_between(date_end, date_start)
    logging.info("days span is {}".format(days))
    if days == 0:
        logging.info("submit etf feature:{}".format(date_start_str))
        etf_task.submit_etf_feature(date_util.to_timestamp(date_start), codes)
    else:
        for day in range(days):
            date_start = date_start + timedelta(days=1)
            logging.info("submit etf feature:{}".format(date_util.dt_to_str(date_start)))
            etf_task.submit_etf_feature(date_util.to_timestamp(date_start), codes)

    return restful.response("ok")


@rest.route("/celery/stock/data", methods=['post'])
def get_stock_data():
    """
    手动同步日k线数据
    :return:
    """
    stock_task.sync_stock_k_line.apply_async(args=[])
    return restful.response("ok")


@rest.route("/celery/stock/detail", methods=['post'])
def get_stock_detail():
    """
    手动同步个股详情
    :return:
    """
    sync_board.sync()
    return restful.response("ok")


@rest.route("/celery/board/feature", methods=['post'])
def get_board_feature():
    body = request.json
    date_start_str = body.get("start", None)
    date_end_str = body.get("end", None)

    if date_start_str is not None:
        date_start = date_util.parse_date_time(date_start_str, "%Y-%m-%d")
        date_end = date_util.parse_date_time(date_end_str, "%Y-%m-%d")
    else:
        date_start = datetime.now()
        date_end = datetime.now()

    days = date_util.get_days_between(date_end, date_start)
    logging.info("days span is {}".format(days))
    if days == 0:
        logging.info("submit stock feature:{}".format(date_start_str))
        board_task.submit_board_feature(date_util.to_timestamp(date_start))
    else:
        for day in range(days):
            date_start = date_start + timedelta(days=1)
            logging.info("submit stock feature:{}".format(date_util.dt_to_str(date_start)))
            board_task.submit_board_feature(date_util.to_timestamp(date_start))

    return restful.response("ok")
