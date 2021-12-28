from app.main.stock.dao import k_line_dao
from datetime import datetime, timedelta
from app.main.utils import date_util
from app.main.stock import stock_kline
import pandas as pd


def sync_day_level(code, base_time=None, time_window=1095):
    """
    同步60天内的数据
    :param code:
    :return:
    """
    point = k_line_dao.get_oldest_k_line(code)

    if base_time is None:
        now = datetime.now()

    if len(point) == 0:
        before = now - timedelta(days=time_window)
    else:
        before = point[0]['date']+timedelta(days=1)

    if date_util.get_days_between(now, before) <= 0:
        before = now

    df = stock_kline.fetch_kline_data(code,
                                      date_util.dt_to_str(before),
                                      date_util.dt_to_str(now), 'qfq')
    if df is None: return None

    data = df.to_dict(orient='records')

    if date_util.get_days_between(now, before) == 0:
        k_line_dao.update_k_line(code,data)
    else:
        k_line_dao.dump_k_line(data)





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
    k_line_dao.dump_k_line(data,level="week")
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


def sync_board_k_line(name, type,base_time=None, time_window=1095):
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
        before = point[0]['date']+timedelta(days=1)
    if date_util.get_days_between(now, before) <= 0:
        before = now
    # if date_util.get_days_between(now, before) == 0:
    #     return None

    df = k_line_dao.get_board_k_line_data(name,
                                          date_util.dt_to_str(before),
                                          date_util.dt_to_str(now))
    df['type'] = type

    # if (before.hour >= 15):
    #     start = before + timedelta(days=1)
    # else:
    #     start = before
    data = df.to_dict(orient='records')

    if date_util.get_days_between(now, before) == 0:
        k_line_dao.update_board_k_line(name,datetime(now.year,now.month,now.day),data)
    else:
        k_line_dao.dump_board_k_line(data)
    return data


def get_stock_k_line(from_date, to_date, codes=None):
    if codes is None:
        daily_price = pd.DataFrame(k_line_dao.get_k_line_data(from_date, to_date))
    else:
        daily_price = pd.DataFrame(k_line_dao.get_k_line_by_code(codes, from_date, to_date))

    return daily_price


if __name__ == "__main__":

    df = stock_kline.fetch_kline_data("600997",
                                      "20060101",
                                      "20070101", 'qfq')
    data = df.to_dict(orient='records')
    k_line_dao.dump_k_line(data)
