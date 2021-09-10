from app.main.db.mongo import db
from typing import List


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

if __name__ == "__main__":
    a = get_stock_bt_board("猪肉")