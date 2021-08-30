from app.main.db.mongo import db
from datetime import datetime
from typing import List


def get_oldest_k_line(code, level='day'):
    db_name = "k_line_" + level
    my_set = db[db_name]

    return list(my_set.find({"code": code}).sort("date", -1).limit(1))


def dump_k_line(data, level='day'):
    db_name = "k_line_" + level
    my_set = db[db_name]

    if len(data) == 0:
        return

    return my_set.insert(data)


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

    query = my_set.find({"code": {"$in":code},
                         "date": {"$lte": end_day, "$gte": start_day}})\
        .sort("date", 1)
    return list(query)


def get_k_line_data(
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
    db_name = "k_line_" + level
    my_set = db[db_name]

    query = my_set\
        .find({"date": {"$lte": end_day, "$gte": start_day}})\
        .sort("date", 1)
    return list(query)


if __name__ == "__main__":
    r = get_k_line_by_code("300763", datetime(2021, 7, 28), datetime(2021, 8, 28))
    print(r)
