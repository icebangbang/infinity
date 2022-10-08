from datetime import datetime

import pandas as pd

from app.main.stock.dao import k_line_dao,board_dao
from app.main.utils import date_util
import logging
from app.main.db.mongo import db


def get_board_k_line_by_offset(from_date, to_date, concept_name,level='day'):
    db_name = "k_line_" + level
    my_set = db[db_name]
    board_dao.get_board_k_line_data_from_db(from_date, to_date, concept_name)
    daily_price = pd.DataFrame(board_dao.get_board_k_line_data_from_db(from_date, to_date,concept_names))

    daily_price = daily_price.set_index("date", drop=False)
    return daily_price

def publish(days=10, slice=30, code_list=None,stock_map={},start=None,end=None):
    if start is None and end is None:

        end = date_util.get_start_of_day(datetime.now())
        start = date_util.get_work_day(end,offset=days)

    boards = board_dao.get_all_board(type=[2])


    rise = []
    result_dict = dict()
    name_dict = dict()
    for stock in boards:
        name_dict[stock['board']] = stock['board']

    page_size = 200
    start_index = 0
    end_index = page_size
    flag = False

    while flag is False:
        logging.info("current index is {}".format(start_index))
        if end_index < len(boards):
            inner = boards[start_index:end_index]
            start_index = end_index
            end_index = end_index + page_size
        else:
            inner = boards[start_index:]
            flag = True
        temp_code_list = [item['board'] for item in inner]
        result_dict = {item['board']: [] for item in inner}
        k_list = board_dao.get_board_k_line_data_from_db( start, end,temp_code_list)
        for k in k_list:
            result_dict[k['name']].append(k)
        for k, v in result_dict.items():
            if len(v) > 0:
                if len(v) == 1:
                    earliest = v[0]["open"]
                    latest = v[0]["close"]
                    c = (latest - earliest) / earliest
                else:
                    earliest = v[0]["close"]
                    latest = v[-1:][0]["close"]
                    c = (latest - earliest) / earliest
                rise.append((k, name_dict[k], c))
        result_dict.clear()

    rise = pd.DataFrame(rise)
    rise.columns = ['code', 'name', 'rise']
    rise = rise.sort_values(by='rise', ascending=False)
    new = rise.to_dict("records")

    top = new[0:slice]

    rise = rise.sort_values(by='rise', ascending=True)
    new = rise.to_dict("records")

    bot = new[0:slice]

    print("涨幅前{}是:".format(slice))
    for i in top:
        print("{} {} {} {}".format(i['code'], i['name'], i['rise'],get_concepts(stock_map,i['code'])))

    print("跌幅前{}是:".format(slice))
    for i in bot:
        print("{} {} {} {}".format(i['code'], i['name'], i['rise'],get_concepts(stock_map,i['code'])))

def get_concepts(stock_map,code):
    if code in stock_map.keys():
        return stock_map[code]['board']
    return ""

def get_all_board()->dict:
    """
    获取板块数据,包括自定义板块
    :return:
    """
    config = db['config']
    board_info = config.find_one({"name": "board"}, {"_id": 0})
    board_custom = board_info['value']

    set = db['board_detail']
    condition1 = {"board": {"$in": board_custom}}
    condition2 = {"type": 2}
    boards_custom = list(set.find(condition1, dict(board=1, _id=0,codes=1)))
    boards = list(set.find(condition2, dict(board=1, _id=0,codes=1)))
    boards_custom.extend(boards)
    return boards_custom

def get_all_board_names():
    """
    获取板块数据,包括自定义板块
    :return:
    """
    boards = get_all_board()
    results = [board['board'] for board in boards]
    return results


if __name__ == "__main__":
    publish(2,100)