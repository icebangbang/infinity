import backtrader as bt
import backtrader.feeds as btfeeds  # 导入数据模块
from datetime import datetime, timedelta
import pandas as pd
import logging
from app.main.stock.strategy.simple_bs_strategy import SimpleBsStrategy
from app.main.stock.company import Company, CompanyGroup

from app.main.stock.dao import k_line_dao, stock_dao
from app.main.stock.job import bt_runner


def run(from_date, to_date, data, sub_st, code, name, **kwargs):
    """

    :param from_date:
    :param trader_start_time:
    :param to_date:
    :param data:
    :param key:
    :param sub_st:
    :param code:
    :param name:
    :param kwargs:
    :return:
    """
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)  # 设置现金10万
    cerebro.broker.setcommission(commission=0.0005)  # 设置手续费及

    # 实例化 cerebro
    print('开始拥有的金额为: %.2f' % cerebro.broker.getvalue())

    df = data[['date', 'open', 'high', 'low', 'close', 'volume']]
    df = df.set_index("date", drop=True)

    data_feed = btfeeds.PandasData(dataname=df, timeframe=bt.TimeFrame.Days)
    cerebro.adddata(data_feed, name=code)  # 通过 name 实现数据集与股票的一一对应

    cerebro.addstrategy(SimpleBsStrategy,
                        from_date=from_date, to_date=to_date,
                        code=code, data=data, sub_st=sub_st,
                        **kwargs)
    cerebro.run()
