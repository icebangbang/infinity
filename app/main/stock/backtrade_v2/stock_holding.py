from datetime import datetime
from typing import List

from app.main.stock.backtrade_v2.record import StockTradeRecord,StockRefreshRecord
from app.main.stock.backtrade_v2.trade_monitor import TradeMonitor
from app.main.utils import cal_util, object_util
from app.main.stock.backtrade_v2.stock_selector import StockSelector,RecommendStock
from app.main.stock.dao import k_line_dao
import logging as log

TRADE_TYPE_BUY = 1


class StockHolding:
    """
    个股持仓情况
    """
    # 个股代码
    code: str
    # 个股名称
    name: str
    # 成本
    cost: float
    # 持仓数
    positions_num: int
    # 浮盈
    profit: float
    # 加入时间
    in_time: datetime
    # 当前价格
    price: float
    # 真实收入
    real_income: float =0
    # 手数
    deal_num: int = 0

    trade_monitor = TradeMonitor()
    # 股票成交历史
    trade_history: List[StockTradeRecord] = list()
    # 股票成交记录
    trade_record: List[StockTradeRecord] = list()
    refresh_record: List[StockRefreshRecord] = list()

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

    def refresh_holding(self,row,date):
        # 数据为空可能是因为停牌等原因
        latest = None
        if row is None:
            record = self.refresh_record[len(self.refresh_record) - 1]
            copy:StockRefreshRecord = object_util.copy_obj(record)
            copy.date= date
            latest = copy
            self.refresh_record.append(copy)
        else:
            close = row['close']
            self.profit = cal_util.round(close - self.cost) * self.deal_num
            self.price = close
            record = StockRefreshRecord(self.cost,close,self.deal_num,date)
            self.refresh_record.append(record)
            latest=record
            log.info("{},{},{}".format(self.price,self.profit,date))

        # 计算最大回撤
        self.trade_monitor.cal_maximum_rollback(self.code,self.refresh_record,self.in_time,date)
        self.trade_monitor.cal_annualized_return(self.code,latest,self.in_time,date)



    def buy(self, price: float, date: datetime, motivation,trader):
        # 滑点
        slippage = trader.slippage
        money = trader.money
        # 滑点后的费用
        cost = cal_util.round(price * (1 + slippage), 2)
        # 计算可以买的手数
        deal_num = int(money / (cost * 100))

        self.cost = cost
        self.in_time = date
        self.deal_num = self.deal_num + deal_num * 100

        trader.money = money - deal_num * cost * 100
        # 计算浮盈
        self.profit = (price-cost) * deal_num * 100
        self.price = price


        now = datetime.now()
        trade_time = datetime(date.year, date.month, date.day,
                              now.hour, now.minute, now.second)

        history = StockTradeRecord(TRADE_TYPE_BUY, self.deal_num, cost, trade_time, motivation)
        # 添加买入记录
        self.trade_history.append(history)
        self.trade_record.append(history)

    def sell(self):
        """
        清空仓位
        :return:
        """
        pass

class HoldingPool:
    stock_holding_list: List[StockHolding] = list()
    # 完成交易的仓位
    finished_holding:List[StockHolding] = list()

    def size(self):
        return len(self.stock_holding_list)

    def add_holding(self,recommend_stock:RecommendStock,trader):
        """
        添加持仓
        :return:
        """
        code = recommend_stock.code
        name = recommend_stock.name
        price = recommend_stock.price
        date = recommend_stock.date
        motivation = recommend_stock.motivation

        holding = StockHolding(code=code,name=name,trader=trader)
        holding.buy(price, date, motivation,trader)
        self.stock_holding_list.append(holding)

    def refresh_holding(self,date):
        """
        更新持仓信息
        :return:
        """
        for stock_holding in self.stock_holding_list:
            code = stock_holding.code
            point = k_line_dao.get_k_line_data_point(code,date)
            stock_holding.refresh_holding(row = point,date = date)

    def remove_holding(self):
        """
        移除仓位
        :return:
        """
        pass

class Trader:
    """
    交易者数据
    """
    holding_pool:HoldingPool = HoldingPool()
    stock_selector:StockSelector = StockSelector()
    money:float
    initial_money:float


    def __init__(self, money: float, fee_rate: float, slippage: float):
        """

        :param money: 本金
        :param fee_rate: 交易手续费
        :param slippage: 交易滑点
        """
        self.initial_money = money
        self.money = money
        self.fee_rate = fee_rate
        self.slippage = slippage

    def buy_supported(self):
        """
        是否支持继续购买
        如果没钱了，买个屁
        :return:
        """
        return self.holding_pool.size() <1

    def trigger(self,date:datetime):
        """
        开始交易
        :return:
        """
        # 判断是否可以支持买入股票，资金维度判断，市场维度判断
        if self.buy_supported():
            # 获取推荐的个股
            recommend_stock_list:List[RecommendStock] = self.stock_selector.select(date)
            for recommend_stock in recommend_stock_list:
                 self.holding_pool.add_holding(recommend_stock,self)

        self.holding_pool.refresh_holding(date)








