"""
股市全局数据统计和展示
"""
from typing import List

from flask import request

from app.main.utils import restful, date_util
from . import rest
from ..model.event import CalendarEvent
from ..stock.service import event_service


@rest.route("/calendar/event", methods=['post'])
def event():
    """
    报告数据概览
    :return:
    """
    request_body: dict = request.json
    start_str = request_body.get("start", date_util.get_current_str())
    end_str = request_body.get("end", date_util.get_current_str())
    start = date_util.parse_date_time(start_str, "%Y-%m-%d")
    end = date_util.parse_date_time(end_str, "%Y-%m-%d")

    events:List[CalendarEvent] = event_service.get_fix_event(start,end)

    for index, event in enumerate(events):
        event.id = index

    return restful.response(events)
