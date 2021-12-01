from typing import List

import backtrader as bt
import logging

from app.main.stock.company import CompanyGroup, Company
from app.main.stock.dao import stock_dao
from app.main.stock.job import bt_runner
from datetime import datetime

from app.main.stock.strategy.strategy_wrapper import StrategyWrapper
from app.main.stock.sub_startegy import SubST


class SimpleBsStrategy(bt.Strategy):
    params = (
        ('maperiod', 5),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self,from_date,to_date, code: str,name,sub_st, **kwargs):
        self.code = code
        self.sub_st = sub_st
        self.from_date = from_date
        self.to_date = to_date
        self.name = name

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next_open(self):
        d = self.data
        code = d._name
        company: Company = self.company_group.get_company(code)

        if not self.position:
            company.order = self.buy(size=int(self.broker.getcash() * 0.99 / d.open[0]))
            self.log('open, %.2f' % d.open[0])

        # Simply log the closing price of the series from the reference

    def next(self):
        d = self.datas[0]
        t = d.datetime.date(0)
        code = self.code
        from_date = self.from_date
        data = self.data
        sub_st = self.sub_st
        name = self.name

        # 先去数据库寻找有无现成的特征
        company: Company = stock_dao.get_company_feature(code, datetime.fromordinal(t.toordinal()))
        if company is None:
            # 重跑特征
            company = bt_runner.run(from_date, t,main_st=StrategyWrapper, data = data,code=code,name=name, sub_st=sub_st)
        features= company.features

        # 根据特征执行买卖

