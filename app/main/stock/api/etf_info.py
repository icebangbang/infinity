"""
同步etf数据
"""
import akshare as ak
import pandas as pd
from app.main.utils import date_util
import logging as log


def fetch_kline_data(code):
    """
    获取场内etf交易数据
    :param code:
    :return:
    """
    df = ak.fund_etf_hist_sina(code)
    df['money'] = df['volume'] * (df['high'] + df['low']) / 2
    df['prev_close'] = df.loc[df['close'].shift(-1) > 0, 'close']
    df['prev_close'] = df['prev_close'].shift()
    df.fillna(0, inplace=True)
    df['code'] = code
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df.to_dict("records")


def get_all_etf():
    """
    获取所有的场内etf基金列表,并逐个
    :return:
    """
    df = ak.fund_etf_category_sina("ETF基金")
    # 成交量
    # efts = df[df['成交额']>=10000000]
    efts = df[['代码', '名称', '成交额']]
    efts = efts.rename(columns={'代码': "code", "名称": "name", "成交额": "money"})

    etfs = efts.to_dict("records")

    etf_info_list = list()
    for etf in etfs:
        # 去除sz,sh标志
        code = etf['code'].replace("sz", "").replace("sh", "")
        name = etf['name']

        etf_basic_info = ak.fund_etf_basic_info_sina(code)
        log.info("获取{},{}的etf基金详情数据:{}".format(code,name,etf_basic_info))
        etf_info_list.append(etf_basic_info)

    return etf_info_list


if __name__ == "__main__":
    d = get_all_etf()
    pass
