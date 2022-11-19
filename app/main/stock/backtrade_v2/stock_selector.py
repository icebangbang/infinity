from datetime import datetime
from typing import List

from app.main.stock.dao import k_line_dao, stock_dao

"""
个股选择器
"""


class RecommendStock:

    def __init__(self, code, name, price, date):
        self.code = code
        self.name = name
        self.price = price
        self.date = date
        self.motivation = "开仓"


class StockSelector:

    def select(self, date: datetime) -> List:
        recommend_stock_list = list()

        point = k_line_dao.get_k_line_data_point("300763",date)
        detail = stock_dao.get_one_stock(point['code'])
        recommend = RecommendStock(point['code'], detail['name'], point['close'], date)

        recommend_stock_list.append(recommend)

        return recommend_stock_list
