import backtrader as bt
import backtrader.feeds as btfeeds  # 导入数据模块
from datetime import datetime
import pandas as pd
import logging
from app.main.stock.strategy.strategy_wrapper import StrategyWrapper
from app.main.stock.sub_startegy.up_sma import UpSma
from app.main.stock.company import Company, CompanyGroup

from app.main.stock.dao import k_line_dao


def run(from_date, to_date, data, key, sub_st, code, name, **kwargs):
    cerebro = bt.Cerebro()

    count = 1
    sub_st_instance = [st(**kwargs) for st in sub_st]
    company = Company(code,
                      name,
                      *sub_st_instance
                      )

    timeline_limit = kwargs.get("timeline_limit", 10)
    resample = kwargs.get("resample", True)

    # if count >=500 : continue
    original = pd.DataFrame(data)
    df = original[['date','open', 'high', 'low', 'close', 'volume']]
    df = df.set_index("date", drop=False)

    if len(df) <= timeline_limit:
        logging.info("{} may not have sma5".format(kwargs.get("timeline_limit", 10), code))
        return
    # data = pd.DataFrame(index=daily_price.index.unique())
    # data_ = pd.merge(data, df, left_index=True, right_index=True, how='left')
    #
    # data_.loc[:, ['volume']] = data_.loc[:, ['volume']].fillna(0)
    # data_.loc[:, ['open', 'high', 'low', 'close']] = data_.loc[:, ['open', 'high', 'low', 'close']].fillna(
    #     method='pad')
    data_feed = btfeeds.PandasData(dataname=df, timeframe=bt.TimeFrame.Days)
    logging.info("feed {} to cerebro,index {}".format(code, count))
    count = count + 1
    cerebro.adddata(data_feed, name=code)  # 通过 name 实现数据集与股票的一一对应

    # 日k整合为周k
    if resample is False:
        cerebro.resampledata(data_feed, name="week", timeframe=bt.TimeFrame.Weeks, compression=1)


    # 实例化 cerebro
    cerebro.broker.setcash(100000.0)  # 设置现金
    cerebro.broker.setcommission(commission=0.0005)  # 设置手续费及
    print('开始拥有的金额为: %.2f' % cerebro.broker.getvalue())

    cerebro.addstrategy(StrategyWrapper, company=company, sub_st=sub_st, **kwargs)
    cerebro.run()
    # cerebro.plot(style='bar')
    # [k for k, v in house.items() if v['sma5_up_count'] >= 2]
    return company

# print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# cerebro.plot()


if __name__ == "__main__":
    from_date = datetime(2021, 8, 1)
    to_date = datetime(2021, 9, 8)
    # codes = ["600725"]
    codes = []

    run(from_date, to_date, codes)
