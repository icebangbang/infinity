from datetime import datetime

from flask import request

from app.main.rest import rest
from app.main.utils import restful, date_util
from app.main.utils.date_util import WorkDayIterator


@rest.route("/common/query/workday", methods=['post'])
def display_work_day():
    """
    根据区间查询工作日
    """
    params: dict = request.json
    start = params.get("start")
    end = params.get("end")
    start = date_util.parse_date_time(start,fmt="%Y-%m-%d")
    end = date_util.parse_date_time(end,fmt="%Y-%m-%d")

    results = []
    now = datetime.now()
    for date in WorkDayIterator(start, end):
        if (date >= date_util.get_start_of_day(now)):
            continue
        results.append(date)

    return restful.response(results)
