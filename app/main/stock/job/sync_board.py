from app.main.stock import stock_board
from app.main.stock.api import stock_info
import logging as log
import pymongo
myclient = pymongo.MongoClient("mongodb://admin:123456@101.37.24.40:20017/")
mydb = myclient["stock"]
stock_detail = mydb["stock_detail"]
board_detail = mydb["board_detail"]

log.info("开始获取股票列表")
stock_list = stock_info.get_stock_list()
type_list = [1,2,3]

for stock in stock_list:
    stock['board'] = list()

stock_dict = {v['code']: v for v in stock_list}
board_list = []

for t in type_list:
    log.info("开始获取板块列表")
    boards = stock_board.get_board(t)
    log.info("总共有{}个板块".format(len(boards)))

    for index,board in enumerate(boards):
        label = board['板块名称']
        code = board['板块代码']
        board_dict = {"board":label,"code":code,"codes":list(),"type":t}
        board_list.append(board_dict)

        log.info("正在获取:{} {}".format(label,str(index)))
        mappings = stock_board.get_board_mapping(symbol_code =code )
        for mapping in mappings:
            if mapping['代码'] == '暂无成份股数据':
                log.info("{} 暂无成分股数据".format(mapping['代码']))
                continue
            if mapping['代码'] in stock_dict.keys():
                board_dict["codes"].append(mapping['代码'])
                stock_dict[mapping['代码']].get('board').append(label)
            else:
                log.info("{}不在字典内".format(mapping['代码']))

# 清空
stock_detail.remove()
board_detail.remove()

x = stock_detail.insert_many(stock_dict.values())
board_detail.insert_many(board_list)

print(x.inserted_ids)
