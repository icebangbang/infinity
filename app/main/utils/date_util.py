from datetime import datetime, timedelta, date
from datetime import time
from chinese_calendar import is_workday
import time as tm


def utc_now():
    return datetime


def parse_date_time(dt_str, fmt="%Y-%m-%d %H:%M:%S") -> datetime:
    """
    解析时间
    :return:
    """
    if dt_str is None: return dt_str
    if not isinstance(dt_str,str): return dt_str

    time = datetime.strptime(dt_str, fmt)
    return time


def date_time_to_str(dt: datetime, fmt="%Y-%m-%d %H:%M:%S"):
    return dt.strftime(fmt)


def get_days_between(end: datetime, start: datetime) -> int:
    secokds = (get_start_of_day(end) - get_start_of_day(start)).total_seconds()

    return int(secokds / (24 * 60 * 60))


def get_start_of_day(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, dt.day)


def get_end_of_day(dt: datetime) -> datetime:
    return datetime.combine(dt, time.max)


def day_incr(dt: datetime, days):
    return dt + timedelta(days=days)


def dt_to_str(dt: datetime, fmt="%Y%m%d") -> str:
    if dt is None: return None
    return dt.strftime(fmt)


def get_friday_of_week():
    now = datetime.now()
    friday = datetime.now() + timedelta(days=4 - now.weekday())
    return friday


def to_timestamp(dt: datetime):
    """
    :param dt:
    :return:
    """
    if dt is None: return dt

    return int(tm.mktime(dt.timetuple()) * 1000.0 + dt.microsecond / 1000.0)


def from_timestamp(timestamp):
    timeStamp = float(timestamp) / 1000
    ret_datetime = datetime.fromtimestamp(timeStamp)
    return ret_datetime


def is_weekend(t) -> bool:
    return t.weekday() >= 5


def get_work_day(now, offset):
    """
    倒推工作日
    :param now:
    :param offset:
    :return:
    """
    i = 1
    while i <= offset:
        t = now - timedelta(days=i)
        if is_workday(t) is False or is_weekend(t):
            offset = offset + 1
        i = i + 1

    return get_start_of_day(now - timedelta(days=offset)), now

def add_and_get_work_day(now, offset):
    """
    正推工作日
    :param now:
    :param offset:
    :return:
    """
    i = 1
    while i <= offset:
        t = now + timedelta(days=i)
        if is_workday(t) is False or is_weekend(t):
            offset = offset + 1
        i = i + 1

    return get_start_of_day(now + timedelta(days=offset))


def if_workday(dt):
    '''
    判断是否为工作日
    '''
    Y = dt.year
    M = dt.month
    D = dt.day
    april_last = date(Y, M, D)
    return is_workday(april_last)


def is_valid_date(str):
    '''判断是否是一个有效的日期字符串'''
    try:
        datetime.strptime(str, "%Y-%m-%d")
        return True
    except:
        return False


if __name__ == "__main__":
    # d = parse_date_time("20210823212121", fmt="%Y%m%d%H%M%S")
    # d2 = parse_date_time("20210829121212", fmt="%Y%m%d%H%M%S")
    # print(get_friday_of_week())
    # now = datetime.now() - timedelta(days=10)
    # print(now.weekday())
    print(is_workday(datetime(2022, 10, 7)))
