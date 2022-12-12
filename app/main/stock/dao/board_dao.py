import pymongo

from app.main.db.mongo import db
from typing import List
from datetime import datetime

from app.main.stock.company import Company
from app.main.utils import date_util


def get_board_by_name(board_name):
    my_set = db['board_detail']
    data = my_set.find_one({"board": board_name})
    return data


def get_all_board(type=[1, 2, 3]):
    """
    根据类型获取东财所有的板块
    :param type:
    :return:
    """
    my_set = db['board_detail']
    data = list(my_set.find({"type": {"$in": type}}, dict(_id=0)))
    return data

def get_mixed_board():
    config = db['config']
    board_info = config.find_one({"name": "board"}, {"_id": 0})
    results = board_info['value']

    set = db['board_detail']
    condition = {"$or": [{"type": 2}]}
    boards = set.find(condition, dict(board=1, _id=0))
    results2 = [board['board'] for board in boards]
    results.extend(results2)
    return results


def get_stock_by_board(board) -> List[str]:
    """
    根据板块获取股票数据
    :param concept:
    :return:
    """
    my_set = db['board_detail']
    detail = my_set.find_one({"board": board})
    code_list = detail['codes']
    return code_list


def get_board_k_line_data_from_db(
        start_day: datetime,
        end_day: datetime,
        board_name: List = None
) -> List:
    """
    获取特定时间的股票走势
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = 'board_k_line_day'
    my_set = db[db_name]

    base = {"date": {"$lte": end_day, "$gte": start_day}}
    if board_name is not None:
        base["name"] = {"$in": board_name}

    query = my_set \
        .find(base) \
        .sort("date", 1)
    return list(query)


def dump_board_feature(companies: List[Company], date):
    start_of_day = date_util.get_start_of_day(date)

    my_set = db['board_feature']
    features = []
    update = []

    for company in companies:
        # features.append(dict(code=company.code, name=company.name, date=start_of_day, features=company.features))
        update.append(pymongo.UpdateMany({'name': company.name, 'date': start_of_day}, {"$set": {
            "name": company.name, "date": start_of_day, "features": company.features,
            "update": datetime.now()
        }}, True))
    my_set.bulk_write(update)


if __name__ == "__main__":
    # a = get_stock_by_board("猪肉")
    a = get_mixed_board()
    print(13)
