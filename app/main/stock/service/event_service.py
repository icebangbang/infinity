from datetime import datetime
from typing import List

from app.main.model.event import CalendarEvent
from app.main.utils import date_util


def get_fix_event(start: datetime, end: datetime) -> List[CalendarEvent]:
    """
    获取固定事件
    :param date_time:
    :return:
    """
    event_results = []

    months = date_util.get_months_within_range(start, end)

    """
    每月的第三个周五是股指交割日，第四个周三为期权交割日，
    在此时间段，特别是季末或年末，如指数在相对高位，权重股会有杀跌需求，指数在相对低位，权重股会有上涨需求
    """
    stock_events: List[CalendarEvent] = [_get_delivery_date_of_stock_event(month) for month in months]
    option_events: List[CalendarEvent] = [_get_delivery_date_of_option_event(month) for month in months]

    event_results.extend(stock_events)
    event_results.extend(option_events)

    return event_results


def _get_delivery_date_of_stock_event(date_time: datetime) -> CalendarEvent:
    """
    股指交割日
    :param date_time: 当月任意时间
    :return:
    """
    target = date_util.get_date_with_offset(date_time, 3, 5)
    while True:
        if date_util.if_workday(target) is False:
            target = date_util.add_and_get_work_day(target, 1)

        return CalendarEvent(title="股指交割日", start=date_util.dt_to_str(target, "%Y-%m-%d"))

def _get_delivery_date_of_option_event(date_time: datetime) -> CalendarEvent:
    """
    期权交割日
    :param date_time: 当月任意时间
    :return:
    """
    target = date_util.get_date_with_offset(date_time, 4, 3)
    if date_util.if_workday(target) is False:
            target = date_util.add_and_get_work_day(target, 1)

    return CalendarEvent(title="期权交割日", start=date_util.dt_to_str(target, "%Y-%m-%d"))


if __name__ == "__main__":
    get_fix_event(datetime.now())
