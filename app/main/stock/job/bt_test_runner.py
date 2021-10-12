import backtrader as bt
import backtrader.feeds as btfeeds  # 导入数据模块
from datetime import datetime
import pandas as pd
import logging

from app.main.stock.company import CompanyGroup
from app.main.stock.strategy.ind_test_strategy import IndTestStrategy
from app.main.stock.strategy.simple_bs_strategy import SimpleBsStrategy

from app.main.stock.dao import k_line_dao
from app.main.stock.strategy.test_startegy import TestStrategy

from_date = datetime(2021, 3, 13)
to_date = datetime(2021, 10, 4)

# daily_price = pd.DataFrame(k_line_dao.get_k_line_data(from_date, to_date))
daily_price = pd.DataFrame(k_line_dao.get_k_line_by_code(['300763'], from_date, to_date))
daily_price = daily_price.set_index("date", drop=False)

count = 1
company_group = CompanyGroup()

for code in daily_price['code'].unique():
    cerebro = bt.Cerebro(cheat_on_open=True)
    df = daily_price.query(f"code=='{code}'")[['open', 'high', 'low', 'close', 'volume']]
    data = pd.DataFrame(index=daily_price.index.unique())
    data_ = pd.merge(data, df, left_index=True, right_index=True, how='left')
    data_.loc[:, ['volume']] = data_.loc[:, ['volume']].fillna(0)
    data_.loc[:, ['open', 'high', 'low', 'close']] = data_.loc[:, ['open', 'high', 'low', 'close']].fillna(method='pad')
    data_feed = btfeeds.PandasData(dataname=data_, fromdate=from_date, todate=to_date)
    logging.info("feed {} to cerebro,index {}".format(code, count))
    count = count + 1
    cerebro.adddata(data_feed, name=code)  # 通过 name 实现数据集与股票的一一对应

    # 实例化 cerebro
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    print(code)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # cerebro.addstrategy(SimpleBsStrategy,company_group=company_group,sub_st=[])
    cerebro.addstrategy(TestStrategy,company_group=company_group,sub_st=[])
    cerebro.run()

    company = company_group.get_company(code)
    company.value = cerebro.broker.getvalue()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

total = 0
cash =0
for company in company_group.get_companies():
    total = total+company.cash
    c = company.value-company.cash
    cash = cash+c

print(cash)
print(total)