from app.main.stock.dao import k_line_dao
from datetime import datetime, timedelta
from app.main.utils import date_util
from app.main.stock import stock_kline


def sync_day_level(code, base_time = None,time_window=60):
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
        before = point[0]['create_time']

    if date_util.get_days_between(now, before) <= 0:
        return None

    if (before.hour >=15):
        start = before + timedelta(days=1)
    else:
        start = before

    df = stock_kline.fetch_kline_data(code,
                                      date_util.dt_to_str(start),
                                      date_util.dt_to_str(now), 'qfq')
    data = df.to_dict(orient='records')
    k_line_dao.dump_k_line(data)
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

def get_kline_of_stock(code,latest_valid_day,time_window=60):
    now = datetime.now()
    point = k_line_dao.get_oldest_k_line(code)
    if len(point) == 0:
        before = now - timedelta(days=time_window)
    else:
        before = date_util.parse_date_time(point[0]['date'], "%Y-%m-%d")

    if date_util.get_days_between(now, before) <= 0:
        return None


if __name__ == "__main__":
    a = sync_day_level("300763", "xx")
