from typing import List

import backtrader as bt
import logging

from app.main.stock.company import CompanyGroup, Company
from app.main.stock.sub_startegy import SubST


class SimpleBsStrategy(bt.Strategy):
    params = (
        ('maperiod', 5),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, company_group: CompanyGroup, sub_st: List[SubST], **kwargs):
        self.company_group = company_group
        d = self.datas[0]
        code = d._name
        logging.info("init {}".format(code))
        sub_st_instance = [st(**kwargs) for st in sub_st]
        company = Company(code,
                          *sub_st_instance
                          )
        company_group.add_company(company)
        company.cash = self.broker.getcash()

        company: Company = company_group.get_company(code)
        company.init_ind(d)

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
        d = self.data
        if d.buflen() - len(d) == 0:
            self.sell()
            self.log('Close, %.2f' % d[0])
