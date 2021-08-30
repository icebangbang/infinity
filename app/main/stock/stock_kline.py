"""
k线数据获取
"""
import akshare as ak
import pandas as pd
from app.main.stock.algo import boll
from datetime import datetime

# stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="603777", start_date="20210301", end_date='20210616')
# print(stock_zh_a_hist_df)


def fetch_kline_data(code, start_date, end_date, adjust, klt='101'):
    data = ak.stock_zh_a_hist(symbol=code, start_date=start_date, end_date=end_date, adjust=adjust, klt=klt)
    data = pd.DataFrame(data[['日期', '开盘', '收盘', '最高', '最低', '成交量']])
    data.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
    data['klt'] ="101"
    data['code'] = str(code)
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
    data['create_time'] = datetime.now()
    return data


if __name__ == '__main__':
    a = fetch_kline_data('300763', '20210701', '20210822', 'qfq')
    boll.get_boll(a)
