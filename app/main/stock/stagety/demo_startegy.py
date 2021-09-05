import backtrader as bt
import logging


class DemoStrategy(bt.Strategy):
    type=None
    params = (
        ('maperiod', 5),
        ('p_period_volume', 10),
        ('p_sell_ma', 5),
        ('pstake', 100),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        logging.info('%s, %s' % (dt.isoformat(), txt))

    def __init__(self,type):
        self.inds = dict()
        self.type = type

        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            boll_mid = bt.indicators.BollingerBands().mid
            self.inds[d]['buy_con'] = bt.And(
                d.open < boll_mid, d.close > boll_mid,
                # 放量
                d.volume == bt.ind.Highest(d.volume, period=self.p.p_period_volume, plot=False))

            # 卖出条件
            self.inds[d]['sell_con'] = d.close < bt.ind.SMA(d.close, period=self.params.p_sell_ma)

    def next(self):
        for i, d in enumerate(self.datas):
            pos = self.getposition(d).size
            if not pos:  # 不在场内，则可以买入
                if self.inds[d]['buy_con']:  # 如果金叉
                   resp = self.buy(data=d, size=self.params.pstake)
                   pass# 买买买
            elif self.inds[d]['sell_con']:  # 在场内，且死叉
                self.close(data=d)  # 卖卖卖

    def notify_trade22(self, trade):
        dt = self.data.datetime.date()
        if trade.isclosed:
            self.log('{} {} Closed: PnL Gross {}, Net {}'.format(
                dt, trade.data._name, round(trade.pnl, 2), round(trade.pnlcomm, 2)))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '%s BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.data._name,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                pass
                # self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                #          (order.executed.price,
                #           order.executed.value,
                #           order.executed.comm))

            self.bar_executed = len(self)
