from datetime import datetime, timedelta
from datetime import time
from chinese_calendar import is_workday


def utc_now():
    return datetime


def parse_date_time(dt_str, fmt="%Y-%m-%d %H:%M:%S") -> datetime:
    """
    解析时间
    :return:
    """
    time = datetime.strptime(dt_str, fmt)
    return time


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
    return dt.strftime(fmt)


def get_friday_of_week():
    now = datetime.now()
    friday = datetime.now() + timedelta(days=4 - now.weekday())
    return friday


def is_weekend(t) -> bool:
    return t.weekday() >= 5


def get_work_day(now, offset):
    i = 1
    while i <= offset:
        t = now - timedelta(days=i)
        if is_workday(t) is False or is_weekend(t):
            offset = offset + 1
        i = i + 1

    return now - timedelta(days=offset), now


if __name__ == "__main__":
    # d = parse_date_time("20210823212121", fmt="%Y%m%d%H%M%S")
    # d2 = parse_date_time("20210829121212", fmt="%Y%m%d%H%M%S")
    print(get_friday_of_week())
    now = datetime.now() - timedelta(days=10)
    print(now.weekday())
