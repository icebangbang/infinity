from app.main.stock.api.overwrite import stock_zh_a_hist
import pandas as pd
from datetime import datetime


def fetch_index_day_level(symbol, start_date, end_date, klt="101",id_map=None):
    """
    同步a股指数
    :return:
    """
    data = stock_zh_a_hist(symbol=symbol,
                           start_date=start_date,
                           end_date=end_date,
                           adjust="",
                           klt=klt,
                           code_id_dict=id_map)

    data = pd.DataFrame(data[['日期', '开盘', '收盘', '最高', '最低', '成交量','最近收盘']])
    data.columns = ['date', 'open', 'close', 'high', 'low', 'volume','prev_close']
    data['klt'] = klt
    data['code'] = symbol
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
    data['create_time'] = datetime.now()
    return data
