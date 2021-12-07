import backtrader as bt
import backtrader.feeds as btfeeds  # 导入数据模块
from datetime import datetime
import pandas as pd
import logging
from app.main.stock.strategy.simple_bs_strategy import SimpleBsStrategy
from app.main.stock.sub_startegy.up_sma import UpSma
from app.main.stock.company import Company, CompanyGroup

from app.main.stock.dao import k_line_dao

"""
买卖策略
"""


def run(from_date, to_date, data, main_st,sub_st, code, name, **kwargs):
    """

    :param from_date: 开始时间
    :param to_date: 结束时间
    :param data: k线数据
    :param main_st: 主题策略,控制买卖,或者是筛选
    :param sub_st: 子策略,用于计算具体指标
    :param code: 股票代码
    :param name: 股票名称
    :param kwargs: 其他参数
    :return:
    """
    cerebro = bt.Cerebro()

    count = 1
    sub_st_instance = [st(**kwargs) for st in sub_st]
    company = Company(code,
                      name,
                      *sub_st_instance
                      )

    timeline_limit = kwargs.get("timeline_limit", 10)

    if isinstance(data, btfeeds.PandasData):
        data_feed = data
    else:
        original = pd.DataFrame(data)
        df = original[['date', 'open', 'high', 'low', 'close', 'volume']]
        df = df.set_index("date", drop=True)

        if len(df) <= timeline_limit:
            logging.info("{} may not have sma5".format(kwargs.get("timeline_limit", 10), code))
            return None

        data_feed = btfeeds.PandasData(dataname=df, timeframe=bt.TimeFrame.Days)
    cerebro.adddata(data_feed, name=code)  # 通过 name 实现数据集与股票的一一对应

    # 日k整合为周k
    # if resample is False:
    #     cerebro.resampledata(data_feed, name="week", timeframe=bt.TimeFrame.Weeks, compression=1)

    # 实例化 cerebro
    # print('开始拥有的金额为: %.2f' % cerebro.broker.getvalue())

    cerebro.addstrategy(main_st,from_date=from_date,to_date=to_date, company=company,code=code,name=name, sub_st=sub_st, **kwargs)
    cerebro.run()
    # cerebro.plot(style='bar')
    # [k for k, v in house.items() if v['sma5_up_count'] >= 2]
    return company
