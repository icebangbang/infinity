from app.main.stock.dao import board_dao, k_line_dao, stock_dao
from app.main.stock.job import bt_runner
from datetime import datetime
import pandas as pd
import backtrader as bt
from app.main.stock.ind.kdj import KDJ
import backtrader.feeds as btfeeds  # 导入数据模块

from app.main.stock.service import board_service, stock_service, stock_index_service
from app.main.stock.sub_startegy.up_sma import UpSma
from app.main.stock.sub_startegy.trend.term import MediumLongTerm, MediumShortUpTerm
from app.main.stock.sub_startegy.trend.medium_short_up_trend import MediumShortUpTrend


def cal_rsv_predict(df,
                    fastk_period=9,
                    slowk_period=3,
                    slowd_period=3,
                    fillna=True,
                    rsv = None):
    if not isinstance(df, pd.DataFrame):
        raise Exception("传入的参数不是pandas的DataFrame类型!")
    # 检查传入的df是否存在high、low、close三列，不存在报错
    if rsv is None:
        if ('high' not in df.columns) or ('low' not in df.columns) or (
                'close' not in df.columns):
            # 抛出异常
            raise Exception("传入的参数不存在最高价、最低价、收盘价中的一个或几个!")
        # 计算指定日期间隔内的最低价的最小值
        low_list = df['low'].rolling(fastk_period, min_periods=fastk_period).min()
        # 将NAN填充成现有数据中的最小值
        if fillna is True:
            low_list.fillna(value=df['low'].expanding().min(), inplace=True)
        # 计算指定日期间隔的最高阶的最大值
        high_list = df['high'].rolling(9, min_periods=9).max()
        # 将NAN填充成现有数据中的最大值
        if fillna is True:
            high_list.fillna(value=df['high'].expanding().max(), inplace=True)
        # 计算RSV （国泰君安中的RSV公式RSV:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;）
        # RSV赋值:(收盘价-N日内最低价的最低值)/(N日内最高价的最高值-N日内最低价的最低值)*100
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100

    k = pd.DataFrame(rsv).ewm(
        com=slowk_period - 1,
        adjust=False).mean()  # rsv针对slowk_period参数求移动权重平均数

    d = k.ewm(com=slowd_period - 1, adjust=False).mean(
    )  # k针对slowd_period参数求移动权重平均数当,adjust为False时，以递归方式计算加权平均值

    j = 3 * k - 2 * d

    return k, d, j, rsv


from_date = datetime(2021, 4, 13)
to_date = datetime(2021, 9, 16)

# daily_price = pd.DataFrame(k_line_dao.get_k_line_data(from_date, to_date))
daily_price = pd.DataFrame(k_line_dao.get_k_line_by_code(["002430"], from_date, to_date))

codes = ["002430"]
for code in codes:
    daily_price = pd.DataFrame(k_line_dao.get_k_line_by_code([code], from_date, to_date))

    k, d, j, rsv = cal_rsv_predict(daily_price)
    count = 0
    while (k[0][len(k)-1] < d[0][len(k)-1]):
        count = count + 1
        value = rsv[len(rsv) - 1] + count * 0.1
        new_rsv = rsv.append(pd.Series([value]), ignore_index=True)
        k, d, j, ignore = cal_rsv_predict(daily_price,rsv = new_rsv)
    print(value)
