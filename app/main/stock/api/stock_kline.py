"""
k线数据获取
"""
import akshare as ak
import pandas as pd
from app.main.stock.algo import boll
from datetime import datetime
import logging
# stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="603777", start_date="20210301", end_date='20210616')
# print(stock_zh_a_hist_df)
id_map = ak.code_id_map()


def fetch_kline_data(code, start_date, end_date, adjust, klt='101'):
    data = ak.stock_zh_a_hist(symbol=code, start_date=start_date, end_date=end_date, adjust=adjust, klt=klt,
                              code_id_dict=id_map)
    # logging.info("字典大小为 {}".format(str(id_map.keys())))
    if data is None: return None
    data = pd.DataFrame(data[['日期', '开盘', '收盘', '最高', '最低', '成交量','成交额',"最近收盘"]])
    data.columns = ['date', 'open', 'close', 'high', 'low', 'volume','money','prev_close']
    data['klt'] = klt
    data['code'] = str(code)
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
    data['create_time'] = datetime.now()
    return data


if __name__ == '__main__':
    # a = fetch_kline_data('601866', '20230512', '20230512', 'qfq',klt="103")
    a = fetch_kline_data('601866', '20230512', '20230512', 'qfq')
    # boll.get_boll(a)
    print(a)
