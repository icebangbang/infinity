from datetime import datetime
from typing import List

from app.main.utils import cal_util

TRADE_TYPE_BUY = 1


class Trader:
    """
    交易者数据
    """

    def __init__(self, money: float, fee_rate: float, slippage: float):
        """

        :param money: 本金
        :param fee_rate: 交易手续费
        :param slippage: 交易滑点
        """
        self.money = money
        self.fee_rate = fee_rate
        self.slippage = slippage


class StockTradeRecord:
    """
    股票交易历史
    """

    def __init__(self, type, deal_num, deal_price, trade_time, motivation):
        """

        :param type: 成交类型,1买入,-1卖出
        :param deal_num: 成交数
        :param deal_price:  成交价格
        :param trade_time: 成交时间
        :param motivation: 成交动机
        """
        self.type = type
        self.deal_num = deal_num
        self.deal_price = deal_price
        self.trade_time = trade_time
        self.motivation = motivation


class StockHolding:
    """
    个股持仓情况
    """
    trader: Trader
    cost: float
    positions_num: int
    profit: float
    in_time: datetime
    price: float
    real_income: float  # 真实收入
    deal_num: int = 0
    money: float = 0

    # 股票成交历史
    trade_history: List[StockTradeRecord] = list()
    # 股票成交记录
    trade_record: List[StockTradeRecord] = list()
    income_record = list()

    def __init__(self, **kwargs):
        """
        :param cost: 成本
        :param positions_num: 持仓数
        :param profit: 盈利
        :param in_time: 盈利
        """
        self.__dict__.update(kwargs)

    def set_price(self, price):
        self.price = price

    def record_income(self, row, index):
        close = row['close']
        index = row.name
        float_income = cal_util.round(
            sum([record.deal_num * (close - record.deal_price) for record in self.trade_record])
            , 2)
        self.income_record.append(dict(float_income=float_income, index=index, date=row['date']))

    def buy(self, price: float, date: datetime, motivation):
        # 滑点
        slippage = self.trader.slippage
        money = self.trader.money
        # 滑点后的费用
        cost = cal_util.round(price * (1 + slippage), 2)
        # 计算可以买的手数
        deal_num = int(money / (cost * 100))

        self.cost = cost
        self.in_time = date
        self.money = money - deal_num * cost * 100
        self.deal_num = self.deal_num + deal_num * 100

        now = datetime.now()
        trade_time = datetime(date.year, date.month, date.day,
                              now.hour, now.minute, now.second)

        history = StockTradeRecord(TRADE_TYPE_BUY, self.deal_num, cost, trade_time, motivation)
        # 添加买入记录
        self.trade_history.append(history)
        self.trade_record.append(history)

    def sell(self):
        pass
