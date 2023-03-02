"""
同步etf数据
"""
import akshare as ak
import pandas as pd
from app.main.utils import date_util


def fetch_kline_data(code):
    """
    获取场内etf交易数据
    :param code:
    :return:
    """
    df = ak.fund_etf_hist_sina(code)
    df['money'] = df['volume'] *( df['high']+df['low'])/2
    df['prev_close'] = df.loc[df['close'].shift(-1) > 0, 'close']
    df['prev_close'] = df['prev_close'].shift()
    df.fillna(0,inplace=True)
    df['code'] = code
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df.to_dict("records")

def get_all_etf():
    """
    获取所有的体量比较大的额场内etf
    :return:
    """
    df = ak.fund_etf_category_sina("ETF基金")
    # 成交量
    # efts = df[df['成交额']>=10000000]
    efts = df[['代码','名称','成交额']]
    efts = efts.rename(columns={'代码':"code","名称":"name","成交额":"money"})

    etfs = efts.to_dict("records")

    for etf in etfs:
        code = etf['code'].replace("sz","").replace("sh","")
        r = ak.fund_etf_basic_info_sina(code)
        print(r)



if __name__ == "__main__":
    d = get_all_etf()
    pass