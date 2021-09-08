import backtrader as bt
import backtrader.feeds as btfeeds  # 导入数据模块
from datetime import datetime
import pandas as pd
import logging
from app.main.stock.startegy.ind_test_strategy import IndTestStrategy

from app.main.stock.dao import k_line_dao

from_date = datetime(2021, 6, 1)
to_date = datetime(2021, 9, 6)
cerebro = bt.Cerebro()

# daily_price = pd.DataFrame(k_line_dao.get_k_line_data(from_date, to_date))
daily_price = pd.DataFrame(k_line_dao.get_k_line_by_code(['300809'], from_date, to_date))
daily_price = daily_price.set_index("date", drop=False)

count = 1

for code in daily_price['code'].unique():
    if count >= 1000: continue
    df = daily_price.query(f"code=='{code}'")[['open', 'high', 'low', 'close', 'volume']]
    if len(df) <= 5:
        logging.info("{} may not have sma5".format(code))
        continue
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
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

house = dict()
cerebro.addstrategy(IndTestStrategy)
cerebro.run()

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# cerebro.plot()
