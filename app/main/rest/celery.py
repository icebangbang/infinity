import logging

from app.main.stock.dao import board_dao
from app.main.stock.job import sync_board
from app.main.utils import restful
from . import rest
from app.main.utils import date_util
from app.main.task import demo, trend_task
from app.main.task import board_task
from datetime import datetime, timedelta
from app.main.task import board_task, stock_task
from flask import request


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
    body = request.json
    date_start_str = body.get("start", None)
    date_end_str = body.get("end", None)

    if date_start_str is not None:
        date_start = date_util.parse_date_time(date_start_str, "%Y-%m-%d")
        date_end = date_util.parse_date_time(date_end_str, "%Y-%m-%d")
    else:
        date_start = datetime.now()
        date_end = datetime.now()

    trend_task.submit_trend_task.apply_async(
        args=[date_util.to_timestamp(date_start), date_util.to_timestamp(date_end)])

    return restful.response("ok")


@rest.route("/celery/stock/feature", methods=['post'])
def get_stock_feature():
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
