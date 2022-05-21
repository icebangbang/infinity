from app.main.stock.api import stock_info, stock_board
import logging as log
import pymongo

from app.main.db.mongo import db
from app.main.stock.dao import stock_dao
import requests

"""
同步板块
"""


def sync():
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
                code = mapping['代码']
                if code == '暂无成份股数据':
                    log.info("{} 暂无成分股数据".format(code))
                    continue
                if code in stock_dict.keys():
                    board_dict["codes"].append(code)
                    stock_dict[code].get('board').append(label)
                    # try:
                    #     web = stock_info.get_stock_web(stock_dict[code])
                    #     if web is not None:
                    #         stock_dict[code]['web'] = web
                    #     else:
                    #         print(code)
                    # except Exception as e:
                    #     print(e)
                else:
                    log.info("{}不在字典内".format(mapping['代码']))

    all_stock = stock_dao.get_all_stock()
    template = "提醒:{}新增了新的概念:{}"
    msg = ""
    if all_stock and len(all_stock) > 0:
        for k, v in stock_dict.items():
            v["name"] = v['name'].replace(" ", "")
            stock = stock_dao.get_one_stock(k)
            if stock is None:
                log.info("新增 {}".format(k))
                continue
            # 寻找差集
            log.info("查看 {} 的概念信息".format(stock['name']))
            diffs = list(set(v['board']).difference(set(stock['board'])))

            if len((diffs)) > 0:
                for diff in diffs:
                    if diff in ['融资融券', '昨日涨停', '昨日触板', '昨日涨停_含一字']:  continue
                    msg = template.format(k, diff) + "\n"
    headers = {'Content-Type': 'application/json'}
    d = {"msgtype": "text",
         "text": {
             "content": msg
         }}
    requests.post(
        "https://oapi.dingtalk.com/robot/send?access_token=8d6107691edc8c68957ad9b3b3e16eeccf4fd2ec005c86692fdeb648da6312b4",
        json=d, headers=headers)

    # 清空
    # stock_detail.drop()
    board_detail.drop()

    for value in stock_dict.values():
        stock_detail.update_one({"code": value['code']}, {"$set": value}, upsert=True)
    board_detail.insert_many(board_list)


if __name__ == "__main__":
    sync()
