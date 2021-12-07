from app.main.db.mongo import db
from datetime import datetime
from typing import List
import pandas as pd
import akshare as ak


def get_oldest_k_line(code, level='day'):
    db_name = "k_line_" + level
    my_set = db[db_name]

    return list(my_set.find({"code": code}).sort("date", -1).limit(1))


def get_concept_oldest_k_line(name):
    db_name = "board_k_line"
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

def update_k_line(code, data):
    db_name = "k_line_day"
    my_set = db[db_name]

    for d in data:
        r = my_set.update({"code": code, "date": d['date']}, d, upsert=True)


def clear_k_line(level='week'):
    db_name = "k_line_" + level
    my_set = db[db_name]
    my_set.delete_many({})


def dump_board_k_line(data, level='day'):
    db_name = "board_k_line"
    my_set = db[db_name]

    if len(data) == 0:
        return

    return my_set.insert(data)


def update_board_k_line(name, date, data):
    db_name = "board_k_line"
    my_set = db[db_name]

    for d in data:
        r = my_set.update({"name": name, "date": d['date']}, d, upsert=True)


def get_k_line_by_code(code: List,
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
    db_name = "k_line_" + level
    my_set = db[db_name]

    query = my_set.find({"code": {"$in": code},
                         "date": {"$lte": end_day, "$gte": start_day}}) \
        .sort("date", 1)
    return list(query)


def get_k_line_data(
        start_day: datetime,
        end_day: datetime,
        level='day', codes=None) -> List:
    """
    获取特定时间的股票走势
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = "k_line_" + level
    my_set = db[db_name]
    query_set = {"date": {"$lte": end_day, "$gte": start_day}}
    if codes is not None:
        query_set['code'] = {"$in":codes}

    query = my_set \
        .find(query_set) \
        .sort("date", 1)
    return list(query)


def get_index_kline_data(
        start_day: datetime,
        end_day: datetime,
        level='day') -> List:
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
        .sort("date", 1)
    return list(query)


def get_board_k_line_data(
        name,
        start_day: datetime,
        end_day: datetime,
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
    data = pd.DataFrame(data[['日期', '开盘', '收盘', '最高', '最低', '成交量']])
    data.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
    data['name'] = str(name)
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
    data['create_time'] = datetime.now()
    return data


if __name__ == "__main__":
    r = get_k_line_by_code("300763", datetime(2021, 7, 28), datetime(2021, 8, 28))
    print(r)
