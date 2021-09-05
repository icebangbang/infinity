import backtrader as bt
import backtrader.feeds as btfeeds  # 导入数据模块
from datetime import datetime
import pandas as pd
import logging
from app.main.stock.stock_kline import fetch_kline_data
from app.main.stock.algo import boll
from app.main.stock.stagety.boll_startegy import BollBStartegy
from app.main.stock.stagety.sma_startegy import Sma5Startegy

from app.main.stock.dao import k_line_dao

from_date = datetime(2021, 8, 1)
to_date = datetime(2021, 9, 3)
cerebro = bt.Cerebro()

daily_price = pd.DataFrame(k_line_dao.get_k_line_data(from_date, to_date))
# daily_price = pd.DataFrame(k_line_dao.get_k_line_by_code(['600495'],from_date,to_date))
daily_price = daily_price.set_index("date", drop=False)

count = 1
for code in daily_price['code'].unique():
    # a = fetch_kline_data('300294', '20210301', '20210903', 'qfq')
    # boll.get_boll(a)
    # a = a.set_index("date",drop=False)
    df = daily_price.query(f"code=='{code}'")[['open', 'high', 'low', 'close', 'volume', 'date']]
    if len(df) <= 5:
        logging.info("{} may not have sma5".format(code))
        continue
    data = pd.DataFrame(index=daily_price.index.unique())
    data_ = pd.merge(data, df, left_index=True,right_index=True, how='left')

    #
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
cerebro.addstrategy(Sma5Startegy, house=house)
cerebro.run()

for k, v in house.items():
    if v['sma5_up_count'] >= 4:
        print(k)
    # [k for k, v in house.items() if v['sma5_up_count'] >= 2]

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# cerebro.plot()
