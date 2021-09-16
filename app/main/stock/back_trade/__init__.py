"""
回测模块
"""
import backtrader.feeds as btfeeds  # 导入数据模块
from app.main.stock.company import CompanyGroup
from app.main.stock.dao import k_line_dao
from app.main.stock.job import bt_runner
import logging
import  backtrader as bt
import pandas as pd

from datetime import datetime

from_date = datetime(2021, 6, 1)
to_date = datetime(2021, 9, 14)



count = 1
company_group = CompanyGroup()

def sell(codes):
    daily_price = pd.DataFrame(k_line_dao.get_k_line_by_code(codes, from_date, to_date))
    daily_price = daily_price.set_index("date", drop=False)

    cerebro = bt.Cerebro()

    for code in daily_price["code"].unique():
        # if count >=500 : continue
        df = daily_price.query("{}=='{}'".format(code, code))[['open', 'high', 'low', 'close', 'volume']]
        data = pd.DataFrame(index=daily_price.index.unique())
        data_ = pd.merge(data, df, left_index=True, right_index=True, how='left')

        data_.loc[:, ['volume']] = data_.loc[:, ['volume']].fillna(0)
        data_.loc[:, ['open', 'high', 'low', 'close']] = data_.loc[:, ['open', 'high', 'low', 'close']].fillna(
            method='pad')
        data_feed = btfeeds.PandasData(dataname=data_, fromdate=from_date, todate=to_date)
        logging.info("feed {} to cerebro,index {}".format(code, count))
        count = count + 1
        cerebro.adddata(data_feed, name=code)  # 通过 name 实现数据集与股票的一一对应

    # 实例化 cerebro
    cerebro.broker.setcash(100000.0)  # 设置现金
    cerebro.broker.setcommission(commission=0.0005)  # 设置手续费及
    print('开始拥有的金额为: %.2f' % cerebro.broker.getvalue())

    cerebro.addstrategy(StrategyWrapper, company_group=company_group, sub_st=sub_st, **kwargs)
    cerebro.run()
    # [k for k, v in house.items() if v['sma5_up_count'] >= 2]
    return company_group

# print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# cerebro.plot()
