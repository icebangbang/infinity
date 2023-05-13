import logging
from datetime import datetime, timedelta

import dateutil

from app.application import app
from app.main.stock.api import stock_kline
from app.main.stock.dao import k_line_dao
from app.main.utils import date_util


def sync_day_level(code, base_time=None, adjust='qfq'):
    """
    同步KLINE_TIME_WINDOW天内的数据
    :param code:
    :return:
    """
    point = k_line_dao.get_oldest_k_line(code,adjust=adjust)
    # default 1095
    time_window =1095 if app is None else app.config["KLINE_TIME_WINDOW"]

    if base_time is None:
        now = datetime.now()

    if len(point) == 0:
        before = now - timedelta(days=time_window)
    else:
        before = point[0]['date'] + timedelta(days=1)

    if date_util.get_days_between(now, before) <= 0:
        before = now

    df = stock_kline.fetch_kline_data(code,
                                      date_util.dt_to_str(before),
                                      date_util.dt_to_str(now), adjust)
    if df is None: return None

    data = df.to_dict(orient='records')

    if date_util.get_days_between(now, before) == 0:
        k_line_dao.update_k_line(code, data, adjust=adjust)
    else:
        k_line_dao.dump_k_line(data, adjust=adjust)


def sync_month_level(code, base_time=None, time_window=6000):
    """
    同步60天内的数据
    :param code:
    :return:
    """
    logging.info("[同步个股月k线]开始同步月线数据:{}".format(code))
    point = k_line_dao.get_oldest_k_line(code, level="month")
    now = datetime.now()
    end_of_current_month = date_util.get_end_of_month(now)
    if base_time is None:
        end_of_current_month = date_util.get_end_of_month(now)

    if len(point) == 0:
        before = end_of_current_month - timedelta(days=time_window)
    else:
        before = point[0]['date'] + dateutil.relativedelta.relativedelta(months=1)

    if date_util.get_days_between(end_of_current_month, before) <= 0:
        before = date_util.get_start_of_month(now)

    df = stock_kline.fetch_kline_data(code,
                                      date_util.dt_to_str(before),
                                      date_util.dt_to_str(end_of_current_month), 'qfq', '103')
    if df is None: return None

    data = df.to_dict(orient='records')
    k_line_dao.update_k_line(code, data, level='month')

    return data


def sync_week_level(code, start):
    """
    同步周k数据
    :param code:
    :return:
    """
    now = date_util.get_friday_of_week()

    df = stock_kline.fetch_kline_data(code,
                                      date_util.dt_to_str(start),
                                      date_util.dt_to_str(now), 'qfq')
    data = df.to_dict(orient='records')
    k_line_dao.dump_k_line(data, level="week")
    return data


def get_latest_valid_day():
    t = datetime.now()
    data = []
    while True:
        data = stock_kline.fetch_kline_data("000002",
                                            date_util.dt_to_str(t),
                                            date_util.dt_to_str(t), 'qfq')
        if len(data) > 0: return t
        t = t - timedelta(days=1)
    return t


def get_kline_of_stock(code, latest_valid_day, time_window=60):
    now = datetime.now()
    point = k_line_dao.get_oldest_k_line(code)
    if len(point) == 0:
        before = now - timedelta(days=time_window)
    else:
        before = date_util.parse_date_time(point[0]['date'], "%Y-%m-%d")

    if date_util.get_days_between(now, before) <= 0:
        return None


def sync_board_k_line(name, type, base_time=None, time_window=1095):
    """
    同步15天内的数据
    :param code:
    :return:
    """
    point = k_line_dao.get_concept_oldest_k_line(name)

    if base_time is None:
        now = datetime.now()

    if len(point) == 0:
        before = now - timedelta(days=time_window)
    else:
        before = point[0]['date'] + timedelta(days=1)
    if date_util.get_days_between(now, before) <= 0:
        before = now

    if before == now and not date_util.is_workday(before):
        return None

    df = k_line_dao.get_board_k_line_data(name,
                                          date_util.dt_to_str(before),
                                          date_util.dt_to_str(now))
    if df is None: return None

    df['type'] = type

    # if (before.hour >= 15):
    #     start = before + timedelta(days=1)
    # else:
    #     start = before
    data = df.to_dict(orient='records')

    if date_util.get_days_between(now, before) == 0:
        k_line_dao.update_board_k_line(name, datetime(now.year, now.month, now.day), data)
    else:
        k_line_dao.dump_board_k_line(data)
    return data


if __name__ == "__main__":
    # df = stock_kline.fetch_kline_data("600997",
    #                                   "20060101",
    #                                   "20070101", 'qfq')
    # data = df.to_dict(orient='records')
    # k_line_dao.dump_k_line(data)

    # df = k_line_dao.get_board_k_line_data('塑料制品',
    #                                       "20220601",
    #                                       "20220610")

    sync_day_level("600098")

    sync_month_level("300330")
    pass
