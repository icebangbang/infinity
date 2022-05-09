"""
指数相关
"""
import datetime
from typing import List

from app.main.db.mongo import db


def get_index_data_by_offset(
        base_day: datetime,
        offset: int,
        level='day', code=None,reverse_result=True) -> List:
    """
    因为有工作日,停牌等无法交易的日期,所以用时间范围筛选,可能会使得筛选的数据无法达到预期
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = "stock_index_k_line_" + level
    my_set = db[db_name]
    query_set = {}
    sort = -1
    if offset >= 0:
        query_set["date"]={"$gte": base_day}
        sort=1
    if offset < 0:
        query_set["date"]={"$lte": base_day}
        sort=-1
    if code is not None:
        query_set['code'] = code

    query = my_set \
        .find(query_set) \
        .sort("date", sort).limit(abs(offset))

    result = list(query)

    if reverse_result:
        result.reverse()

    return result