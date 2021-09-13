from datetime import datetime,timedelta
from datetime import time


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

    return int(secokds/(24 * 60 * 60))


def get_start_of_day(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, dt.day)


def get_end_of_day(dt: datetime) -> datetime:
    return datetime.combine(dt, time.max)


def dt_to_str(dt: datetime, fmt="%Y%m%d") -> str:
    return dt.strftime(fmt)

def get_friday_of_week():
    now = datetime.now()
    friday = datetime.now() + timedelta(days=4 - now.weekday())
    return friday

def is_weekend(t)->bool:
    return t.weekday() >= 5


if __name__ == "__main__":
    # d = parse_date_time("20210823212121", fmt="%Y%m%d%H%M%S")
    # d2 = parse_date_time("20210829121212", fmt="%Y%m%d%H%M%S")
    print(get_friday_of_week())
    now = datetime.now()-timedelta(days=10)
    print(now.weekday())
