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

    months = date_util.get_months_within_range(start, end)
    events: List[CalendarEvent] = [_get_delivery_date_of_stock_event(month) for month in months]

    return events


def _get_delivery_date_of_stock_event(date_time: datetime) -> CalendarEvent:
    # 第三周的周五
    target = date_util.get_date_with_offset(date_time, 3, 5)
    while True:
        if date_util.if_workday(target) is False:
            target = date_util.add_and_get_work_day(target, 1)

        return CalendarEvent(title="股指期货交割日", start=date_util.dt_to_str(target, "%Y-%m-%d"))


if __name__ == "__main__":
    get_fix_event(datetime.now())
