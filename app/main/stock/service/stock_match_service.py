"""
此服务用于获取优质的个股
"""
from datetime import datetime

import dateutil
import pandas as pd
from app.main.stock.dao import stock_training_picker_dao
from app.main.utils import date_util


def get_by_year(board, year, trend) -> list:
    """
    根据年份时间段获取板块上升期内优质的个股
    :return:
    """
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    records = stock_training_picker_dao.select_by_date(board, start, end,trend)
    df = pd.DataFrame(records)
    result = {}
    for start_scope,group in df.groupby("start_scope"):
        sorted_group_list = sorted(group.to_dict(orient="records"),key=lambda item: item['maximum_up'], reverse=True)
        r = []
        for sorted_group in sorted_group_list:
            simpled = {}
            simpled['code'] = sorted_group['code']
            simpled['maximum_up'] = sorted_group['maximum_up']
            simpled['name'] = sorted_group['name']
            simpled['maximum_rollback'] = sorted_group['maximum_rollback']
            r.append(simpled)

        result[date_util.dt_to_str(start_scope)] = r

    return result

