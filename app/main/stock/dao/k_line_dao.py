from datetime import datetime
from typing import List

import akshare as ak
import pandas as pd

from app.main.db.mongo import db
from app.main.utils import collection_util


def get_earliest_k_line(code="000001",level='day'):
    """
    获取最早的k线数据点
    :param code:
    :param level:
    :return:
    """
    db_name = "k_line_" + level
    my_set = db[db_name]

    points = list(my_set.find({"code": code}).sort("date", 1).limit(1))
    if collection_util.is_not_empty(points):
        return points[0]
    return None

def get_oldest_k_line(code, level='day'):
    """
    获取最近的k线
    :param code:
    :param level:
    :return:
    """
    db_name = "k_line_" + level
    my_set = db[db_name]

    return list(my_set.find({"code": code}).sort("date", -1).limit(1))


def get_concept_oldest_k_line(name):
    db_name = "board_k_line_day"
    my_set = db[db_name]

    return list(my_set.find({"name": name}).sort("_id", -1).limit(1))


def dump_k_line(data, level='day'):
    """
    存储个股日k
    :param data:
    :param level:
    :return:
    """
    db_name = "k_line_" + level
    my_set = db[db_name]

    if len(data) == 0:
        return

    return my_set.insert(data)


def update_k_line(code, data, level="day"):
    db_name = "k_line_" + level
    my_set = db[db_name]

    for d in data:
        r = my_set.update({"code": code, "date": d['date']}, d, upsert=True)


def clear_k_line(level='week'):
    db_name = "k_line_" + level
    my_set = db[db_name]
    my_set.delete_many({})


def dump_board_k_line(data, level='day'):
    db_name = "board_k_line_day"
    my_set = db[db_name]

    if len(data) == 0:
        return

    return my_set.insert(data)


def update_board_k_line(name, date, data):
    db_name = "board_k_line_day"
    my_set = db[db_name]

    for d in data:
        r = my_set.update({"name": name, "date": d['date']}, d, upsert=True)


def get_k_line_by_code(code: List,
                       start_day: datetime = None,
                       end_day: datetime = None,
                       level='day',
                       limit=None,
                       sort=1):
    """
    获取特定时间和代码的股票走势
    :param code:
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = "k_line_" + level
    my_set = db[db_name]

    filter = {"code": {"$in": code}}

    if start_day is not None and end_day is not None:
        filter['date'] = {"$lte": end_day, "$gte": start_day}

    query = my_set.find(filter) \
        .sort("date", sort)

    if limit is not None:
        query = query.limit(limit)
    return list(query)


def get_board_k_line_by_name(name: List,
                             start_day: datetime,
                             end_day: datetime,
                             level='day'):
    """
    获取特定时间和代码的股票走势
    :param code:
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = "board_k_line_day"
    my_set = db[db_name]

    query = my_set.find({"name": {"$in": name},
                         "date": {"$lte": end_day, "$gte": start_day}}) \
        .sort("date", 1)
    return list(query)


def get_k_line_data(
        start_day: datetime,
        end_day: datetime,
        level='day', codes=None, sort=1) -> List:
    """
    获取特定时间的股票走势
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = "k_line_" + level
    my_set = db[db_name]
    query_set = {"date": {"$gte": start_day, "$lte": end_day}}
    if codes is not None:
        query_set['code'] = {"$in": codes}

    query = my_set \
        .find(query_set) \
        .sort("date", sort)
    return list(query)


def get_k_line_data_point(
        code: str,
        date: datetime,
        level='day', ) -> dict:
    """
    获取特定时间的股票走势
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = "k_line_" + level
    my_set = db[db_name]

    result = my_set.find_one({"date": date, "code": code})

    return result


def get_k_line_data_by_offset(
        base_day: datetime,
        offset: int,
        level='day',
        table_name="k_line",
        key="code",
        code=None, reverse_result=True) -> List:
    """
    因为有工作日,停牌等无法交易的日期,所以用时间范围筛选,可能会使得筛选的数据无法达到预期
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = table_name + "_" + level
    my_set = db[db_name]
    query_set = {}
    sort = -1
    if offset >= 0:
        query_set["date"] = {"$gte": base_day}
        sort = 1
    if offset < 0:
        query_set["date"] = {"$lte": base_day}
        sort = -1
    if code is not None:
        query_set[key] = code

    query = my_set \
        .find(query_set) \
        .sort("date", sort).limit(abs(offset))

    result = list(query)

    if reverse_result:
        result.reverse()

    return result


def get_index_kline_data(
        start_day: datetime,
        end_day: datetime,
        level='day', sort=1) -> List:
    """
    获取特定时间的股票走势
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = "stock_index_k_line_" + level
    my_set = db[db_name]

    query = my_set \
        .find({"date": {"$lte": end_day, "$gte": start_day}}) \
        .sort("date", sort)
    return list(query)


def get_board_k_line_data(
        name,
        start_day: str,
        end_day: str,
) -> List:
    """
    获取特定时间的股票走势
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    data = \
        ak.stock_board_concept_hist_em(
            symbol=name,
            beg=start_day,
            end=end_day)
    if data is None or len(data) <= 0:
        return None
    data = pd.DataFrame(data[['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '最近收盘']])
    data.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'money', 'prev_close']
    data['name'] = str(name)
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
    data['create_time'] = datetime.now()
    return data


if __name__ == "__main__":
    r = get_k_line_data_by_offset(datetime(2009, 3, 4),
                                  offset=-251, codes=['600556'])
    print(r)
