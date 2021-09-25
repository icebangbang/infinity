from app.main.stock.company import CompanyGroup, Company
from app.main.stock.dao import board_dao, k_line_dao, stock_dao
from app.main.stock.job import bt_runner
from datetime import datetime
import pandas as pd
import backtrader as bt
import backtrader.feeds as btfeeds  # 导入数据模块
import logging

from app.main.stock.service import board_service, stock_service, stock_index_service
from app.main.stock.strategy.kdj_macd_strategy import KdjMacdStrategy
from app.main.stock.sub_startegy.up_sma import UpSma
from app.main.stock.sub_startegy.trend.term import MediumLongTerm, MediumShortUpTerm
from app.main.stock.sub_startegy.trend.medium_short_up_trend import MediumShortUpTrend

stocks = stock_dao.get_all_stock()

vcstore = bt.stores.VCStore()
data = vcstore.getdata(dataname='015ES', timeframe=bt.TimeFrame.Minutes, compression=2)



def get_stock_status():
    """
    中长期(Medium&LongTerm)指数强弱判断
    """
    from_date = datetime(2006, 10, 1)
    to_date = datetime(2008, 1, 1)
    # data = pd.DataFrame(k_line_dao.get_k_line_by_code(["300005"], from_date, to_date))
    # data = pd.DataFrame(k_line_dao.get_k_line_data(from_date, to_date))
    # daily_price = data.set_index("date", drop=False)

    sub_st = [MediumShortUpTrend, ]
    kwargs = {"ma_period": 17,
              "ma_match_num": 17,
              "up_mid_bolling_period": 1,
              "timeline_limit": 30}

    count = 1
    company_group = CompanyGroup()
    key = "code"

    # for code in daily_price[key].unique():
    for code in ["600997"]:
        # code = stock['code']
        print(code)
        data = pd.DataFrame(k_line_dao.get_k_line_by_code([code], from_date, to_date))
        daily_price = data.set_index("date", drop=False)

        cerebro = bt.Cerebro()
        df = daily_price.query("{}=='{}'".format(key, code))[['open', 'high', 'low', 'close', 'volume']]

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

        company = Company(code)
        company_group.add_company(company)
        cerebro.addstrategy(KdjMacdStrategy, company=company)
        cerebro.run()

    ml_term_up = []

    for company in company_group.get_companies():

        c1 = company.get("close_gte_ma20")
        c2 = company.get("ma20[0]_gte_ma20[-1]")
        c3 = company.get("macd_incr")
        c4 = company.get("kdj_golden")

        if c1 and c2 and c3 and c4:
            ml_term_up.append(company)

    codes = [str(company) for company in ml_term_up]
    print([str(company) for company in ml_term_up])

    return codes


if __name__ == "__main__":
    codes = get_stock_status()
    # stock_details = stock_dao.get_stock_detail_list(codes)
    # stock_map = {}
    # boards = []
    # for stock in stock_details:
    #     stock['code'] = stock
    #     boards.extend(stock['board'])
    #
    # pd.DataFrame(boards).groupby(0).apply(lambda x: x.sort_values(0, ascending=False))

    # pd.DataFrame(boards)[0].value_counts(normalize=False, sort=True).to_frame('count').reset_index()
    # if len(codes) != 0:
    #     stock_service.publish(10, 30, codes, stock_map)
