from datetime import datetime
from typing import List

from app.main.db.mongo import db
from app.main.model.event import CalendarEvent
from app.main.utils import date_util, simple_util


def get_from_db(start: datetime, end: datetime) -> List[CalendarEvent]:
    calendar_event = db['calendar_event']
    events = list(calendar_event.find({"start": {"$gte": start, "$lte": end}}, {"_id": 0}))
    # for event in events:
    #     event['start'] = date_util.dt_to_str(event['start'],"%Y-%m-%d")
    events = [CalendarEvent(**event) for event in events]
    return events


def get_fix_event(start: datetime, end: datetime) -> List[CalendarEvent]:
    """
    获取固定事件
    :param start:
    :param end:
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
    lpr_events: List[CalendarEvent] = [_get_lpr_push_event(month) for month in months]

    event_results.extend(stock_events)
    event_results.extend(option_events)
    event_results.extend(lpr_events)

    return event_results


def _get_lpr_push_event(date_time: datetime) -> CalendarEvent:
    """
    lpr公布时间，每个月20号
    :return:
    """
    year = date_time.year
    month = date_time.month
    lpr_date = datetime(year, month, 20, 9, 15, 0)
    lpr_date = date_util.stop_until_work_day(lpr_date)
    return CalendarEvent(title="LPR公布日", start=date_util.dt_to_str(lpr_date, "%Y-%m-%d %H:%M:%S"))


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
    import pandas as pd

    path = simple_util.get_root_path()
    r = pd.read_excel(path + "app/static/doc/2023年国家统计局主要统计信息发布日程表.xlsx")
    results = r.to_dict(orient="records")
    new = list()

    for index, result in enumerate(results):
        if index % 2 == 0:
            for k, v in result.items():
                if "/" in v:
                    result[k] = "2023-" + k.replace("月", "-") + v[0:v.index("/")]
                if '……' in v:
                    result[k] = None
        if index % 2 == 1:
            for k, v in result.items():
                if ":" in v:
                    results[index - 1][k] = results[index - 1][k] + " {}:00".format(v)

    for index, result in enumerate(results):
        if index % 2 == 0 and index != 32:
            new.append(results[index])

    events = []

    for row in new:
        title = row['内容']
        for k, v in row.items():
            if "月" in k and v is not None:
                event = dict(title=title, start=v, source="国家统计局")
                events.append(event)
    r = pd.DataFrame(events)
    r.to_csv(path + "app/static/events/2023年国家统计局主要统计信息发布日程表.csv", index=False, encoding='utf-8')

    for event in events:
        event['start'] = date_util.parse_date_time(event['start'], "%Y-%m-%d %H:%M:%S")
        db['calendar_event'].update_one({"title": event['title'],
                                         "start": date_util.parse_date_time(event['start'], "%Y-%m-%d %H:%M:%S"),
                                         }, {"$set": event}, upsert=True)
