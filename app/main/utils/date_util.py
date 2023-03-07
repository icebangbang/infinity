import time as tm
from datetime import datetime, timedelta, date
from datetime import time

import sxtwl
from chinese_calendar import is_workday
from dateutil.relativedelta import relativedelta

from app.main.yi.constant import jqmc, Gan, Zhi


def get_years(start: datetime, end: datetime):
    """
    获取时间区间涉及的年份
    :param start:
    :param end:
    :return:
    """
    year_start = start.year
    year_end = end.year

    return [year for year in range(year_start, year_end + 1)]


def get_report_day(dt: datetime):
    month = dt.month
    year = dt.year
    day = 30
    season = 1

    # 第二年的第一季度披露上一个季度的报告
    if 1 <= month <= 3:
        year = year - 1
        m = 12
        day = 31
        season = 4
    # 当年一季度的报告
    if 4 <= month <= 6:
        m = 3
        day = 31
        season = 1
    # 当年二季度的报告
    if 7 <= month <= 9:
        m = 6
        day = 30
        season = 1
    # 当年年三季度的报告
    if 10 <= month <= 12:
        m = 9
        day = 30
        season = 3

    return datetime(year, m, day), season


def is_same_day(day1: datetime, day2: datetime) -> bool:
    return day1.year == day2.year \
           and day1.month == day2.month \
           and day1.day == day2.day


def in_trade_time(time: datetime):
    """

    :param time:
    :param early: 提早时间
    :param delay: 延迟时间
    :return:
    """
    if is_weekend(time) or is_workday(time) is False:
        return False

    hour = time.hour
    min = time.minute
    mixed = hour + min / 60

    return 9.5 <= mixed <= 15


def in_trade_time_scope(time: datetime, early=0, delay=0):
    """
    设定交易的时间范围
    :param time:
    :param early: 提早时间
    :param delay: 延迟时间
    :return:
    """
    if is_weekend(time) or is_workday(time) is False:
        return False

    hour = time.hour
    min = time.minute
    mixed = hour + min / 60

    return 9.5 - early <= mixed <= 15 + delay or 11.5 + early <= mixed <= 13.5 - delay


def in_time_range(time: datetime, range: datetime, level):
    """
    判断是否在某个年度内,或者季节内
    :param time:
    :param range:
    :param level:
    :return:
    """
    if level == 'year':
        return time.year == range.year
    if level == 'season':
        start = range - timedelta(3)
        return start <= time <= range


def utc_now():
    return datetime


def parse_date_time(dt_str, fmt="%Y-%m-%d %H:%M:%S") -> datetime:
    """
    解析时间
    :return:
    """
    if dt_str is None or dt_str == '': return None
    if not isinstance(dt_str, str): return dt_str

    time = datetime.strptime(dt_str, fmt)
    return time


def date_time_to_str(dt: datetime, fmt="%Y-%m-%d %H:%M:%S"):
    return dt.strftime(fmt)


def get_days_between(end: datetime, start: datetime) -> int:
    seconds = (get_start_of_day(end) - get_start_of_day(start)).total_seconds()

    return int(seconds / (24 * 60 * 60))


def get_workdays_between(end: datetime, start: datetime) -> int:
    day = 0
    while True:
        workday = get_work_day(end, 1)
        day = day + 1
        end = workday
        if workday < start:
            return day


def get_seconds_between(end: datetime, start: datetime) -> int:
    """
    获取分钟的时间间隔
    :param end:
    :param start:
    :return:
    """
    seconds = (end - start).total_seconds()

    return int(seconds)


def get_minutes_between(end: datetime, start: datetime) -> int:
    """
    获取分钟的时间间隔
    :param end:
    :param start:
    :return:
    """
    seconds = (end - start).total_seconds()

    return int(seconds / 60)


def get_start_day_of_now():
    now = datetime.now()
    return datetime(now.year, now.month, now.day)


def get_start_of_day(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, dt.day)


def get_end_of_day(dt: datetime) -> datetime:
    return datetime.combine(dt, time.max)


def get_start_of_month(dt: datetime) -> datetime:
    month_start = datetime(dt.year, dt.month, 1)
    return month_start


def get_end_of_month(dt: datetime) -> datetime:
    month_end = datetime(dt.year, dt.month + 1, 1) - timedelta(days=1)
    return month_end


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


def from_timestamp(timestamp) -> datetime:
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

    return get_start_of_day(now - timedelta(days=offset))


def get_latest_work_day(base=None):
    """
    倒推工作日
    :param now:
    :param offset:
    :return:
    """
    base = datetime.now() if base is None else base
    d = get_start_of_day(base)
    while True:
        if is_workday(d) is False or is_weekend(d):
            d = d - timedelta(days=1)
        else:
            break
    return d


def add_and_get_work_day(now, offset):
    """
    正推工作日
    :param now:
    :param offset:
    :return:
    """
    i = 1
    t = now
    while i <= offset:
        t = t + timedelta(days=i)
        if is_workday(t) is False or is_weekend(t):
            offset = offset + 1
        i = i + 1

    return t


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


def get_week_start(t: datetime):
    """
    判断一周开始的时间
    :param t:
    :return:
    """
    index = t.weekday()
    span = index - 0
    start = t - timedelta(span)
    return get_start_of_day(start)


def get_week_end(t: datetime, if_work_day: bool = True):
    """

    :param t:
    :param if_work_day:
    :return:
    """
    i = 4 if if_work_day else 6

    index = t.weekday()

    span = index - i
    start = t - timedelta(span)
    return get_end_of_day(start)


def get_date_gz(date: datetime):
    """
    获取年月日时干支
    :return:
    """
    day = sxtwl.fromSolar(date.year, date.month, date.day)
    year_gz_index = day.getYearGZ()
    year_gz_str = Gan[year_gz_index.tg] + Zhi[year_gz_index.dz]
    # 月干支
    month_gz_index = day.getMonthGZ()
    month_gz_str = Gan[month_gz_index.tg] + Zhi[month_gz_index.dz]

    # 日干支
    day_gz_index = day.getDayGZ()
    day_gz_str = Gan[day_gz_index.tg] + Zhi[day_gz_index.dz]

    # 时干支
    # 第一个参数为该天的天干，第二个参数为小时
    hour_gz_index = sxtwl.getShiGz(year_gz_index.tg, date.hour)
    hour_gz_str = Gan[hour_gz_index.tg] + Zhi[hour_gz_index.dz]

    return year_gz_str + '-' + month_gz_str + '-' + day_gz_str + '-' + hour_gz_str

    # print("%d时天干地支:" % (hour), Gan[hTG.tg] + Zhi[hTG.dz])


def get_jq_list(start, end, ignore_time=True) -> list:
    """
    获取一定时间范围内的节气节点
    :param start:
    :param end:
    :param ignore_time:
    :return:
    """
    jq_list = []
    # lunar_start = datetime(now.year - 1, 10, 1)
    day = sxtwl.fromSolar(start.year, start.month, start.day)
    date = start
    while True:
        if day.hasJieQi():
            if date > end:
                break
            # if date.year != now.year:
            #     date = date + datetime.timedelta(1)
            #     day = lunar.getDayBySolar(date.year, date.month, date.day)
            #     continue
            qj_start_time = sxtwl.JD2DD(day.getJieQiJD())
            if ignore_time:
                jq_start = datetime(day.getSolarYear(), day.getSolarMonth(), day.getSolarDay())
            else:
                jq_start = datetime(day.getSolarYear(), day.getSolarMonth(), day.getSolarDay(),
                                    int(qj_start_time.h), int(qj_start_time.m),
                                    int(qj_start_time.s))
            jq_list.append(dict(time=jq_start, jq=jqmc[day.getJieQi()], jq_index=day.getJieQi()))

            # date = date + datetime.timedelta(1)
            # day = sxtwl.fromSolar(date.year, date.month, date.day)
        date = date + timedelta(1)
        day = sxtwl.fromSolar(date.year, date.month, date.day)

    if len(jq_list) > 0:
        jq_index = (len(jqmc) + jq_list[0]['jq_index'] - 1) % len(jqmc)
        new_jq_list = [dict(time=start, jq_index=jq_index, jq=jqmc[jq_index])]
        new_jq_list.extend(jq_list)
        return new_jq_list
    return jq_list


class WorkDayIterator(object):
    def __init__(self, start, end):
        self.date = start
        self.end = end

    def __iter__(self):
        return self

    def __next__(self):
        if self.date <= self.end:
            val = self.date
            self.date = add_and_get_work_day(val, 1)
            if is_workday(val) is not True:
                val = self.date
                self.date = add_and_get_work_day(val, 1)
            return val
        else:
            raise StopIteration


class ReportTimeIterator(object):
    def __init__(self, start, end, type):
        self.date = start
        self.end = end
        self.type = type

    def __iter__(self):
        return self

    def __next__(self):
        if self.date <= self.end:
            val = self.date
            if self.type == 'year':
                self.date = val + relativedelta(years=1)
            elif self.type == 'season':
                self.date = val + relativedelta(months=1)
            return val
        else:
            raise StopIteration


if __name__ == "__main__":
    print(get_report_day(datetime.now()))
    # d = parse_date_time("20210823212121", fmt="%Y%m%d%H%M%S")
    # d2 = parse_date_time("20210829121212", fmt="%Y%m%d%H%M%S")
    # print(get_friday_of_week())
    # now = datetime.now() - timedelta(days=10)
    # print(now.weekday())
    # print(is_workday(datetime(2022, 10, 7)))
    # print(get_week_start(datetime.now()))

    # values = WorkDayIterator(datetime(2022, 6, 1),datetime(2022, 6, 2))
    days = get_days_between(datetime.now(), datetime(2018, 6, 1))
    # for v in values:
    #     print(v, end=' ')

    # for value in YearIterator(2010, 2022):
    #     print(value)

    # jq_list = get_jq_list(datetime(2023, 2, 23), datetime(2023, 9, 1))
    # print(jq_list)

    date_start = datetime(2018, 10, 1)
    days = get_days_between(datetime.now(), date_start)

    for day in range(days):
        date_start = add_and_get_work_day(date_start, 1)

    print(date_start)
    # print([year for year in range(2012, 2014)])
