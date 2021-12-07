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
