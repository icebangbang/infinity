# from app.main.stock.dao import board_dao
#
# boards = board_dao.get_all_board()
# # 获取最近一个交易日
#
# step = int(len(boards) / 8)
# boards = [boards[i:i + step] for i in range(0, len(boards), step)]
# # sync_data(boards)
# print(123)
# from app.main.stock.dao import stock_dao
# from app.main.stock.service import sync_kline_service

# sync_kline_service.sync_day_level('300763')

# stocks = stock_dao.get_all_stock()
# step = int(len(stocks) / 100)
# print(len(stocks))
# for i in range(0, len(stocks), step):
#     group = stocks[i:i + step]
#     print(len(group),i,i+step)
from app.main.stock.dao import stock_dao
import logging

num = 0


def transform_task(codes, deepth):

    if len(codes) <=20:
        global num
        num = num + len(codes)
        print(num,deepth)
        return

    step = int(len(codes) / 20)
    for i in range(0, len(codes), step):
        group = codes[i:i + step]
        print("拆分个股k线任务,时序{}".format(deepth))
        # i+step > len(stocks) 说明为最后一组

        transform_task(group, deepth + 1)






stocks = stock_dao.get_all_stock(dict(code=1, _id=0))

codes = [stock['code'] for stock in stocks]

transform_task(codes, 1)
