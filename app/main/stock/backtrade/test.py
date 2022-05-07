import backtrader as bt
import datetime
import pandas as pd
import numpy as np
import os, sys
import copy
import math
import warnings

from app.main.stock.backtrade.data_carrier import PandasDataMore
from app.main.stock.dao import k_line_dao, stock_dao

warnings.filterwarnings("ignore")


# 我们使用的时候，直接用我们新的类读取数据就可以了。
class test_two_ma_strategy(bt.Strategy):
    # params = (('short_period', 5),
    #           ("long_period", 60),
    #           )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('{}, {}'.format(dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.bar_num = 0
        # 保存均线数据
        # self.stock_short_ma_dict={data._name:bt.talib.SMA(data.close,timeperiod=self.p.short_period) for data in self.datas}
        # self.stock_short_ma_dict={data._name:bt.talib.SMA(data.close,timeperiod=self.p.long_period) for data in self.datas}
        self.ma5 = bt.indicators.SimpleMovingAverage(self.data.close, period=5)
        # 保存现有持仓的股票
        self.position_dict = {}
        # 当前有交易的股票
        self.stock_dict = {}

    def prenext(self):

        self.next()

    def next(self):
        # 50w资金
        pre_date = self.data.datetime.date(-1).strftime("%Y-%m-%d")
        current_date = self.data.datetime.date(0).strftime("%Y-%m-%d")

        pre_close = self.data.close[-1]
        current_close = self.data.close[0]

        pre_ma5 = self.ma5[-1]
        current_ma5 = self.ma5[0]

        if pre_close < pre_ma5 and current_close >=current_ma5:
            self.buy(size=100)
        if pre_close > pre_ma5 and current_close <= current_ma5:
            self.close()



    def notify_order(self, order):

        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status == order.Rejected:
            self.log(f"Rejected : order_ref:{order.ref}  data_name:{order.p.data._name}")

        if order.status == order.Margin:
            self.log(f"Margin : order_ref:{order.ref}  data_name:{order.p.data._name}")

        if order.status == order.Cancelled:
            self.log(f"Concelled : order_ref:{order.ref}  data_name:{order.p.data._name}")

        if order.status == order.Partial:
            self.log(f"Partial : order_ref:{order.ref}  data_name:{order.p.data._name}")

        if order.status == order.Completed:
            if order.isbuy():
                self.log(
                    f" BUY : data_name:{order.p.data._name} price : {order.executed.price} , cost : {order.executed.value} , commission : {order.executed.comm}")
                print('当前可用资金', self.broker.getcash())

                print('当前总资产', self.broker.getvalue())

                print('当前持仓量', self.broker.getposition(self.data).size)

                print('当前持仓成本', self.broker.getposition(self.data).price)

                # 也可以直接获取持仓

                print('当前持仓量', self.getposition(self.data).size)

                print('当前持仓成本', self.getposition(self.data).price)

            else:  # Sell
                self.log(
                    f" SELL : data_name:{order.p.data._name} price : {order.executed.price} , cost : {order.executed.value} , commission : {order.executed.comm}")

    def notify_trade(self, trade):
        # 一个trade结束的时候输出信息
        if trade.isclosed:
            self.log('closed symbol is : {} , total_profit : {} , net_profit : {}'.format(
                trade.getdataname(), trade.pnl, trade.pnlcomm))
            # self.trade_list.append([self.datas[0].datetime.date(0),trade.getdataname(),trade.pnl,trade.pnlcomm])

        if trade.isopen:
            self.log('open symbol is : {} , price : {} '.format(
                trade.getdataname(), trade.price))

    def stop(self):

        pass

    # 初始化cerebro,获得一个实例


cerebro = bt.Cerebro()
# cerebro.broker = bt.brokers.BackBroker(shortcash=True)  # 0.5%
# params = dict(
#
#     fromdate=datetime.datetime(2005, 1, 4),
#     todate=datetime.datetime(2020, 7, 31),
#     timeframe=bt.TimeFrame.Days,
#     dtformat=("%Y-%m-%d"),
#     compression=1,
#     datetime=0,
#     open=1,
#     high=2,
#     low=3,
#     close=4,
#     volume=5,
#     openinterest=-1)

data_list = k_line_dao.get_k_line_data(datetime.datetime(2005, 1, 4),
                                       datetime.datetime(2020, 7, 31), codes=['300763'])
code_name_map = stock_dao.get_code_name_map()
data_df = pd.DataFrame(data_list)

for code, group in data_df.groupby("code"):
    name = code_name_map[code]

    original = pd.DataFrame(group)
    df = original[['date', 'open', 'high', 'low', 'close', 'volume', 'prev_close']]
    df = df.set_index("date", drop=True)
    data_feed = PandasDataMore(dataname=df, timeframe=bt.TimeFrame.Days,dtformat=("%Y-%m-%d"))
# 添加数据到cerebro
    cerebro.adddata(data_feed, name=name)

print("加载数据完毕")
# 添加手续费，按照万分之二收取
cerebro.broker.setcommission(commission=0.0002, stocklike=True)
# 设置初始资金为50w
cerebro.broker.setcash(50000)
# 添加策略
cerebro.addstrategy(test_two_ma_strategy)
# cerebro.addanalyzer(bt.analyzers.TotalValue, _name='_TotalValue')
cerebro.addanalyzer(bt.analyzers.PyFolio,_name='PyFolio')
# 运行回测
results = cerebro.run()
# 打印相关信息
portfolio_stats = results[0].analyzers.getbyname('PyFolio')
returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
returns.index = returns.index.tz_convert(None)

import quantstats
# quantstats.reports.html(returns, output='stats.html', title='锦浪科技')
quantstats.reports.plots(returns)


