from datetime import datetime

from pandas import DataFrame

from app.main.utils.date_util import WorkDayIterator
from app.main.stock.backtrade_v2.stock_holding import StockHolding
from typing import Dict

class Core:
    data: DataFrame
    holding:Dict[str,StockHolding] = dict()
    buy_strategy = None
    sell_strategy = None
    date_range = []

    def set_trader(self, trader):
        self.trader = trader

    def init(self, trader, **kwargs):
        self.buy_strategy_instance = kwargs['buy_strategy'](self)
        self.sell_strategy_instance = kwargs['sell_strategy'](self)
        self.trader = trader

        start: datetime = kwargs['start']
        end: datetime = kwargs['end']
        self.date_range = [work_day for work_day in WorkDayIterator(start, end)]

        self.__dict__.update(kwargs)

    def apply_day(self, date: datetime,index:int):
        self.buy_strategy_instance.trigger(date,index)
        self.sell_strategy_instance.trigger(date,index)
        # 每日记录收益
        self.holding.record_income(date,index)

    def run(self):
        for index,work_day in enumerate(self.date_range):
            # self.data.apply(lambda row: self.apply_row(row), axis=1)
            self.apply_day(work_day,index)

    def add_holding(self,price,date,code):
        """
        添加持仓
        :return:
        """
        holding = StockHolding(trader=self.trader)
        holding.buy(price,date,"开仓")
        self.holding[code] = holding