from app.main.db.mongo import db
from typing import List
from  datetime import datetime


def get_all_board():
    my_set = db['board_detail']
    data = list(my_set.find({}))
    return data


def get_stock_bt_board(board) -> List[str]:
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
        ) -> List:
    """
    获取特定时间的股票走势
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = 'board_k_line'
    my_set = db[db_name]

    query = my_set\
        .find({"date": {"$lte": end_day, "$gte": start_day}})\
        .sort("date", 1)
    return list(query)

if __name__ == "__main__":
    a = get_stock_bt_board("猪肉")