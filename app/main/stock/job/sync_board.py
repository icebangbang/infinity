from app.main.stock.api import stock_info, stock_board
import logging as log
import pymongo

from app.main.db.mongo import db
from app.main.stock.dao import stock_dao
import requests

"""
同步板块
"""
def sync_board():
    # myclient = pymongo.MongoClient("mongodb://admin:123456@101.37.24.40:20017/")
    # mydb = myclient["stock"]
    stock_detail = db["stock_detail"]
    board_detail = db["board_detail"]

    log.info("开始获取股票列表")
    stock_list = stock_info.get_stock_list()
    type_list = [1, 2, 3]

    for stock in stock_list:
        stock['board'] = list()

    stock_dict = {v['code']: v for v in stock_list}
    board_list = []

    for t in type_list:
        log.info("开始获取板块列表")
        boards = stock_board.get_board(t)
        log.info("总共有{}个板块".format(len(boards)))

        for index, board in enumerate(boards):
            label = board['板块名称']
            code = board['板块代码']
            board_dict = {"board": label, "code": code, "codes": list(), "type": t}
            board_list.append(board_dict)

            log.info("正在获取:{} {}".format(label, str(index)))
            mappings = stock_board.get_board_mapping(symbol_code=code)
            for mapping in mappings:
                if mapping['代码'] == '暂无成份股数据':
                    log.info("{} 暂无成分股数据".format(mapping['代码']))
                    continue
                if mapping['代码'] in stock_dict.keys():
                    board_dict["codes"].append(mapping['代码'])
                    stock_dict[mapping['代码']].get('board').append(label)
                else:
                    log.info("{}不在字典内".format(mapping['代码']))

    all_stock = stock_dao.get_all_stock()
    if all_stock and len(all_stock) > 0:
        for k, v in stock_dict.items():
            stock = stock_dao.get_one_stock(k)
            if stock is None:
                log.info("新增 {}".format(k))
                continue
            # 寻找差集
            log.info("查看 {} 的概念信息".format(stock['name']))
            diffs = list(set(v['board']).difference(set(stock['board'])))

            if len((diffs)) > 0:
                for diff in diffs:
                    headers = {'Content-Type': 'application/json'}
                    d = {"msgtype": "text",
                         "text": {
                             "content": "提醒:{}新增了新的概念:{}".format(k, diff)
                         }}
                    requests.post(
                        "https://oapi.dingtalk.com/robot/send?access_token=8d6107691edc8c68957ad9b3b3e16eeccf4fd2ec005c86692fdeb648da6312b4",
                        json=d, headers=headers)

    # 清空
    stock_detail.drop()
    board_detail.drop()

    x = stock_detail.insert_many(stock_dict.values())
    board_detail.insert_many(board_list)

    print(x.inserted_ids)

sync_board()
