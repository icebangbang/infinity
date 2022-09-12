"""
业绩服务
"""
from app.main.db.mongo import db
from app.main.stock.dao import stock_dao
from app.main.stock.service import stock_service
from app.main.utils import date_util
from app.main.utils.date_util import WorkDayIterator, ReportTimeIterator
from datetime import datetime

def get_performance_size_info(start, end,    time_level = 'year'):
    """
    获取各个板块的趋势分组数据
    :return:
    """
    type = ['一季报', '中报', '三季报', '年报']

    board_detail = db['board_detail']
    boards = list(board_detail.find({"type": 2}))
    board_dict = {board['board']: board['size'] for board in boards}

    result_list = []

    config = db['config']
    board_info = config.find_one({"name": "board"}, {"_id": 0})
    another_boards = board_info['value']

    another_boards = list(board_detail.find({"board": {"$in": another_boards}}))

    for time_range in ReportTimeIterator(start, end, time_level):
        for another_board in another_boards:
            stock_profit = db['stock_profit']
            code_list = another_board['codes']
            stock_detail: dict = stock_dao.get_stock_detail_map(code_list)
            profits = list(stock_profit.find(
                {"date": time_range,
                 "code": {"$in": code_list}}, dict(PARENT_NETPROFIT=1, _id=0)))

            netprofit = 0
            new_netprofit = 0
            total_netprofit = 0

            for profit in profits:
                PARENT_NETPROFIT = profit["PARENT_NETPROFIT"]
                code = profit['code']
                stock = stock_detail[code]
                date = stock['date']
                if date_util.in_time_range(date, time_range, time_level):
                    # 该季度上市的
                    new_netprofit = new_netprofit + PARENT_NETPROFIT
                else:
                    netprofit = netprofit + PARENT_NETPROFIT
                total_netprofit = total_netprofit + PARENT_NETPROFIT


if __name__ == "__main__":
    get_performance_size_info(datetime(2010,12,31),datetime(2018,12,31))
